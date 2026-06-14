import sqlite3

DB_PATH = 'database/app.db'

SUBJECTS = [
    'turkmen', 'english', 'informatics', 'history', 'jemgyyet',
    'economics', 'biology', 'chemistry', 'mathematics', 'physics', 'zehin',
]

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
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

def upsert_result(student_id, cmp):
    data = {'student_id': student_id}
    for s in SUBJECTS:
        data[f'{s}_c'] = cmp[s]['correct']
        data[f'{s}_w'] = cmp[s]['wrong']
        data[f'{s}_n'] = cmp[s]['no_answer']
    t = cmp['_total']
    data['total_correct']   = t['correct']
    data['total_wrong']     = t['wrong']
    data['total_no_answer'] = t['no_answer']
    data['score']           = t['score']
    col_names = [k for k in data if k != 'student_id']
    cols_sql  = ', '.join(col_names)
    vals_sql  = ', '.join(f':{k}' for k in col_names)
    upd_sql   = ', '.join(f'{k} = :{k}' for k in col_names)
    conn = get_connection()
    conn.execute(f'''
        INSERT INTO results (student_id, {cols_sql})
        VALUES (:student_id, {vals_sql})
        ON CONFLICT(student_id) DO UPDATE SET {upd_sql}, computed_at = CURRENT_TIMESTAMP
    ''', data)
    conn.commit()
    conn.close()

def delete_results_for_book_type(book_type):
    conn = get_connection()
    conn.execute('''
        DELETE FROM results
        WHERE student_id IN (SELECT id FROM students WHERE book_type = ?)
    ''', (book_type,))
    conn.commit()
    conn.close()

def get_all_answer_keys():
    conn = get_connection()
    rows = conn.execute('SELECT * FROM answer_keys ORDER BY book_type').fetchall()
    conn.close()
    return {row['book_type']: row for row in rows}

def upsert_answer_key(book_type, answers):
    conn = get_connection()
    conn.execute('''
        INSERT INTO answer_keys (book_type, answers)
        VALUES (?, ?)
        ON CONFLICT(book_type) DO UPDATE SET answers = excluded.answers,
                                             uploaded_at = CURRENT_TIMESTAMP
    ''', (book_type, answers))
    conn.commit()
    conn.close()
