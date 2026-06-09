from flask import Flask, render_template, request, redirect, url_for, flash
import db

app = Flask(__name__)
app.secret_key = 'university-secret-key'

# Fixed-width field slices
FIELDS = [
    ('student_number', slice(0,   10)),
    ('first_name',     slice(10,  22)),
    ('last_name',      slice(22,  34)),
    ('book_type',      slice(34,  35)),
    ('direction1',     slice(35,  39)),
    ('direction2',     slice(39,  43)),
    ('direction3',     slice(43,  47)),
    ('direction4',     slice(47,  51)),
    ('turkmen',        slice(51,  71)),
    ('english',        slice(71,  91)),
    ('informatics',    slice(91,  106)),
    ('history',        slice(106, 121)),
    ('jemgyyet',       slice(121, 136)),
    ('economics',      slice(136, 151)),
    ('biology',        slice(151, 166)),
    ('chemistry',      slice(166, 186)),
    ('mathematics',    slice(186, 206)),
    ('physics',        slice(206, 226)),
    ('zehin',          slice(226, 241)),
]

def parse_line(line):
    return {name: line[s].strip() for name, s in FIELDS}

@app.route('/')
def index():
    students = db.get_all_students()
    return render_template('index.html', students=students)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file or file.filename == '':
        flash('Файл не выбран.', 'warning')
        return redirect(url_for('index'))

    raw = file.read()
    try:
        content = raw.decode('utf-8')
    except UnicodeDecodeError:
        content = raw.decode('windows-1251')

    added = 0
    skipped = []

    for line in content.splitlines():
        if len(line) < 241:
            continue
        student = parse_line(line)
        if not student['student_number']:
            continue
        if db.student_exists(student['student_number']):
            skipped.append(student['student_number'])
        else:
            db.insert_student(student)
            added += 1

    if added:
        flash(f'Добавлено студентов: {added}', 'success')
    if skipped:
        flash(f'Уже существуют (пропущены): {", ".join(skipped)}', 'warning')
    if not added and not skipped:
        flash('В файле не найдено подходящих строк.', 'danger')

    return redirect(url_for('index'))

@app.route('/delete/<int:student_id>', methods=['POST'])
def delete(student_id):
    db.delete_student(student_id)
    flash('Студент удалён.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    db.init()
    app.run(host='0.0.0.0', port=8000, debug=True)
