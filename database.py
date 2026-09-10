import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'student_tasks.db')

def get_db_connection():
    """Establish and return an SQLite connection configured for dict-like rows."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(reset=False):
    """Initialize tables using schema.sql. If reset=True, drop and recreate tables."""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    conn = get_db_connection()
    with conn:
        if reset:
            conn.execute("DROP TABLE IF EXISTS tasks;")
            conn.execute("DROP TABLE IF EXISTS users;")
        conn.executescript(schema_sql)
    conn.close()

if __name__ == '__main__':
    print(f"Initializing clean database at: {DATABASE_PATH}")
    init_db(reset=True)
    print("Database cleanly initialized with zero static/dummy data.")
