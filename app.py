from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import csv
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
        # Invalidate the token
        tokens[token] = False
        return True
    return False

@app.route('/password', methods=['GET', 'POST'])
def password_page():
    if request.method == 'POST':
        password = request.form.get('password')
        
        # Example password check (replace with your own logic)
        if password == 'verysneakypassword123':
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
    subject = request.form.get('subject')

    conn = sqlite3.connect('exam.db')
    cursor = conn.cursor()
    
    query = '''
    SELECT test_name, subject, date, location, start_time, end_time, description
    FROM exams
    WHERE 1=1
    '''
    
    # Easy way to add paramater values and sub them into the placeholders at the end
    params = []
    
    if stu_class:
        query += " AND classes = ?"
        params.append(stu_class)
    
    if subject:
        query += " AND subject = ?"
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
    if 'csv_file' not in request.files:
        flash('No file part', category='error')
        return redirect(url_for("plan_creator"))

    file = request.files['csv_file']

    if file.filename == '':
        flash('No selected file', category='error')
        return redirect(url_for("plan_creator"))

    if file and file.filename.endswith('.csv'):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        flash('File uploaded successfully', category='success')

        conn = sqlite3.connect('exam.db')
        cursor = conn.cursor()
        try:
            # Open the file for reading
            with open(filepath, 'r') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    stu_index = row['Stu_index']
                    stu_name = row['Stu_Name']
                    class_ = row['Class']
                    subject = row['Subject']
                    
                    # Inserting into students table
                    cursor.execute('''
                    INSERT INTO students (stu_index, stu_name, class, subject)
                    VALUES (?, ?, ?, ?)
                    ''', (stu_index, stu_name, class_, subject))
                
            # Commit the transaction after processing all rows
            conn.commit()

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            flash('An error occurred while processing the file.', category='error')
        except Exception as e:
            print(f"General error: {e}")
            flash('An unexpected error occurred.', category='error')
        finally:
            conn.close()

    else:
        flash('Invalid file type. Please upload a CSV file.', category='error')

    return redirect(url_for("plan_creator"))

if __name__ == '__main__':
  app.run(debug=True, port=5000)
