from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import json
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Database configuration
DATABASE = 'school_management.db'

def get_db_connection():
    """Establish database connection with row factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()

    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('director', 'profesor', 'padre')),
            full_name TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Students table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth DATE,
            grade TEXT NOT NULL,
            parent_id INTEGER,
            address TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES users (id)
        )
    ''')

    # Teachers table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            subject TEXT,
            hire_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Subjects table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            teacher_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id)
        )
    ''')

    # Grades table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            grade_value REAL NOT NULL,
            grade_type TEXT NOT NULL CHECK (grade_type IN ('parcial', 'final', 'tarea')),
            date_recorded DATE DEFAULT CURRENT_DATE,
            teacher_id INTEGER,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (subject_id) REFERENCES subjects (id),
            FOREIGN KEY (teacher_id) REFERENCES teachers (id)
        )
    ''')

    # Rooms table - NEW
    conn.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            capacity INTEGER,
            room_type TEXT,
            equipment TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Schedules table - NEW
    conn.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            teacher_id INTEGER NOT NULL,
            room_id INTEGER,
            date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            grade TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects (id),
            FOREIGN KEY (teacher_id) REFERENCES teachers (id),
            FOREIGN KEY (room_id) REFERENCES rooms (id)
        )
    ''')

    # Announcements table - NEW
    conn.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT,
            priority TEXT NOT NULL CHECK (priority IN ('alta', 'media', 'baja')),
            target_audience TEXT NOT NULL CHECK (target_audience IN ('todos', 'estudiantes', 'profesores', 'padres')),
            author_id INTEGER NOT NULL,
            expires_at DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users (id)
        )
    ''')

    # Create default admin user
    admin_password = generate_password_hash('admin123')
    conn.execute('''
        INSERT OR IGNORE INTO users (username, password, role, full_name, email)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', admin_password, 'director', 'Administrador del Sistema', 'admin@school.edu'))


    # Create default admin user
  
    conn.execute('''
        INSERT OR IGNORE INTO users (username, password, role, full_name, email)
        VALUES (?, ?, ?, ?, ?)
    ''', ('juan', generate_password_hash('juan123'), 'padre', 'ricardo tapia', 'father@school.edu'))

    conn.commit()
    conn.close()
init_db()

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session or session['user_role'] not in roles:
                flash('No tienes permisos para acceder a esta página.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Authentication routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_role'] = user['role']
            session['full_name'] = user['full_name']
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()

    # Get statistics
    total_students = conn.execute('SELECT COUNT(*) as count FROM students').fetchone()['count']
    total_teachers = conn.execute('SELECT COUNT(*) as count FROM teachers').fetchone()['count']
    total_subjects = conn.execute('SELECT COUNT(*) as count FROM subjects').fetchone()['count']
    total_schedules = conn.execute('SELECT COUNT(*) as count FROM schedules').fetchone()['count']
    total_announcements = conn.execute('SELECT COUNT(*) as count FROM announcements WHERE expires_at IS NULL OR expires_at >= date("now")').fetchone()['count']
    total_rooms = conn.execute('SELECT COUNT(*) as count FROM rooms').fetchone()['count']

    # Get recent announcements
    recent_announcements = conn.execute('''
        SELECT a.*, u.full_name as author_name
        FROM announcements a
        JOIN users u ON a.author_id = u.id
        WHERE (a.expires_at IS NULL OR a.expires_at >= date('now'))
        AND (a.target_audience = 'todos' OR a.target_audience = ?)
        ORDER BY a.created_at DESC
        LIMIT 3
    ''', (session['user_role'],)).fetchall()

    conn.close()

    stats = {
        'students': total_students,
        'teachers': total_teachers,
        'subjects': total_subjects,
        'schedules': total_schedules,
        'announcements': total_announcements,
        'rooms': total_rooms
    }

    return render_template('dashboard.html', stats=stats, recent_announcements=recent_announcements)

# Student Management Routes
@app.route('/students')
@login_required
@role_required(['director', 'profesor'])
def list_students():
    conn = get_db_connection()
    students = conn.execute('''SELECT s.*, u.full_name as parent_name 
FROM students s 
LEFT JOIN users u ON s.parent_id = u.id
ORDER BY 
    CASE s.grade
        WHEN '1ro Primaria' THEN 1
        WHEN '2do Primaria' THEN 2
        WHEN '3ro Primaria' THEN 3
        WHEN '4to Primaria' THEN 4
        WHEN '5to Primaria' THEN 5
        WHEN '6to Primaria' THEN 6
        WHEN '1ro Secundaria' THEN 7
        WHEN '2do Secundaria' THEN 8
        WHEN '3ro Secundaria' THEN 9
        WHEN '4to Secundaria' THEN 10
        WHEN '5to Secundaria' THEN 11
        WHEN '6to Secundaria' THEN 12
        ELSE 99  -- Opcional: para grados no listados
    END,
    s.last_name, 
    s.first_name;
    ''').fetchall()
    conn.close()
    return render_template('students/list.html', students=students)

@app.route('/students/add', methods=['GET', 'POST'])
@login_required
@role_required(['director', 'profesor'])
def add_student():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        grade = request.form['grade']
        address = request.form['address']
        phone = request.form['phone']
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO students (first_name, last_name, date_of_birth, grade, address, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, date_of_birth, grade, address, phone))
        conn.commit()
        conn.close()
        
        flash('Estudiante registrado exitosamente.', 'success')
        return redirect(url_for('list_students'))

    return render_template('students/add.html')

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(['director', 'profesor'])
def edit_student(id):
    conn = get_db_connection()

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        grade = request.form['grade']
        address = request.form['address']
        phone = request.form['phone']
        
        conn.execute('''
            UPDATE students 
            SET first_name = ?, last_name = ?, date_of_birth = ?, grade = ?, address = ?, phone = ?
            WHERE id = ?
        ''', (first_name, last_name, date_of_birth, grade, address, phone, id))
        conn.commit()
        conn.close()
        
        flash('Estudiante actualizado exitosamente.', 'success')
        return redirect(url_for('list_students'))

    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    conn.close()

    if not student:
        flash('Estudiante no encontrado.', 'error')
        return redirect(url_for('list_students'))

    return render_template('students/edit.html', student=student)

@app.route('/students/delete/<int:id>')
@login_required
@role_required(['director'])
def delete_student(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Estudiante eliminado exitosamente.', 'success')
    return redirect(url_for('list_students'))

# Teacher Management Routes
@app.route('/teachers')
@login_required
@role_required(['director'])
def list_teachers():
    conn = get_db_connection()
    teachers = conn.execute('SELECT * FROM teachers ORDER BY last_name, first_name').fetchall()
    conn.close()
    return render_template('teachers/list.html', teachers=teachers)

@app.route('/teachers/add', methods=['GET', 'POST'])
@login_required
@role_required(['director'])
def add_teacher():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        subject = request.form['subject']
        hire_date = request.form['hire_date']
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO teachers (first_name, last_name, email, phone, subject, hire_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, email, phone, subject, hire_date))
        conn.commit()
        conn.close()
        
        flash('Profesor registrado exitosamente.', 'success')
        return redirect(url_for('list_teachers'))

    return render_template('teachers/add.html')

@app.route('/teachers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(['director'])
def edit_teacher(id):
    conn = get_db_connection()

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        subject = request.form['subject']
        hire_date = request.form['hire_date']
        
        conn.execute('''
            UPDATE teachers 
            SET first_name = ?, last_name = ?, email = ?, phone = ?, subject = ?, hire_date = ?
            WHERE id = ?
        ''', (first_name, last_name, email, phone, subject, hire_date, id))
        conn.commit()
        conn.close()
        
        flash('Profesor actualizado exitosamente.', 'success')
        return redirect(url_for('list_teachers'))

    teacher = conn.execute('SELECT * FROM teachers WHERE id = ?', (id,)).fetchone()
    conn.close()

    if not teacher:
        flash('Profesor no encontrado.', 'error')
        return redirect(url_for('list_teachers'))

    return render_template('teachers/edit.html', teacher=teacher)

@app.route('/teachers/delete/<int:id>')
@login_required
@role_required(['director'])
def delete_teacher(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM teachers WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Profesor eliminado exitosamente.', 'success')
    return redirect(url_for('list_teachers'))

# Grade Management Routes
@app.route('/grades')
@login_required
def list_grades():
    conn = get_db_connection()

    if session['user_role'] == 'padre':
        # Parents can only see their children's grades
        grades = conn.execute('''
            SELECT g.*, s.first_name || ' ' || s.last_name as student_name,
                   sub.name as subject_name, t.first_name || ' ' || t.last_name as teacher_name
            FROM grades g
            JOIN students s ON g.student_id = s.id
            JOIN subjects sub ON g.subject_id = sub.id
            JOIN teachers t ON g.teacher_id = t.id
            WHERE s.parent_id = ?
            ORDER BY g.date_recorded DESC
        ''', (session['user_id'],)).fetchall()
    else:
        grades = conn.execute('''
            SELECT g.*, s.first_name || ' ' || s.last_name as student_name,
                   sub.name as subject_name, t.first_name || ' ' || t.last_name as teacher_name
            FROM grades g
            JOIN students s ON g.student_id = s.id
            JOIN subjects sub ON g.subject_id = sub.id
            JOIN teachers t ON g.teacher_id = t.id
            ORDER BY g.date_recorded DESC
        ''').fetchall()

    conn.close()
    return render_template('grades/list.html', grades=grades)

@app.route('/grades/add', methods=['GET', 'POST'])
@login_required
@role_required(['director', 'profesor'])
def add_grade():
    conn = get_db_connection()

    if request.method == 'POST':
        student_id = request.form['student_id']
        subject_id = request.form['subject_id']
        grade_value = request.form['grade_value']
        grade_type = request.form['grade_type']
        teacher_id = request.form['teacher_id']
        
        conn.execute('''
            INSERT INTO grades (student_id, subject_id, grade_value, grade_type, teacher_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, subject_id, grade_value, grade_type, teacher_id))
        conn.commit()
        conn.close()
        
        flash('Nota registrada exitosamente.', 'success')
        return redirect(url_for('list_grades'))

    students = conn.execute('SELECT * FROM students ORDER BY last_name, first_name').fetchall()
    subjects = conn.execute('SELECT * FROM subjects ORDER BY name').fetchall()
    teachers = conn.execute('SELECT * FROM teachers ORDER BY last_name, first_name').fetchall()
    conn.close()

    return render_template('grades/add.html', students=students, subjects=subjects, teachers=teachers)

# Subject Management Routes
@app.route('/subjects')
@login_required
@role_required(['director', 'profesor'])
def list_subjects():
    conn = get_db_connection()
    subjects = conn.execute('''
        SELECT s.*, t.first_name || ' ' || t.last_name as teacher_name
        FROM subjects s
        LEFT JOIN teachers t ON s.teacher_id = t.id
        ORDER BY s.name
    ''').fetchall()
    conn.close()
    return render_template('subjects/list.html', subjects=subjects)

@app.route('/subjects/add', methods=['GET', 'POST'])
@login_required
@role_required(['director'])
def add_subject():
    conn = get_db_connection()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        teacher_id = request.form['teacher_id'] if request.form['teacher_id'] else None
        
        conn.execute('''
            INSERT INTO subjects (name, description, teacher_id)
            VALUES (?, ?, ?)
        ''', (name, description, teacher_id))
        conn.commit()
        conn.close()
        
        flash('Materia registrada exitosamente.', 'success')
        return redirect(url_for('list_subjects'))

    teachers = conn.execute('SELECT * FROM teachers ORDER BY last_name, first_name').fetchall()
    conn.close()

    return render_template('subjects/add.html', teachers=teachers)

# Schedule Management Routes - NEW
@app.route('/schedules')
@login_required
def list_schedules():
    # Get week parameter or default to current week
    week_param = request.args.get('week')
    if week_param:
        try:
            week_start = datetime.strptime(week_param, '%Y-%m-%d').date()
        except ValueError:
            week_start = datetime.now().date()
    else:
        week_start = datetime.now().date()
    
    # Adjust to Monday of the week
    week_start = week_start - timedelta(days=week_start.weekday())
    week_end = week_start + timedelta(days=6)
    
    conn = get_db_connection()
    schedules = conn.execute('''
        SELECT s.*, sub.name as subject_name, 
               t.first_name || ' ' || t.last_name as teacher_name,
               r.name as room_name
        FROM schedules s
        JOIN subjects sub ON s.subject_id = sub.id
        JOIN teachers t ON s.teacher_id = t.id
        LEFT JOIN rooms r ON s.room_id = r.id
        WHERE s.date BETWEEN ? AND ?
        ORDER BY s.date, s.start_time
    ''', (week_start, week_end)).fetchall()
    conn.close()
    
    return render_template('schedules/list.html', 
                         schedules=schedules, 
                         week_start=week_start, 
                         week_end=week_end,
                         timedelta=timedelta)

@app.route('/schedules/add', methods=['GET', 'POST'])
@login_required
@role_required(['director', 'profesor'])
def add_schedule():
    conn = get_db_connection()
    
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        teacher_id = request.form['teacher_id']
        room_id = request.form['room_id'] if request.form['room_id'] else None
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        grade = request.form['grade']
        notes = request.form['notes']
        
        # Check for scheduling conflicts
        conflict = conn.execute('''
            SELECT COUNT(*) as count FROM schedules 
            WHERE date = ? AND room_id = ? 
            AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?))
        ''', (date, room_id, start_time, start_time, end_time, end_time)).fetchone()
        
        if room_id and conflict['count'] > 0:
            flash('Conflicto de horario: el aula ya está ocupada en ese horario.', 'error')
        else:
            conn.execute('''
                INSERT INTO schedules (subject_id, teacher_id, room_id, date, start_time, end_time, grade, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (subject_id, teacher_id, room_id, date, start_time, end_time, grade, notes))
            conn.commit()
            flash('Horario registrado exitosamente.', 'success')
            conn.close()
            return redirect(url_for('list_schedules'))
    
    subjects = conn.execute('SELECT * FROM subjects ORDER BY name').fetchall()
    teachers = conn.execute('SELECT * FROM teachers ORDER BY last_name, first_name').fetchall()
    rooms = conn.execute('SELECT * FROM rooms ORDER BY name').fetchall()
    conn.close()
    
    return render_template('schedules/add.html', subjects=subjects, teachers=teachers, rooms=rooms)

@app.route('/schedules/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(['director', 'profesor'])
def edit_schedule(id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        teacher_id = request.form['teacher_id']
        room_id = request.form['room_id'] if request.form['room_id'] else None
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        grade = request.form['grade']
        notes = request.form['notes']
        
        # Check for scheduling conflicts (excluding current schedule)
        conflict = conn.execute('''
            SELECT COUNT(*) as count FROM schedules 
            WHERE date = ? AND room_id = ? AND id != ?
            AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?))
        ''', (date, room_id, id, start_time, start_time, end_time, end_time)).fetchone()
        
        if room_id and conflict['count'] > 0:
            flash('Conflicto de horario: el aula ya está ocupada en ese horario.', 'error')
        else:
            conn.execute('''
                UPDATE schedules 
                SET subject_id = ?, teacher_id = ?, room_id = ?, date = ?, 
                    start_time = ?, end_time = ?, grade = ?, notes = ?
                WHERE id = ?
            ''', (subject_id, teacher_id, room_id, date, start_time, end_time, grade, notes, id))
            conn.commit()
            flash('Horario actualizado exitosamente.', 'success')
            conn.close()
            return redirect(url_for('list_schedules'))
    
    schedule = conn.execute('SELECT * FROM schedules WHERE id = ?', (id,)).fetchone()
    if not schedule:
        flash('Horario no encontrado.', 'error')
        conn.close()
        return redirect(url_for('list_schedules'))
    
    subjects = conn.execute('SELECT * FROM subjects ORDER BY name').fetchall()
    teachers = conn.execute('SELECT * FROM teachers ORDER BY last_name, first_name').fetchall()
    rooms = conn.execute('SELECT * FROM rooms ORDER BY name').fetchall()
    conn.close()
    
    return render_template('schedules/edit.html', 
                         schedule=schedule, 
                         subjects=subjects, 
                         teachers=teachers, 
                         rooms=rooms)

@app.route('/schedules/delete/<int:id>')
@login_required
@role_required(['director'])
def delete_schedule(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM schedules WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('Horario eliminado exitosamente.', 'success')
    return redirect(url_for('list_schedules'))

@app.route('/schedules/calendar')
@login_required
def schedule_calendar():
    conn = get_db_connection()
    schedules = conn.execute('''
        SELECT s.*, sub.name as subject_name, 
               t.first_name || ' ' || t.last_name as teacher_name,
               r.name as room_name
        FROM schedules s
        JOIN subjects sub ON s.subject_id = sub.id
        JOIN teachers t ON s.teacher_id = t.id
        LEFT JOIN rooms r ON s.room_id = r.id
        ORDER BY s.date, s.start_time
    ''').fetchall()
    
    events = []
    for schedule in schedules:
        events.append({
            'title': f"{schedule['subject_name']} - {schedule['grade']}",
            'start': f"{schedule['date']}T{schedule['start_time']}",
            'end': f"{schedule['date']}T{schedule['end_time']}",
            'description': f"Profesor: {schedule['teacher_name']}\nAula: {schedule['room_name'] or 'No asignada'}"
        })
    
    conn.close()
    return render_template('schedules/calendar.html', events=json.dumps(events))

# Announcement Management Routes - NEW
@app.route('/announcements')
@login_required
def list_announcements():
    category = request.args.get('category', '')
    priority = request.args.get('priority', '')
    
    query = '''
        SELECT a.*, u.full_name as author_name
        FROM announcements a
        JOIN users u ON a.author_id = u.id
        WHERE (a.expires_at IS NULL OR a.expires_at >= date('now'))
        AND (a.target_audience = 'todos' OR a.target_audience = ?)
    '''
    params = [session['user_role']]
    
    if category:
        query += ' AND a.category = ?'
        params.append(category)
    
    if priority:
        query += ' AND a.priority = ?'
        params.append(priority)
    
    query += ' ORDER BY a.created_at DESC'
    
    conn = get_db_connection()
    announcements = conn.execute(query, params).fetchall()
    categories = conn.execute('SELECT DISTINCT category FROM announcements WHERE category IS NOT NULL').fetchall()
    conn.close()
    
    return render_template('announcements/list.html', 
                         announcements=announcements, 
                         categories=categories,
                         current_category=category,
                         current_priority=priority)

@app.route('/announcements/add', methods=['GET', 'POST'])
@login_required
@role_required(['director', 'profesor'])
def add_announcement():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category'] if request.form['category'] else None
        priority = request.form['priority']
        target_audience = request.form['target_audience']
        expires_at = request.form['expires_at'] if request.form['expires_at'] else None
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO announcements (title, content, category, priority, target_audience, author_id, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, content, category, priority, target_audience, session['user_id'], expires_at))
        conn.commit()
        conn.close()
        
        flash('Anuncio publicado exitosamente.', 'success')
        return redirect(url_for('list_announcements'))
    
    return render_template('announcements/add.html')

@app.route('/announcements/view/<int:id>')
@login_required
def view_announcement(id):
    conn = get_db_connection()
    announcement = conn.execute('''
        SELECT a.*, u.full_name as author_name
        FROM announcements a
        JOIN users u ON a.author_id = u.id
        WHERE a.id = ?
    ''', (id,)).fetchone()
    conn.close()
    
    if not announcement:
        flash('Anuncio no encontrado.', 'error')
        return redirect(url_for('list_announcements'))
    
    return render_template('announcements/view.html', announcement=announcement)

@app.route('/announcements/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(['director', 'profesor'])
def edit_announcement(id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category'] if request.form['category'] else None
        priority = request.form['priority']
        target_audience = request.form['target_audience']
        expires_at = request.form['expires_at'] if request.form['expires_at'] else None
        
        conn.execute('''
            UPDATE announcements 
            SET title = ?, content = ?, category = ?, priority = ?, target_audience = ?, expires_at = ?
            WHERE id = ?
        ''', (title, content, category, priority, target_audience, expires_at, id))
        conn.commit()
        conn.close()
        
        flash('Anuncio actualizado exitosamente.', 'success')
        return redirect(url_for('list_announcements'))
    
    announcement = conn.execute('SELECT * FROM announcements WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if not announcement:
        flash('Anuncio no encontrado.', 'error')
        return redirect(url_for('list_announcements'))
    
    return render_template('announcements/edit.html', announcement=announcement)

@app.route('/announcements/delete/<int:id>')
@login_required
@role_required(['director'])
def delete_announcement(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM announcements WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('Anuncio eliminado exitosamente.', 'success')
    return redirect(url_for('list_announcements'))

# Room Management Routes - NEW
@app.route('/rooms')
@login_required
@role_required(['director', 'profesor'])
def list_rooms():
    conn = get_db_connection()
    rooms = conn.execute('SELECT * FROM rooms ORDER BY name').fetchall()
    conn.close()
    return render_template('rooms/list.html', rooms=rooms)

@app.route('/rooms/add', methods=['GET', 'POST'])
@login_required
@role_required(['director'])
def add_room():
    if request.method == 'POST':
        name = request.form['name']
        capacity = request.form['capacity'] if request.form['capacity'] else None
        room_type = request.form['room_type'] if request.form['room_type'] else None
        equipment = request.form['equipment']
        location = request.form['location']
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO rooms (name, capacity, room_type, equipment, location)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, capacity, room_type, equipment, location))
        conn.commit()
        conn.close()
        
        flash('Aula registrada exitosamente.', 'success')
        return redirect(url_for('list_rooms'))
    
    return render_template('rooms/add.html')

# User Management Routes (Solo Director)
@app.route('/users')
@login_required
@role_required(['director'])
def list_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY role, full_name').fetchall()
    conn.close()
    return render_template('users/list.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
@role_required(['director'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        full_name = request.form['full_name']
        email = request.form['email']
        
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO users (username, password, role, full_name, email)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, hashed_password, role, full_name, email))
            conn.commit()
            flash('Usuario creado exitosamente.', 'success')
            return redirect(url_for('list_users'))
        except sqlite3.IntegrityError:
            flash('El nombre de usuario ya existe.', 'error')
        finally:
            conn.close()
    
    return render_template('users/add.html')

@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(['director'])
def edit_user(id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()
    
    if not user:
        flash('Usuario no encontrado.', 'error')
        conn.close()
        return redirect(url_for('list_users'))
    
    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        full_name = request.form['full_name']
        email = request.form['email']
        new_password = request.form.get('new_password')
        
        update_data = [username, role, full_name, email, id]
        update_query = '''
            UPDATE users 
            SET username = ?, role = ?, full_name = ?, email = ?
        '''
        
        if new_password:
            hashed_password = generate_password_hash(new_password)
            update_query = update_query.replace('?', '?, ?', 1)
            update_query += ', password = ?'
            update_data.insert(4, hashed_password)
        
        update_query += ' WHERE id = ?'
        
        try:
            conn.execute(update_query, tuple(update_data))
            conn.commit()
            flash('Usuario actualizado exitosamente.', 'success')
            return redirect(url_for('list_users'))
        except sqlite3.IntegrityError:
            flash('El nombre de usuario ya existe.', 'error')
        finally:
            conn.close()
    
    return render_template('users/edit.html', user=user)

@app.route('/users/delete/<int:id>')
@login_required
@role_required(['director'])
def delete_user(id):
    # Prevenir eliminación del usuario admin principal
    if id == 1:
        flash('No se puede eliminar el usuario administrador principal.', 'error')
        return redirect(url_for('list_users'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('Usuario eliminado exitosamente.', 'success')
    return redirect(url_for('list_users'))

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
