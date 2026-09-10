import functools
import re
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db_connection

auth = Blueprint('auth', __name__)

def login_required(view):
    """Decorator to require authenticated user session."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Please log in to access your task dashboard.', 'info')
            return redirect(url_for('auth.login', next=request.path))
        return view(**kwargs)
    return wrapped_view

@auth.before_app_request
def load_logged_in_user():
    """Load user record into Flask g context before each request."""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        conn = get_db_connection()
        g.user = conn.execute(
            'SELECT id, username, email, created_at FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        conn.close()

@auth.route('/register', methods=('GET', 'POST'))
def register():
    if g.user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        error = None

        if not username or len(username) < 3:
            error = 'Username must be at least 3 characters long.'
        elif not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            error = 'Username can only contain letters, numbers, dots, and underscores.'
        elif not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            error = 'Please provide a valid email address.'
        elif not password or len(password) < 6:
            error = 'Password must be at least 6 characters long.'
        elif password != confirm_password:
            error = 'Passwords do not match.'

        if error is None:
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                    (username, email, generate_password_hash(password))
                )
                user_id = cursor.lastrowid
                conn.commit()

                session.clear()
                session['user_id'] = user_id
                session['username'] = username
                session['email'] = email

                flash(f'Welcome aboard, {username}! Add your first study task to get started.', 'success')
                return redirect(url_for('dashboard'))
            except conn.IntegrityError as e:
                err_str = str(e).lower()
                if 'users.username' in err_str or 'username' in err_str:
                    error = f'Username "{username}" is already taken.'
                elif 'users.email' in err_str or 'email' in err_str:
                    error = f'Email address "{email}" is already registered.'
                else:
                    error = 'An account with these details already exists.'
            finally:
                conn.close()

        flash(error, 'danger')

    return render_template('register.html')

@auth.route('/login', methods=('GET', 'POST'))
def login():
    if g.user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        error = None
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? OR email = ?',
            (identifier, identifier.lower())
        ).fetchone()
        conn.close()

        if user is None:
            error = 'No account found with that username or email.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect password. Please try again.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']

            flash(f'Welcome back, {user["username"]}!', 'success')
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('dashboard'))

        flash(error, 'danger')

    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
