from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "amongs"

# upload folder path setup
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
# ensure the directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# token system
tokens = {}

def generate_token():
    return str(uuid.uuid4())

# expiry system
def store_token(token, expiry=60):
    expiration_time = datetime.now() + timedelta(minutes=expiry)
    tokens[token] = {"valid": True, "expires_at": expiration_time}

def validate_token(token):
    token_info = tokens.get(token)
    
    if token_info and token_info["valid"]:
        # see if token expired
        if datetime.now() < token_info["expires_at"]:
            return True
    return False

@app.route('/password', methods=['GET', 'POST'])
def password_page():
    if request.method == 'POST':
        password = request.form.get('password')
        
        # password validation here
        if password == '123':
            token = generate_token()
            store_token(token)
            return redirect(url_for("plan_creator", token=token))
        else:
            return "Invalid password", 403
    
    return render_template('password.html')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/exam_finder")
def exam_finder():
    return render_template("finder.html")

@app.route("/search_test", methods=['POST', "GET"])
def search_test():
    stu_class = request.form.get('class')
    subject = request.form.get('subject').lower()

    conn = sqlite3.connect('exam.db')
    cursor = conn.cursor()

    query = '''
    SELECT test_name, subject, date, location, start_time, end_time, description, image
    FROM exams
    WHERE 1=1
    '''

    params = []

    if stu_class:
        query += " AND classes LIKE ?"
        params.append(f"%{stu_class}%")

    if subject:
        query += " AND lower(subject) = ?"
        params.append(subject)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return render_template("finder.html", exams=results)


@app.route("/plan_creator")
def plan_creator():
    token = request.args.get('token')
    
    if token and validate_token(token):
        form_data = session.get('form_data', {})
        return render_template('creator.html', token=token, form_data=form_data)
    else:
        return "Invalid or expired token", 403
    
@app.route("/submit_form", methods=['POST'])
def submit_form():
    error = 0

    # retrieve token from form
    token = request.form.get('token')

    session['form_data'] = {
        'test_name': request.form.get('test_name'),
        'subject': request.form.get('subject'),
        'classes': request.form.get('classes'),
        'location': request.form.get('location'),
        'date': request.form.get('date'),
        'start_time': request.form.get('start_time'),
        'end_time': request.form.get('end_time'),
        'description': request.form.get('description'),
    }
    test_name = request.form.get('test_name')
    subject = request.form.get('subject')
    classes = request.form.get('classes')
    location = request.form.get('location')

    # date validation
    date = request.form.get('date')

    exam_date = datetime.strptime(date, '%Y-%m-%d').date()
    today = datetime.today().date()

    if exam_date < today:
        flash('The exam date cannot be earlier than today.', category='error')
        error = 1

    # time validation
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')

    format_str = '%H:%M'
    start_time2 = datetime.strptime(start_time, format_str).time()
    end_time2 = datetime.strptime(end_time, format_str).time()

    if start_time2 > end_time2:
        flash('Start time cannot be later than end time', category='error')
        error = 1

    description = request.form.get('description')

    # Image file validation
    if 'image_file' in request.files:
        file = request.files['image_file']

        if file.filename == '':
            flash('No selected file', category='info')
            
        elif file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            image_url = url_for('static', filename='uploads/' + filename, _external=True)
        else:
            flash('Invalid file type. Please upload an image file (JPG, JPEG, PNG, or GIF).', category='error')
            error = 1
    
    if error == 1:
        return redirect(url_for('plan_creator', token=token,))
    try:
        conn = sqlite3.connect('exam.db')
        cursor = conn.cursor()
        # avoid using f string to prevent illegal sql injection which can cause very very bad stuff
        cursor.execute('''
            INSERT INTO exams (test_name, classes, subject, location, date, start_time, end_time, description, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (test_name, classes, subject, location, date, start_time, end_time, description, image_url))

        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        render_template("creator.html", success="Sorry, an error has occured", token=token)
    finally:
        conn.close()

    return render_template("creator.html", success="Plan successfully created", token=token)

if __name__ == '__main__':
  app.run(debug=True, port=5000)
