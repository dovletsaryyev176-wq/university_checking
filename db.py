import sqlite3

DB_PATH = 'database/app.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init():
    conn = get_connection()
    with open('database/schema.sql', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.close()

def get_all_students():
    conn = get_connection()
    rows = conn.execute('SELECT * FROM students ORDER BY student_number').fetchall()
    conn.close()
    return rows

def student_exists(student_number):
    conn = get_connection()
    row = conn.execute(
        'SELECT id FROM students WHERE student_number = ?', (student_number,)
    ).fetchone()
    conn.close()
    return row is not None

def insert_student(data):
    conn = get_connection()
    conn.execute('''
        INSERT INTO students (
            student_number, first_name, last_name, book_type,
            direction1, direction2, direction3, direction4,
            turkmen, english, informatics, history, jemgyyet,
            economics, biology, chemistry, mathematics, physics, zehin
        ) VALUES (
            :student_number, :first_name, :last_name, :book_type,
            :direction1, :direction2, :direction3, :direction4,
            :turkmen, :english, :informatics, :history, :jemgyyet,
            :economics, :biology, :chemistry, :mathematics, :physics, :zehin
        )
    ''', data)
    conn.commit()
    conn.close()

def delete_student(student_id):
    conn = get_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
    conn.commit()
    conn.close()
