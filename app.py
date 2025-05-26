
from flask import Flask,jsonify, get_flashed_messages, render_template, request, flash, redirect, url_for, session, g, send_from_directory
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import datetime
import random
import uuid

app = Flask(__name__)
app.secret_key = 'super_secret_key'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database.db')

# Configure static and template folders
app.static_folder = 'static'
app.template_folder = 'templates'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure folders exist
os.makedirs(app.static_folder, exist_ok=True)
os.makedirs(app.template_folder, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# File upload validation
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.executescript('''
        CREATE TABLE IF NOT EXISTS laborers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            language TEXT NOT NULL,
            aadhar TEXT NOT NULL UNIQUE,
            dob TEXT NOT NULL,
            sex TEXT NOT NULL,
            address TEXT NOT NULL,
            abilities TEXT,
            employment_length TEXT,
            employment_unit TEXT,
            photo TEXT,
            employment_proof TEXT,
            password TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS employers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            language TEXT NOT NULL,
            aadhar TEXT NOT NULL,
            dob TEXT NOT NULL,
            sex TEXT NOT NULL,
            address TEXT NOT NULL,
            abilities_required TEXT,
            company_id INTEGER,
            password TEXT NOT NULL,
            FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
        
        CREATE TABLE IF NOT EXISTS company (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            reg_id TEXT UNIQUE NOT NULL,  -- Company Registration ID
            address TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS jobs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            posted_by INTEGER NOT NULL,
            job_title TEXT NOT NULL,
            location TEXT NOT NULL,
            work_start TIME NOT NULL,       
            work_end TIME NOT NULL,         
            duration_start DATE NOT NULL,   
            duration_end DATE NOT NULL,     
            description TEXT NOT NULL,
            salary INTEGER NOT NULL,
            FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE
        );

        
        CREATE TABLE IF NOT EXISTS grievances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            issues TEXT NOT NULL,
            complaint TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved integer,
            admin_reply TEXT DEFAULT NULL,
            FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES laborers(id) ON DELETE CASCADE
        );

    
        
        CREATE TABLE IF NOT EXISTS employment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    laborer_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT,
    FOREIGN KEY (laborer_id) REFERENCES laborers(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

          CREATE TABLE IF NOT EXISTS schemes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            offered_by TEXT NOT NULL,
            description TEXT NOT NULL,
            registration_link TEXT,
            read_more_link TEXT
        );
        
    
        

        CREATE TABLE IF NOT EXISTS scheme_eligibility (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scheme_id INTEGER NOT NULL,
            criteria TEXT NOT NULL,
            FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE CASCADE
        );
        
CREATE TABLE IF NOT EXISTS job_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    laborer_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (laborer_id) REFERENCES laborers(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);
        
        CREATE TABLE IF NOT EXISTS messages
        ( id INTEGER PRIMARY KEY AUTOINCREMENT, laborer_id INTEGER NOT NULL, 
        employer_id INTEGER NOT NULL, message TEXT NOT NULL, 
        conversation_id TEXT, 
        sender_type TEXT NOT NULL CHECK(sender_type IN ('laborer', 'employer')),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, application_id INTEGER, 
        job_id INTEGER, 
        FOREIGN KEY (laborer_id) REFERENCES laborers(id) ON DELETE CASCADE,
        FOREIGN KEY (employer_id) REFERENCES employers(id) ON DELETE CASCADE, 
        FOREIGN KEY (application_id) REFERENCES job_applications(id) ON DELETE CASCADE, FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
        CHECK ( (application_id IS NOT NULL AND job_id IS NULL) OR (application_id IS NULL AND job_id IS NOT NULL) ) );

        ''')

        db.commit()
        
def assign_missing_uuids():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    for table in ['laborers', 'employers']:
        cursor.execute(f"SELECT id FROM {table} WHERE uuid IS NULL OR uuid = ''")
        rows = cursor.fetchall()

        for row in rows:
            new_uuid = generate_unique_uuid(table, cursor)
            cursor.execute(f"UPDATE {table} SET uuid = ? WHERE id = ?", (new_uuid, row['id']))
            print(f"Assigned UUID {new_uuid} to {table[:-1]} ID {row['id']}")

    conn.commit()
    conn.close()


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    

    new_password = 'admin'
    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE admin SET password = ? WHERE id = ?', (hashed_password, 1))
    conn.commit()
    conn.close()

    print("Password updated.")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = ?', (username,))
        admin = cursor.fetchone()
        print(admin, admin['id'])
        if admin and check_password_hash(admin['password'], password):
            session['admin_id'] = admin['id']
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials.', 'error')
            return render_template('admin_login.html')

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    return redirect(url_for('home'))

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

@app.route('/verify_license', methods=['POST'])
def verify_license():
    employer_id = request.form['employer_id']
    db = get_db()
    cursor = db.cursor()

    cursor.execute('UPDATE employers SET verified = 1 WHERE id = ?', (employer_id,))
    db.commit()

    flash('Employer license verified successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST' and 'forward_grievance' in request.form:
        grievance_id = request.form['grievance_id']
        forward_email = request.form['forward_email']

        # Fetch grievance, laborer, and employer details
        cursor.execute('''
            SELECT g.issues, g.complaint, g.created_at,
                   c.name AS company_name,
                   l.name AS laborer_name, l.phone AS laborer_phone,
                   e.name AS employer_name, e.phone AS employer_phone, e.email AS employer_email
            FROM grievances g
            JOIN company c ON g.company_id = c.id
            JOIN laborers l ON g.user_id = l.id
            JOIN employers e ON e.company_id = c.id
            WHERE g.id = ?
            LIMIT 1
        ''', (grievance_id,))
        grievance_info = cursor.fetchone()

        if grievance_info:
            # Compose the email
            email_body = f"""Grievance Forwarded:

Company: {grievance_info['company_name']}
Issue: {grievance_info['issues']}
Complaint: {grievance_info['complaint']}
Submitted On: {grievance_info['created_at']}

Laborer Details:
Name: {grievance_info['laborer_name']}
Phone: {grievance_info['laborer_phone']}

Employer Details:
Name: {grievance_info['employer_name']}
Phone: {grievance_info['employer_phone']}
Email: {grievance_info['employer_email']}
"""

            msg = MIMEText(email_body)
            msg['Subject'] = 'Forwarded Grievance Details'
            msg['From'] = formataddr(('Admin', 'neilthedev05@gmail.com'))
            msg['To'] = forward_email

            try:
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login('neilthedev05@gmail.com', 'umzb gufm kawt edee')
                    server.send_message(msg)
                flash('Grievance forwarded successfully.', 'success')
            except Exception as e:
                flash(f'Error sending email: {str(e)}', 'error')
        else:
            flash('Grievance not found.', 'error')

        return redirect(url_for('admin_dashboard'))

    # Handle new scheme creation
    if request.method == 'POST' and 'add_scheme' in request.form:
        title = request.form['title']
        offered_by = request.form['offered_by']
        description = request.form['description']
        registration_link = request.form.get('registration_link', '')
        read_more_link = request.form.get('read_more_link', '')

        # Insert new scheme into schemes table
        cursor.execute('''
            INSERT INTO schemes (title, offered_by, description, registration_link, read_more_link)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, offered_by, description, registration_link, read_more_link))
        
        db.commit()
        scheme_id = cursor.lastrowid

     
        eligibility_points = request.form.getlist('eligibility[]')

        for point in eligibility_points:
            cursor.execute('''
                INSERT INTO scheme_eligibility (scheme_id, criteria)
                VALUES (?, ?)
            ''', (scheme_id, point))

        db.commit()
        flash('Scheme added successfully with multiple eligibility criteria!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST' and 'submit_reply' in request.form:
        grievance_id = request.form['grievance_id']
        admin_reply = request.form['admin_reply'].strip()

        if admin_reply:
            cursor.execute('''
                UPDATE grievances
                SET admin_reply = ?, resolved = 1
                WHERE id = ?
            ''', (admin_reply, grievance_id))
            db.commit()
            flash('Reply submitted and grievance marked as resolved.', 'success')
        else:
            flash('Reply cannot be empty.', 'error')
        return redirect(url_for('admin_dashboard'))

    cursor.execute('''
        SELECT s.id, s.title, s.offered_by, s.description, s.registration_link, s.read_more_link,
               GROUP_CONCAT(e.criteria, ', ') AS eligibility_points
        FROM schemes s
        LEFT JOIN scheme_eligibility e ON s.id = e.scheme_id
        GROUP BY s.id 
    ''')
    
    schemes = cursor.fetchall()

    cursor.execute('''
        SELECT g.id AS id, 
       g.issues, 
       g.complaint, 
       g.created_at, 
       g.resolved,
       g.admin_reply,
       c.name AS company_name, 
       l.name AS laborer_name, 
       l.phone AS laborer_phone,
       l.aadhar AS laborer_aadhar
        FROM grievances g
        JOIN company c ON g.company_id = c.id
        JOIN laborers l ON g.user_id = l.id
        ORDER BY g.created_at DESC
    ''')

    grievances = cursor.fetchall()
    
    cursor.execute('''
    SELECT e.id, e.name, e.phone, e.email, e.language, e.aadhar, e.dob, e.sex, e.address,
       e.abilities_required, e.license, e.verified, c.name AS company_name
FROM employers e
LEFT JOIN company c ON e.company_id = c.id
''')
    employers = cursor.fetchall()
    
    cursor.execute('''
    SELECT id, name, phone, language, aadhar, dob, sex, address, abilities, employment_length,
           employment_unit, photo, employment_proof
    FROM laborers
''')
    laborers = cursor.fetchall()

    cursor.execute('''
    SELECT j.id, j.job_title, j.location, j.work_start, j.work_end, j.duration_start,
           j.duration_end, j.description, j.salary, c.name AS company_name
    FROM jobs j
    JOIN company c ON j.company_id = c.id
''')
    jobs = cursor.fetchall()
    cursor.execute('''
    SELECT ja.id AS application_id, ja.status, ja.applied_at,
           l.name AS laborer_name, j.job_title, c.name AS company_name
    FROM job_applications ja
    JOIN laborers l ON ja.laborer_id = l.id
    JOIN jobs j ON ja.job_id = j.id
    JOIN company c ON j.company_id = c.id
''')
    applications = cursor.fetchall()



    return render_template('admin_dashboard.html', schemes=schemes, grievances=grievances, laborers=laborers,employers=employers, jobs=jobs,applications=applications)



@app.route('/admin/resolve_grievance/<int:grievance_id>')
def resolve_grievance(grievance_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    db = get_db()
    cursor = db.cursor()

    cursor.execute('UPDATE grievances SET resolved = 1 WHERE id = ?', (grievance_id,))
    db.commit()

    flash('Grievance resolved successfully!', 'success')
    return redirect(url_for('admin_dashboard'))



@app.route('/admin/add_scheme', methods=['POST'])
def add_scheme():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    title = request.form['title']
    offered_by = request.form['offered_by']
    description = request.form['description']
    eligibility_criteria = request.form['eligibility_criteria']
    registration_link = request.form['registration_link']
    read_more_link = request.form['read_more_link']

    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        INSERT INTO schemes (title, offered_by, description, eligibility_criteria, registration_link, read_more_link)
        VALUES (?, ?, ?, ?, ?, ?)''',
        (title, offered_by, description, eligibility_criteria, registration_link, read_more_link))

    db.commit()

    flash('Scheme added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/')
def home():
    return render_template('login.html')

@app.route('/schemes')
def schemes():
    if 'user_id' not in session:
        return render_template('schemes.html', schemes=[])

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute('''
            SELECT 
                s.id, 
                s.title, 
                s.offered_by, 
                s.description, 
                s.registration_link, 
                s.read_more_link, 
                (
                    SELECT GROUP_CONCAT(e.criteria, ', ') 
                    FROM scheme_eligibility e
                    WHERE e.scheme_id = s.id
                ) AS eligibility_points
            FROM schemes s
        ''')

        schemes = cursor.fetchall()
        return render_template('schemes.html', schemes=schemes)

    except Exception as e:
        print(f"Error: {e}")
        flash("Page is unable to load, please try again later.", 'error')
        return render_template('schemes.html', schemes=[], )
    
def generate_unique_uuid(table, cursor):
    while True:
        uuid = random.randint(1000000, 9999999)  # 7-digit number
        cursor.execute(f'SELECT id FROM {table} WHERE uuid = ?', (uuid,))
        if not cursor.fetchone():
            return uuid
        else: 
            return generate_unique_uuid(table, cursor)



@app.route('/register/laborer', methods=['GET', 'POST'])
def register_laborer():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        language = request.form['language']
        aadhar = request.form['aadhar']
        dob = request.form['dob']
        sex = request.form['sex']
        address = request.form['address']
        abilities = ",".join(request.form.getlist('abilities'))
        employment_length = request.form['employment-length']
        employment_unit = request.form['employment-unit']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        
        # Handle file uploads
        photo = request.files['photo']
        employment_proof = request.files['employment-proof']

        photo_filename = secure_filename(photo.filename) if photo and allowed_file(photo.filename) else None
        employment_proof_filename = secure_filename(employment_proof.filename) if employment_proof and allowed_file(employment_proof.filename) else None

        if photo_filename:
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        if employment_proof_filename:
            employment_proof.save(os.path.join(app.config['UPLOAD_FOLDER'], employment_proof_filename))

        db = get_db()
        cursor = db.cursor()
        laborer_uuid = generate_unique_uuid('laborers', cursor)
        # ✅ Uniqueness check for phone and aadhar
        cursor.execute('SELECT id FROM laborers WHERE phone = ? OR aadhar = ?', (phone, aadhar))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('There exists an account already with the given phone number or Aadhar number.', 'error')
            return redirect(url_for('register_laborer'))
        
        def generate_unique_id():
            while True:
                laborer_id = random.randint(10000000, 99999999)  # Generate a random 8-digit number
                cursor.execute('SELECT id FROM laborers WHERE id = ?', (laborer_id,))
                if not cursor.fetchone():  # If ID does not exist, it's unique
                    return laborer_id
        
        laborer_id = generate_unique_id()

        try:
            # Insert new laborer
            cursor.execute('''
INSERT INTO laborers (id, uuid, name, phone, language, aadhar, dob, sex, address, abilities, employment_length, employment_unit, photo, employment_proof, password)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
(laborer_id, laborer_uuid, name, phone, language, aadhar, dob, sex, address, abilities, employment_length, employment_unit, photo_filename, employment_proof_filename, password))


            db.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            flash('Failed to register. Please try again.', 'error')
            return redirect(url_for('register_laborer'))

    return render_template('lregister.html')

@app.route('/register/employer', methods=['GET', 'POST'])
def register_employer():
    assign_missing_uuids()
    
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        language = request.form['language']
        aadhar = request.form['aadhar']
        email = request.form['email']
        dob = request.form['dob']
        sex = request.form['sex']
        address = request.form['address']
        company_name = request.form['company-name']
        company_reg_id = request.form['company-reg']
        abilities_required = ",".join(request.form.getlist('abilities-required'))
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')

        # ✅ Handle license image
        license_image = request.files.get('license_image')
        license_filename = None

        if license_image and allowed_file(license_image.filename):
            filename = secure_filename(license_image.filename)
            license_filename = f"{phone}_{filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], license_filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            license_image.save(save_path)

        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT id FROM employers WHERE phone = ? OR aadhar = ? OR email = ?', (phone, aadhar, email))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('An employer with this phone or Aadhar or Email Address already exists.', 'error')
            return redirect(url_for('register_employer'))

        cursor.execute('''
            INSERT OR IGNORE INTO company (name, reg_id, address)
            VALUES (?, ?, ?)
        ''', (company_name, company_reg_id, address))
        db.commit()

        cursor.execute('SELECT id FROM company WHERE reg_id = ?', (company_reg_id,))
        company = cursor.fetchone()

        if company:
            company_id = company['id']
            employer_uuid = generate_unique_uuid('employers', cursor)

            try:
                cursor.execute('''
                    INSERT INTO employers (uuid, name, phone, email, language, aadhar, dob, sex, address, abilities_required, company_id, password, license)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    employer_uuid, name, phone, email, language, aadhar, dob, sex, address, abilities_required, company_id, password, license_filename
                ))

                db.commit()
                flash('Employer registered successfully!', 'success')
                return redirect(url_for('login'))

            except sqlite3.IntegrityError:
                flash('Failed to register employer. Please try again.', 'error')
                return redirect(url_for('register_employer'))

        else:
            flash('Company registration failed.', 'error')
            return redirect(url_for('register_employer'))

    return render_template('eregister.html')



@app.route('/login', methods=['POST', 'GET'])
def login():
    messages = get_flashed_messages(with_categories=True)
    if request.method == 'GET':
        return render_template('login.html',  messages=messages)
    
    else:
        password = request.form['password']
        user_role = request.form['user_role']
        db = get_db()
        cursor = db.cursor()
        
        
        
        
        if user_role == 'laborer':
            identifier = request.form['phone']

            if identifier.lower().startswith('ml'):
                try:
                    uuid = int(identifier[2:])
                    cursor.execute('SELECT * FROM laborers WHERE uuid = ?', (uuid,))
                except ValueError:
                    return render_template('login.html', error="Invalid laborer UUID format!", messages=messages)
            else:
                cursor.execute('SELECT * FROM laborers WHERE phone = ?', (identifier,))
        
        else:  # employer
            identifier = request.form['company-id']

            if identifier.lower().startswith('emp'):
                try:
                    uuid = int(identifier[3:])
                    cursor.execute('SELECT * FROM employers WHERE uuid = ?', (uuid,))
                except ValueError:
                    return render_template('login.html', error="Invalid employer UUID format!", messages=messages)
            else:
                cursor.execute('''
                    SELECT employers.* FROM employers
                    JOIN company ON employers.company_id = company.id
                    Where employers.phone = ?
                ''', (identifier,))

        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_role'] = user_role
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials!", messages=messages)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        email = request.form['email']

        cursor.execute("SELECT * FROM employers WHERE email = ?", (email,))
        employer = cursor.fetchone()

        if employer:
            otp = str(random.randint(100000, 999999))
            session['otp'] = otp
            session['reset_email'] = email

            # Send OTP
            msg = MIMEText(f'Your OTP for password reset is: {otp}')
            msg['Subject'] = 'OTP for Password Reset'
            msg['From'] = formataddr(('Admin', 'neilthedev05@gmail.com'))
            msg['To'] = email

            try:
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login('neilthedev05@gmail.com', 'umzb gufm kawt edee')
                    server.send_message(msg)
                flash('OTP sent to your email.', 'success')
                return redirect(url_for('verify_otp'))
            except Exception as e:
                flash(f'Error sending email: {str(e)}', 'error')
        else:
            flash('Email not found.', 'error')
    return render_template('forgot_password.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if entered_otp == session.get('otp'):
            if new_password == confirm_password:
                db = get_db()
                cursor = db.cursor()
                password = generate_password_hash(request.form['new_password'], method='pbkdf2:sha256')
                cursor.execute("UPDATE employers SET password = ? WHERE email = ?", 
                               (password, session['reset_email']))
                db.commit()
                session.pop('otp', None)
                session.pop('reset_email', None)
                flash('Password reset successfully.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Passwords do not match.', 'error')
        else:
            flash('Invalid OTP.', 'error')
    return render_template('verify_otp.html')



@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    if session['user_role'] == 'employer':
        # Get employer details separately
        cursor.execute('''
            SELECT employers.*, company.name AS company_name, company.reg_id AS company_reg_id
            FROM employers
            JOIN company ON employers.company_id = company.id
            WHERE employers.id = ?
        ''', (session['user_id'],))
        
        employer = cursor.fetchone()

        if not employer:
            return "Employer not found", 404

        # Get employer's posted jobs
        cursor.execute('''
            SELECT jobs.*
            FROM jobs
            WHERE company_id = ?
        ''', (employer['company_id'],))
        
        jobs = cursor.fetchall()

        # Pass both employer details and jobs to the template
        return render_template('dashboard.html', user=employer, jobs=jobs, role='employer')

    else:
        # For laborers
        cursor.execute("SELECT * FROM laborers WHERE id = ?", (session['user_id'],))
        laborer = cursor.fetchone()

        if not laborer:
            return "Laborer not found", 404

        return render_template('dashboard.html', user=laborer, role='laborer')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/offerjob', methods=['GET', 'POST'])
def offer_job():
    if 'user_id' not in session or session['user_role'] != 'employer':
        flash('You must be logged in as a employer to offer jobs.', 'error')
        return redirect(url_for('login')) 

    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        job_title = request.form['title']
        location = request.form['location']
        work_start = request.form['work-start']
        work_end = request.form['work-end']
        duration_start = request.form['duration-start']
        duration_end = request.form['duration-end']
        description = request.form['description']
        salary = request.form['salary']

        cursor.execute('''
            SELECT company_id FROM employers
            WHERE id = ?
        ''', (session['user_id'],))
        company = cursor.fetchone()

        if company:
            company_id = company['company_id']
            
            cursor.execute('''
                INSERT INTO jobs (company_id, job_title, location, work_start, work_end, duration_start, duration_end, description, salary, posted_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (company_id, job_title, location, work_start, work_end, duration_start, duration_end, description, salary, session['user_id']))
            
            db.commit()

            return redirect(url_for('dashboard')) 

    return render_template('offerjob.html')

@app.route('/grievance', methods=['GET', 'POST'])
def grievance():
    if 'user_id' not in session or session['user_role'] != 'laborer':
        flash('You must be logged in as a laborer to file a grievance.', 'error')
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    
    cursor.execute('SELECT id, name FROM company')
    companies = cursor.fetchall()

    if request.method == 'POST':
        company_id = request.form.get('company')
        issues = ', '.join(request.form.getlist('issues'))
        complaint = request.form.get('complaint')

        if not issues:
            flash('Please select at least one grievance issue.', 'error')
            return redirect(url_for('grievance'))

        if not complaint:
            flash('Complaint field cannot be empty.', 'error')
            return redirect(url_for('grievance'))

        
        cursor.execute('''
            SELECT e.id
            FROM employment e
            JOIN jobs j ON e.job_id = j.id
            WHERE e.laborer_id = ? AND j.company_id = ?
        ''', (session['user_id'], company_id))

        employment_record = cursor.fetchone()

        if not employment_record:
            flash('You have not worked for this company.', 'error')
            return redirect(url_for('grievance'))

        
        cursor.execute('''
            INSERT INTO grievances (company_id, user_id, issues, complaint)
            VALUES (?, ?, ?, ?)
        ''', (company_id, session['user_id'], issues, complaint))

        db.commit()
        flash('Grievance submitted successfully!', 'success')
        return redirect(url_for('view_grievance_status'))

    return render_template('grievance.html', companies=companies)

@app.route('/grievances/status')
def view_grievance_status():
    if 'user_id' not in session or session['user_role'] != 'laborer':
        flash('You must be logged in as a laborer to view grievances.', 'error')
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT g.id, g.issues, g.complaint, g.created_at, g.resolved,
               g.admin_reply, c.name AS company_name
        FROM grievances g
        JOIN company c ON g.company_id = c.id
        WHERE g.user_id = ?
        ORDER BY g.created_at DESC
    ''', (session['user_id'],))

    grievances = cursor.fetchall()

    return render_template('grievance_status.html', grievances=grievances)


@app.route('/searchjobs', methods=['GET', 'POST'])
def search_jobs():
    if 'user_id' not in session or session['user_role'] != 'laborer':
        flash('You must be logged in as a laborer to search for jobs.', 'error')
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()
    
    laborer_id = session['user_id']  # Get logged-in user ID

    # Get search parameters from request
    job_title = request.form.get('job-title', '').strip()
    location = request.form.get('location', '').strip()
    start_date = request.form.get('start-date', '').strip()
    end_date = request.form.get('end-date', '').strip()
    work_start = request.form.get('work-start', '').strip()
    work_end = request.form.get('work-end', '').strip()

    # Base SQL query to fetch job listings, excluding jobs already applied for
    query = '''
    SELECT j.id, j.job_title, j.location, j.work_start, j.work_end, 
       j.duration_start, j.duration_end, j.description, j.salary,
       c.name AS company_name
        FROM jobs j
        JOIN company c ON j.company_id = c.id
        LEFT JOIN job_applications ja ON j.id = ja.job_id AND ja.laborer_id = ?
        WHERE ja.id IS NULL
        AND DATE(j.duration_start) >= DATE(?)
        AND NOT EXISTS (
            SELECT 1
            FROM job_applications ja2
            JOIN jobs aj ON ja2.job_id = aj.id
            WHERE ja2.laborer_id = ?
            AND ja2.status = 'Accepted'
            AND (
                DATE(j.duration_start) <= DATE(aj.duration_end) AND
                DATE(j.duration_end) >= DATE(aj.duration_start)
            )
)

    '''
    
    today_date = datetime.date.today().strftime('%Y-%m-%d')
    params = [laborer_id, today_date, laborer_id]

    # Apply search filters dynamically
    # Apply search filters dynamically
    if job_title:
        query += " AND j.job_title LIKE ?"
        params.append(f"%{job_title}%")

    if location:
        query += " AND j.location LIKE ?"
        params.append(f"%{location}%")

    if start_date and not end_date:
        print(f"Received Start Date: {start_date}")
        query += " AND DATE(j.duration_start) >= DATE(?)"
        params.append(start_date)

    if end_date and not start_date:
        print(f"Received End Date: {end_date}")
        query += " AND DATE(j.duration_end) <= DATE(?)"
        params.append(end_date)
    
    if start_date and end_date:
        if start_date > end_date:
            flash("Start date cannot be after the end date.", "error")
        else:
            query += " AND duration_start >= ? AND duration_end <= ?"
            params.extend([start_date, end_date])

    if work_start:
        query += " AND TIME(j.work_start) >= TIME(?)"
        params.append(work_start)

    if work_end:
        query += " AND TIME(j.work_end) <= TIME(?)"
        params.append(work_end)

    if end_date:
        if end_date < today_date:
            flash("End date cannot be before today.", "error")
    # Execute query
    cursor.execute(query, params)
    jobs = cursor.fetchall()

    # If it's an AJAX request, return JSON data
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
         return jsonify({
            "jobs": [dict(job) for job in jobs],
            "flash_messages": get_flashed_messages(with_categories=True)  # Return flash messages
        })

    return render_template('searchjobs.html', jobs=jobs)



@app.route('/apply/<int:job_id>')
def apply_job(job_id):
    if 'user_id' not in session or session['user_role'] != 'laborer':
        flash('You must be logged in as a laborer to apply for jobs.', 'error')
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    laborer_id = session['user_id']
    cursor.execute('SELECT id FROM job_applications WHERE laborer_id = ? AND job_id = ?', (laborer_id, job_id))
    existing_application = cursor.fetchone()

    if existing_application:
        flash('You have already applied for this job.', 'info')
        return redirect(url_for('search_jobs'))

    cursor.execute('INSERT INTO job_applications (laborer_id, job_id) VALUES (?, ?)', (laborer_id, job_id))
    db.commit()

    flash('Application submitted successfully!', 'success')
    return redirect(url_for('search_jobs'))

@app.route('/track', methods=['GET'])
def track_applications():
    if 'user_id' not in session or session['user_role'] != 'laborer':
        flash('You must be logged in as a laborer to track applications.', 'error')
        return redirect(url_for('login'))

    laborer_id = session['user_id']
    db = get_db()
    cursor = db.cursor()

    query = '''
        SELECT ja.id AS application_id, j.job_title, j.location, 
               j.duration_start, j.duration_end, 
               j.work_start, j.work_end, j.salary, 
               c.name AS company_name, ja.status, ja.applied_at,
               j.id as job_id
        FROM job_applications ja
        JOIN jobs j ON ja.job_id = j.id
        JOIN company c ON j.company_id = c.id
        WHERE ja.laborer_id = ?
        ORDER BY ja.applied_at DESC
    '''
    
    cursor.execute(query, (laborer_id,))
    applications = cursor.fetchall()

    # Categorize applications
    successful_apps = [dict(app) for app in applications if app['status'] == 'Accepted']
    unsuccessful_apps = [dict(app) for app in applications if app['status'] in ['Rejected', 'Withdrawn']]
    pending_apps = [dict(app) for app in applications if app['status'] == 'Pending']

    return render_template(
        'track.html',
        successful_apps=successful_apps,
        unsuccessful_apps=unsuccessful_apps,
        pending_apps=pending_apps
    )
    

@app.route('/remove_application/<int:application_id>', methods=['POST'])
def remove_application(application_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM job_applications WHERE id = ?", (application_id,))
    db.commit()
    return jsonify({"success": True})


@app.route("/applications")
def view_applications():
    if "user_id" not in session or session.get("user_role") != "employer":
        return redirect(url_for("home"))

    employer_id = session["user_id"]
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """SELECT ja.id AS application_id, ja.status,
                  j.job_title, j.location,
                  l.name AS laborer_name, l.phone AS contact,
                  l.abilities AS skills, l.id AS laborer_id
           FROM job_applications AS ja
           JOIN jobs AS j ON ja.job_id = j.id
           JOIN laborers AS l ON ja.laborer_id = l.id
           WHERE j.company_id = (SELECT company_id FROM employers WHERE id = ?)""",
        (employer_id,)
    )

    applications = cursor.fetchall()

    # Group applications by job title
    grouped_applications = {}
    for app in applications:
        job_title = app['job_title']
        if job_title not in grouped_applications:
            grouped_applications[job_title] = []
        grouped_applications[job_title].append(app)

    return render_template("apps.html", grouped_applications=grouped_applications)



@app.route("/update_application", methods=["POST"])
def update_application():
    data = request.json
    application_id = data.get("application_id")
    new_status = data.get("status")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("UPDATE job_applications SET status = ? WHERE id = ?", (new_status, application_id))
    
    if new_status == "Accepted":
        # Fetch laborer_id, job_id, and start_date, end_date from the job_applications and jobs table
        cursor.execute("""
            SELECT ja.laborer_id, ja.job_id, j.duration_start, j.duration_end
            FROM job_applications ja
            JOIN jobs j ON ja.job_id = j.id
            WHERE ja.id = ?
        """, (application_id,))
        
        application = cursor.fetchone()
        
        if application:
            laborer_id, job_id, duration_start, duration_end = application
            # Insert the record into the employment table with start and end date from the job
            cursor.execute(
                "INSERT INTO employment (laborer_id, job_id, start_date, end_date) VALUES (?, ?, ?, ?)",
                (laborer_id, job_id, duration_start, duration_end)
            )
    
    db.commit()

    return jsonify({"message": "Application status updated successfully!"})


@app.route('/contact_employer/<int:job_id>', methods=['GET', 'POST'])
def contact_employer(job_id):
    db = get_db()
    cursor = db.cursor()
    print(job_id)
    # Fetch job details and employer info
    cursor.execute(''' 
        SELECT jobs.id, jobs.job_title, jobs.description, jobs.salary, jobs.company_id, 
               employers.id AS employer_id, employers.name, employers.phone, employers.email
        FROM jobs
        JOIN employers ON jobs.posted_by = employers.id  -- Join directly using the posted_by column
        WHERE jobs.id = ? 
    ''', (int(job_id),))

    job = cursor.fetchone()

    if not job:
        flash("Job not found.", "error")
        return redirect(url_for('search_jobs'))

    if request.method == "POST":
        laborer_id = session.get('user_id')
        message = request.form['message']

        if not laborer_id:
            flash("You must be logged in as a laborer to contact an employer.", "error")
            return redirect(url_for('login'))

        # Create a conversation ID that also identifies the context (job-based message)
        cid = f'laborer_{laborer_id}_employer_{job["employer_id"]}_job_{job_id}'

        cursor.execute(''' 
            INSERT INTO messages (laborer_id, employer_id, message, sender_type, conversation_id, job_id)
            VALUES (?, ?, ?, 'laborer', ?, ?)
        ''', (laborer_id, job['employer_id'], message, cid, job_id))
        db.commit()

        # flash("Your message has been sent to the employer!", "success")
        return redirect(url_for('view_messages'))

    return render_template('contact_employer.html', job=job)



@app.route('/contact_laborer/<int:application_id>', methods=['GET', 'POST'])
def contact_laborer(application_id):
    db = get_db()
    cursor = db.cursor()

    # Fetch job and laborer details based on the application_id
    cursor.execute(''' 
        SELECT jobs.id AS job_id, jobs.job_title, jobs.description, jobs.salary, jobs.company_id,
               laborers.id AS laborer_id, laborers.name AS laborer_name, laborers.phone AS laborer_phone
        FROM job_applications
        JOIN jobs ON job_applications.job_id = jobs.id
        JOIN laborers ON job_applications.laborer_id = laborers.id
        WHERE job_applications.id = ?
    ''', (application_id,))

    job = cursor.fetchone()

    if not job:
        flash("Application not found or application is not accepted.", "error")
        return redirect(url_for('view_applications'))

    if request.method == "POST":
        employer_id = session.get('user_id')  # Get logged-in employer
        message = request.form['message']

        if not employer_id:
            flash("You must be logged in as an employer to contact a laborer.", "error")
            return redirect(url_for('login'))

        # Create a conversation ID that also identifies the context (application-based message)
        cid = f'laborer_{job["laborer_id"]}_employer_{employer_id}_application_{application_id}'

        cursor.execute(''' 
            INSERT INTO messages (laborer_id, employer_id, message, sender_type, conversation_id, application_id)
            VALUES (?, ?, ?, 'employer', ?, ?)
        ''', (job['laborer_id'], employer_id, message, cid, application_id))
        db.commit()

        # flash("Your message has been sent to the laborer!", "success")
        return redirect(url_for('view_messages'))

    return render_template('contact_laborer.html', job=job)



@app.route('/messages', methods=['GET'])
def view_messages():
    if 'user_id' not in session:
        flash("You need to be logged in to view messages.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_type = session['user_role']  # Determine if laborer or employer

    db = get_db()
    cursor = db.cursor()

    if user_type == "laborer":
        cursor.execute('''
        SELECT m.conversation_id, m.laborer_id, m.employer_id, e.name AS employer_name, 
               m.message, m.timestamp, m.sender_type, m.job_id, m.application_id,
               j.job_title, c.name AS company_name
        FROM messages m
        JOIN employers e ON m.employer_id = e.id
        LEFT JOIN jobs j ON m.job_id = j.id  -- Join jobs table to get job title
        LEFT JOIN company c ON j.company_id = c.id  -- Join company table to get employer company name
        WHERE m.laborer_id = ?
        ORDER BY m.timestamp DESC
        ''', (user_id,))

    else:  # For Employers
        cursor.execute('''
        SELECT m.conversation_id, m.laborer_id, m.employer_id, l.name AS laborer_name, 
               m.message, m.timestamp, m.sender_type, m.job_id, m.application_id,
               j.job_title, c.name AS company_name
        FROM messages m
        JOIN laborers l ON m.laborer_id = l.id
        LEFT JOIN jobs j ON m.job_id = j.id  -- Join jobs table to get job title
        LEFT JOIN company c ON j.company_id = c.id  -- Join company table to get company name
        WHERE m.employer_id = ?
        ORDER BY m.timestamp DESC
        ''', (user_id,))

    messages = cursor.fetchall()

    # Group messages by conversation_id
    conversations = {}
    for msg in messages:
        conversation_id = msg["conversation_id"]
        
        # Check if the conversation_id is already in the dictionary
        if conversation_id not in conversations:
            # Determine if it's job-based or application-based
            job_id = msg["job_id"]
            application_id = msg["application_id"]

            # If application_id is missing but job_id is present, try to fetch it
            if user_type == "laborer" and not application_id and job_id:
                cursor.execute('''
                    SELECT id FROM job_applications
                    WHERE laborer_id = ? AND job_id = ?
                ''', (user_id, job_id))
                application = cursor.fetchone()
                if application:
                    application_id = application["id"]

            # Fetch job title and company name
            if job_id:
                cursor.execute('''
                    SELECT j.job_title, c.name AS company_name
                    FROM jobs j
                    JOIN company c ON j.company_id = c.id
                    WHERE j.id = ?
                ''', (job_id,))
                job_details = cursor.fetchone()
                job_title = job_details["job_title"] if job_details else "N/A"
                company_name = job_details["company_name"] if job_details else "N/A"
            else:
                job_id = msg["job_id"]
                application_id = msg["application_id"]
                cursor.execute('''
                SELECT j.job_title, c.name AS company_name
                FROM job_applications ja
                JOIN jobs j ON ja.job_id = j.id
                JOIN company c ON j.company_id = c.id
                WHERE ja.id = ?
                ''', (application_id,))
                job_details = cursor.fetchone()
                job_title = job_details["job_title"] if job_details else "N/A"
                company_name = job_details["company_name"] if job_details else "N/A"

            
            # Determine the participant's name
            participants = msg["employer_name"] if user_type == "laborer" else msg["laborer_name"]
            
            conversations[conversation_id] = {
                "participants": participants,
                "messages": [],
                "job_id": job_id,
                "application_id": application_id,
                "job_title": job_title,
                "company_name": company_name
            }

        
        # Append the message to the relevant conversation
        conversations[conversation_id]["messages"].append(dict(msg))

    return render_template('messages.html', conversations=conversations, user_type=user_type)




import logging

@app.route('/send_message/<conversation_id>', methods=['POST'])
def send_message(conversation_id):
    if 'user_id' not in session:
        flash("You need to be logged in to send a message.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_type = session['user_role']
    message = request.form['message']

    # Debug log
    logging.debug(f"Message received: {message}, User: {user_id}, Role: {user_type}")

    # Extract laborer_id, employer_id, and job/application information from conversation_id
    try:
        parts = conversation_id.split('_')
        laborer_id = int(parts[1])  # Laborer ID should be the second part
        employer_id = int(parts[3])  # Employer ID should be the fourth part
        conversation_type = parts[4]  # "job" or "application"
        conversation_id = "_".join(parts[:6])  # Rebuild the base conversation ID
        print(parts, conversation_id)
    except ValueError:
        flash("Invalid conversation ID format.", "error")
        return redirect(url_for('view_messages'))

    # Ensure the user is part of the conversation
    if user_type == 'laborer' and laborer_id != user_id:
        flash("You are not authorized to send a message in this conversation.", "error")
        return redirect(url_for('view_messages'))
    if user_type == 'employer' and employer_id != user_id:
        flash("You are not authorized to send a message in this conversation.", "error")
        return redirect(url_for('view_messages'))

    # Insert the message into the database
    db = get_db()
    cursor = db.cursor()

    job_id = None
    application_id = None

    # Check if the conversation is related to a job or application
    if conversation_type == 'job':
        job_id = int(parts[5])  # Extract job_id if it's a job conversation
    elif conversation_type == 'application':
        application_id = int(parts[5])  # Extract application_id if it's an application conversation

    # If both job_id and application_id are present, raise an error
    if job_id and application_id:
        flash("A message can only be associated with either a job or an application, not both.", "error")
        return redirect(url_for('view_messages'))

    # If neither job_id nor application_id is set, raise an error
    if not job_id and not application_id:
        flash("You must specify either a job or an application for the conversation.", "error")
        return redirect(url_for('view_messages'))

    # Insert the message into the database based on the user type
    if user_type == 'laborer':
        cursor.execute(''' 
            INSERT INTO messages (laborer_id, employer_id, message, sender_type, conversation_id, job_id, application_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, employer_id, message, 'laborer', conversation_id, job_id, application_id))
    elif user_type == 'employer':
        cursor.execute(''' 
            INSERT INTO messages (laborer_id, employer_id, message, sender_type, conversation_id, job_id, application_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (laborer_id, user_id, message, 'employer', conversation_id, job_id, application_id))

    db.commit()

    # Log the database insertion
    logging.debug(f"Message sent: {message} by {user_type}")


    return jsonify({
        "message": message,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sender_type": user_type
    })

@app.route('/view_applications/<int:job_id>', methods=['GET'])
def show_job_applications(job_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    # Get job details for the job_id (just in case you want to show job info on the applications page)
    cursor.execute('''
        SELECT jobs.job_title, jobs.location, company.name AS company_name
        FROM jobs
        JOIN company ON jobs.company_id = company.id
        WHERE jobs.id = ?
    ''', (job_id,))
    job = cursor.fetchone()

    if not job:
        return "Job not found", 404

    # Get applications for the selected job
    cursor.execute('''
        SELECT ja.id AS application_id, laborers.name AS laborer_name, ja.status
        FROM job_applications ja
        JOIN laborers ON ja.laborer_id = laborers.id
        WHERE ja.job_id = ?
    ''', (job_id,))
    applications = cursor.fetchall()

    # Render the view with the job and its applications
    return render_template('view_applications.html', job=job, applications=applications)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    user_id = session['user_id']
    role = session['user_role']

    if role == 'laborer':
        cursor.execute("SELECT * FROM laborers WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if request.method == 'POST':
            fields = ['name', 'phone', 'language', 'address', 'dob', 'sex', 'abilities', 'employment_length', 'employment_unit']
            updates = [request.form.get(field, '') for field in fields]

            # Handling photo and employment_proof
            new_photo = request.files.get('photo')
            new_employment_proof = request.files.get('employment_proof')

            # Only update if a new file is uploaded, otherwise keep the current file
            if new_photo and allowed_file(new_photo.filename):
                photo_filename = secure_filename(new_photo.filename)
                new_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
                updates.append(photo_filename)
            else:
                updates.append(user['photo'])  # Keep existing photo filename

            if new_employment_proof and allowed_file(new_employment_proof.filename):
                employment_proof_filename = secure_filename(new_employment_proof.filename)
                new_employment_proof.save(os.path.join(app.config['UPLOAD_FOLDER'], employment_proof_filename))
                updates.append(employment_proof_filename)
            else:
                updates.append(user['employment_proof'])  # Keep existing employment proof filename

            # Only update if any field has changed
            if any(user[field] != val for field, val in zip(fields + ['photo', 'employment_proof'], updates)):
                cursor.execute(f'''
                    UPDATE laborers SET {', '.join(f"{field} = ?" for field in fields + ['photo', 'employment_proof'])}
                    WHERE id = ?
                ''', (*updates, user_id))
                db.commit()
                return redirect(url_for('dashboard'))
            else:
                flash('No changes detected in your profile.', 'info')

        return render_template('edit_profile.html', user=user, role='laborer')

    elif role == 'employer':
        cursor.execute(''' 
            SELECT employers.*, company.name AS company_name, company.reg_id, company.id AS company_id
            FROM employers
            JOIN company ON employers.company_id = company.id
            WHERE employers.id = ? 
        ''', (user_id,))
        user = cursor.fetchone()

        if request.method == 'POST':
            fields = ['name', 'phone', 'language', 'dob', 'sex', 'address', 'abilities_required']
            updates = [request.form.get(field, '') for field in fields]

            # Update company details if changed
            new_company_name = request.form.get('company_name')
            new_reg_id = request.form.get('company_reg')

            if new_company_name != user['company_name'] or new_reg_id != user['reg_id']:
                cursor.execute('''
                    UPDATE company SET name = ?, reg_id = ? WHERE id = ?
                ''', (new_company_name, new_reg_id, user['company_id']))
                db.commit()

            # Only update employer table if needed
            if any(user[field] != val for field, val in zip(fields, updates)):
                cursor.execute(f'''
                    UPDATE employers SET {', '.join(f"{field} = ?" for field in fields)}
                    WHERE id = ?
                ''', (*updates, user_id))
                db.commit()
                return redirect(url_for('dashboard'))
            else:
                flash('No changes detected in your profile.', 'info')

    return render_template('edit_profile.html', user=user, role='employer')





@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)


