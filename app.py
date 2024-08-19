from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import uuid

app = Flask(__name__)
app.secret_key = "amongs"

# Upload folder path setup
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Token system
tokens = {}

def generate_token():
    return str(uuid.uuid4())

def store_token(token):
    tokens[token] = True

@app.route('/generate-token')
def generate_access_token():
    token = generate_token()
    store_token(token)
    return f"Access your page here: {url_for('plan_creator', token=token, _external=True)}"

def validate_token(token):
    if token in tokens and tokens[token]:
        # invalidate the token
        tokens[token] = False
        return True
    return False

@app.route('/password', methods=['GET', 'POST'])
def password_page():
    if request.method == 'POST':
        password = request.form.get('password')
        
        # password thing here
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

@app.route("/search_test", methods=['POST'])
def search_test():
    stu_class = request.form.get('class')
    subject = (request.form.get('subject')).lower()

    conn = sqlite3.connect('exam.db')
    cursor = conn.cursor()
    
    query = '''
    SELECT test_name, subject, date, location, start_time, end_time, description
    FROM exams
    WHERE 1=1
    '''
    
    # easy way to add paramater values and sub them into the placeholders at the end
    # prevents the sql injection(illegal stuff) things from happening since i'm not using a f string anymore
    params = []
    
    if stu_class:
        query += " AND classes LIKE ?"
        params.append(f"%{stu_class}%")
    
    # so that subject is not case sensitive
    if subject:
        query += "AND lower(subject) = ?"
        params.append(subject)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return render_template("finder.html", exams=results)

@app.route("/plan_creator")
def plan_creator():
    token = request.args.get('token')
    
    if token and validate_token(token):
        return render_template('creator.html')
    else:
        return "Invalid or expired token", 403

@app.route("/submit_form", methods=['POST'])
def submit_form():
    test_name = request.form.get('test_name')
    subject = request.form.get('subject')
    classes = request.form.get('classes')
    location = request.form.get('location')
    date = request.form.get('date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    description = request.form.get('description')

    try:
        conn = sqlite3.connect('exam.db')
        cursor = conn.cursor()

        # avoid using f string to prevent illegal sql injection which can cause very very bad stuff
        cursor.execute('''
            INSERT INTO exams (test_name, classes, subject, location, date, start_time, end_time, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        ''', (test_name, classes, subject, location, date, start_time, end_time, description))

        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        render_template("creator.html", success="Sorry, an error has occured")
    finally:
        conn.close()

    return render_template("creator.html", success="Plan successfully created")

@app.route('/file_upload', methods=['POST'])
def file_upload():
    if 'image_file' not in request.files:
        flash('No file part', category='error')
        return redirect(url_for("plan_creator"))

    file = request.files['image_file']

    if file.filename == '':
        flash('No selected file', category='error')
        return redirect(url_for("plan_creator"))

    # Image file types
    if file and (file.filename.endswith('.jpg') or 
                file.filename.endswith('.jpeg') or 
                file.filename.endswith('.png') or 
                file.filename.endswith('.gif')):
        filename = file.filename

        # uploading it into the uploads folder
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        flash('Image uploaded successfully', category='success')
    else:
        # handling other files
        flash('Invalid file type. Please upload an image file (JPG, JPEG, PNG, or GIF).', category='error')

    return redirect(url_for("plan_creator"))

if __name__ == '__main__':
  app.run(debug=True, port=5000)
