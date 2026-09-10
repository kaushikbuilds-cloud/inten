import os
from datetime import datetime, date
from flask import (
    Flask, render_template, request, jsonify, redirect, url_for, g, flash, session
)
from auth import auth, login_required
from database import get_db_connection, init_db

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'student-task-manager-dev-key-998877'),
    )

    # Register blueprints
    app.register_blueprint(auth)

    # Ensure database is initialized
    with app.app_context():
        init_db()

    def calculate_task_metadata(task_dict):
        """Augment a task dict with computed fields like overdue status and badge data."""
        due_str = task_dict.get('due_date')
        is_overdue = False
        due_human = "No due date"
        badge_variant = "secondary"

        if due_str:
            try:
                # Support YYYY-MM-DD format
                due_date_obj = datetime.strptime(due_str.split('T')[0], "%Y-%m-%d").date()
                today = date.today()
                diff = (due_date_obj - today).days

                if task_dict.get('status') == 'Pending' and diff < 0:
                    is_overdue = True
                    badge_variant = "danger"
                    due_human = f"{abs(diff)} day{'s' if abs(diff) != 1 else ''} overdue"
                elif diff == 0:
                    badge_variant = "warning"
                    due_human = "Due today"
                elif diff == 1:
                    badge_variant = "info"
                    due_human = "Due tomorrow"
                elif diff > 1:
                    badge_variant = "neutral"
                    due_human = f"In {diff} days"
                else:
                    badge_variant = "neutral"
                    due_human = f"{abs(diff)} days ago"
            except ValueError:
                due_human = due_str

        task_dict['is_overdue'] = is_overdue
        task_dict['due_human'] = due_human
        task_dict['due_badge_variant'] = badge_variant
        return task_dict

    @app.route('/demo-login')
    def demo_login():
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = 'alex_student' LIMIT 1").fetchone()
        if not user:
            user = conn.execute("SELECT * FROM users LIMIT 1").fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            modal_param = request.args.get('modal', '')
            if modal_param:
                return redirect(url_for('dashboard', modal=modal_param))
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))

    @app.route('/')
    @login_required
    def dashboard():
        return render_template('dashboard.html')

    # API Endpoints
    @app.route('/api/stats', methods=['GET'])
    @login_required
    def get_stats():
        user_id = g.user['id']
        conn = get_db_connection()
        
        # Aggregate counts
        stats_row = conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'Pending' AND date(due_date) < date('now', 'localtime') THEN 1 ELSE 0 END) as overdue
            FROM tasks
            WHERE user_id = ?
        """, (user_id,)).fetchone()

        total = stats_row['total'] or 0
        completed = stats_row['completed'] or 0
        pending = stats_row['pending'] or 0
        overdue = stats_row['overdue'] or 0
        completion_rate = round((completed / total * 100)) if total > 0 else 0

        # Unique subjects for filtering
        subjects = [
            row['subject'] for row in conn.execute(
                "SELECT DISTINCT subject FROM tasks WHERE user_id = ? AND subject IS NOT NULL AND subject != '' ORDER BY subject ASC",
                (user_id,)
            ).fetchall()
        ]

        conn.close()
        return jsonify({
            'total': total,
            'completed': completed,
            'pending': pending,
            'overdue': overdue,
            'completion_rate': completion_rate,
            'subjects': subjects
        })

    @app.route('/api/tasks', methods=['GET'])
    @login_required
    def list_tasks():
        user_id = g.user['id']
        status_filter = request.args.get('status', 'all')
        subject_filter = request.args.get('subject', 'all')
        priority_filter = request.args.get('priority', 'all')
        search_query = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'due_date_asc')

        query = "SELECT * FROM tasks WHERE user_id = ?"
        params = [user_id]

        # Status filter
        if status_filter == 'Pending':
            query += " AND status = 'Pending'"
        elif status_filter == 'Completed':
            query += " AND status = 'Completed'"
        elif status_filter == 'Overdue':
            query += " AND status = 'Pending' AND date(due_date) < date('now', 'localtime')"

        # Subject filter
        if subject_filter and subject_filter != 'all':
            query += " AND subject = ?"
            params.append(subject_filter)

        # Priority filter
        if priority_filter and priority_filter != 'all':
            query += " AND priority = ?"
            params.append(priority_filter)

        # Search filter
        if search_query:
            query += " AND (title LIKE ? OR description LIKE ? OR subject LIKE ?)"
            wildcard = f"%{search_query}%"
            params.extend([wildcard, wildcard, wildcard])

        # Sorting logic
        sort_map = {
            'due_date_asc': " ORDER BY due_date ASC, priority DESC",
            'due_date_desc': " ORDER BY due_date DESC",
            'created_at_desc': " ORDER BY created_at DESC",
            'priority_desc': """ ORDER BY 
                CASE priority 
                    WHEN 'High' THEN 1 
                    WHEN 'Medium' THEN 2 
                    WHEN 'Low' THEN 3 
                    ELSE 4 
                END ASC, due_date ASC"""
        }
        query += sort_map.get(sort_by, " ORDER BY due_date ASC")

        conn = get_db_connection()
        rows = conn.execute(query, params).fetchall()
        conn.close()

        tasks = [calculate_task_metadata(dict(row)) for row in rows]
        return jsonify({'tasks': tasks})

    @app.route('/api/tasks', methods=['POST'])
    @login_required
    def create_task():
        data = request.get_json() or request.form
        title = (data.get('title') or '').strip()
        description = (data.get('description') or '').strip()
        subject = (data.get('subject') or 'General').strip()
        priority = data.get('priority', 'Medium').capitalize()
        due_date = (data.get('due_date') or '').strip()

        if not title:
            return jsonify({'error': 'Task title is required.'}), 400

        if priority not in ('Low', 'Medium', 'High'):
            priority = 'Medium'

        if not due_date:
            due_date = date.today().strftime('%Y-%m-%d')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (user_id, title, description, subject, priority, due_date, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Pending')
        """, (g.user['id'], title, description, subject, priority, due_date))
        task_id = cursor.lastrowid
        conn.commit()

        new_row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()

        new_task = calculate_task_metadata(dict(new_row))
        return jsonify({'task': new_task, 'message': 'Task created successfully!'}), 201

    @app.route('/api/tasks/<int:task_id>', methods=['PUT'])
    @login_required
    def update_task(task_id):
        conn = get_db_connection()
        task = conn.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, g.user['id'])).fetchone()
        if not task:
            conn.close()
            return jsonify({'error': 'Task not found.'}), 404

        data = request.get_json() or request.form
        title = (data.get('title') or task['title']).strip()
        description = data.get('description', task['description'])
        subject = (data.get('subject') or task['subject']).strip()
        priority = data.get('priority', task['priority'])
        due_date = (data.get('due_date') or task['due_date']).strip()
        status = data.get('status', task['status'])

        if not title:
            conn.close()
            return jsonify({'error': 'Task title cannot be empty.'}), 400

        if priority not in ('Low', 'Medium', 'High'):
            priority = task['priority']

        if status not in ('Pending', 'Completed'):
            status = task['status']

        conn.execute("""
            UPDATE tasks
            SET title = ?, description = ?, subject = ?, priority = ?, due_date = ?, status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        """, (title, description, subject, priority, due_date, status, task_id, g.user['id']))
        conn.commit()

        updated_row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()

        updated_task = calculate_task_metadata(dict(updated_row))
        return jsonify({'task': updated_task, 'message': 'Task updated successfully!'})

    @app.route('/api/tasks/<int:task_id>/toggle', methods=['POST'])
    @login_required
    def toggle_task(task_id):
        conn = get_db_connection()
        task = conn.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, g.user['id'])).fetchone()
        if not task:
            conn.close()
            return jsonify({'error': 'Task not found.'}), 404

        new_status = 'Completed' if task['status'] == 'Pending' else 'Pending'
        conn.execute("""
            UPDATE tasks
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        """, (new_status, task_id, g.user['id']))
        conn.commit()

        updated_row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()

        updated_task = calculate_task_metadata(dict(updated_row))
        msg = "Task marked as completed!" if new_status == 'Completed' else "Task marked as pending."
        return jsonify({'task': updated_task, 'message': msg})

    @app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
    @login_required
    def delete_task(task_id):
        conn = get_db_connection()
        task = conn.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, g.user['id'])).fetchone()
        if not task:
            conn.close()
            return jsonify({'error': 'Task not found.'}), 404

        conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, g.user['id']))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Task deleted successfully!'})

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
