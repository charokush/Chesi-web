from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import Student, News, Teacher, Assignments, Photo, File
from datetime import datetime
import json
import os
from datetime import datetime
from models import db
from flask_migrate import Migrate
from functools import wraps
from werkzeug.utils import secure_filename
import os
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'PassWord@123'  # Replace with a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
UPLOAD_FOLDER = os.path.join('static', 'images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

UPLOAD_FOLDERS = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDERS'] = UPLOAD_FOLDERS


class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255))
    description = db.Column(db.String(255))
    note = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, title, image, description, note):
        self.title = title
        self.image = image
        self.description = description
        self.note = note

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255))
    teacher = db.Column(db.String(255))
    posts = db.Column(db.Boolean, default=False)
    
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    adm = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    stream = db.Column(db.String(50))

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_no = db.Column(db.String(255))
    name = db.Column(db.String(255))
    classes = db.Column(db.String(255))
    subject1 = db.Column(db.String(255))
    subject2 = db.Column(db.String(255))
    password = db.Column(db.String(255))
    posts = db.Column(db.Boolean)  # Boolean column to store True or False
    department = db.Column(db.String(255))  # Define the 'department' column

    def __init__(self, job_no, name, classes, subject1, subject2, password, posts, department):
        self.job_no = job_no
        self.name = name
        self.classes = classes
        self.subject1 = subject1
        self.subject2 = subject2
        self.password = password
        self.posts = posts
        self.department = department.lower()

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)



class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)

    def __init__(self, description, filename):
        self.description = description
        self.filename = filename



class Assignments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Text, nullable=False)
    subject = db.Column(db.Text, nullable=False)
    teacher_post = db.Column(db.Text, nullable=True)  # This will be automatically populated
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    posts = db.Column(db.Boolean, default=False)

    def __init__(self, level, subject, teacher_post, title, body, posts=False):
        self.level = level
        self.subject = subject.lower()
        self.teacher_post = teacher_post  # Make sure to include this line
        self.title = title
        self.body = body
        self.posts = posts


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    story = db.Column(db.String(500))
    filename = db.Column(db.String(100))


class Memo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    audience = db.Column(db.String(100), nullable=False)

@app.route('/add_student', methods=['POST'])
def add_student():
    if request.method == 'POST':
        adm = request.form['adm']
        name = request.form['name']
        level = request.form['level']
        stream = request.form['stream']
        password = request.form['password']

        # Hash the password using generate_password_hash
        hashed_password = generate_password_hash(password, method='sha256')

        # Check if a student with the same 'adm' value exists
        existing_student = Student.query.filter_by(adm=adm).first()

        if existing_student:
            # Flash an error message if the student with 'adm' exists
            flash('Student with Admission Number already exists', 'error')
        else:
            # Insert a new student with the hashed password
            student = Student(adm=adm, name=name, level=level, stream=stream, password=hashed_password)
            db.session.add(student)
            db.session.commit()
            flash('Student added successfully', 'success')

        return redirect(url_for('admin_dashboard'))


@app.route("/")
def index():
    # Use SQLAlchemy to query the database
    latest_news_posts = News.query.order_by(News.id.desc()).limit(2).all()
    
    return render_template('index.html', news_posts=latest_news_posts)

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Redirect to login page if not logged in\
    else:
        students = Student.query.all()
        return render_template('admin_dashboard.html', students=students)



@app.route('/department')
def department():
    return render_template('department.html')


@app.route('/staff_login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        job_no = request.form['job_no']
        password = request.form['password']

        # Check if a teacher with the given job_no exists
        teacher = Teacher.query.filter_by(job_no=job_no).first()

        if teacher and teacher.password == password:
            # Successful login, store teacher information in session
            session['teacher_id'] = teacher.id
            session['teacher_name'] = teacher.name
            session['teacher_job_no'] = teacher.job_no
            flash('Login successful!', 'success')
            return redirect(url_for('teacher_dashboard'))
        else:
            flash('Login failed. Please check your Job Number and password.', 'danger')

    return render_template('staff_login.html')





@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        adm = request.form['adm']
        password = request.form['password']

        student = Student.query.filter_by(adm=adm).first()

        if student and check_password_hash(student.password, password):
            # Successful login, store user information in session
            session['user_id'] = student.id
            session['user_name'] = student.name

            flash('Login successful!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Login failed. Please check your ADM number and password.', 'danger')

    return render_template('student_login.html')



@app.route("/tutorials")
def tutorials():
    youtube_url = "https://youtube.com/@CHESINGELESECSCHOOL-kc8ru?si=S5qRIXn7ZQYy2UL5"
    return redirect(youtube_url)

@app.route('/teacher_dashboard')
def teacher_dashboard():
    # Check if the teacher is logged in (has a session)
    if 'teacher_name' in session:
        teacher_name = session['teacher_name']
        teacher_job_no = session['teacher_job_no'] 
        assignments = Assignments.query.filter_by(teacher_post=teacher_job_no).all()
        memos = Memo.query.filter_by(audience='teacher').all()
        return render_template('teacher_dashboard.html', teacher_name=teacher_name, teacher_job_no=teacher_job_no, assignments=assignments, memos=memos)
    else:
        # Redirect to the login page if the teacher is not logged in
        flash('You need to log in to access this page.', 'warning')
        return redirect(url_for('staff_login'))

@app.route('/news')
def news_page():
    news_posts = News.query.all()
    return render_template('news.html', news_posts=news_posts)


@app.route('/add_assignment')
def add_assignment():
    if 'teacher_name' in session:
        teacher_job_no = session['teacher_job_no']
        teacher_name = session['teacher_name']
        return render_template('add_assignment.html', teacher_name=teacher_name,teacher_job_no=teacher_job_no)
    else:
        # Redirect to the login page if the teacher is not logged in
        return redirect(url_for('add_assignment'))



@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    news_posts = News.query.all()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        # Create a new news post
        news_post = News(title=title, body=body)
        db.session.add(news_post)
        db.session.commit()

        flash('News added successfully!', 'success')

        return redirect(url_for('news'))

    # Handle GET request (display the form)
    return render_template('add_news.html',news_posts=news_posts)

@app.route('/news')
def news():
    # Query the news table to get all news posts
    news_posts = News.query.all()
    return render_template('your_template.html', news_posts=news_posts)


@app.route('/photos')
def photos():
    if not session.get('logged_in'):
        return redirect(url_for('login'))  
    else:
        uploaded_images = Photo.query.all()
        return render_template('photos.html', uploaded_images=uploaded_images)




@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)

    if file:
        description = request.form['description']
        filename = secure_filename(file.filename)
        
        # Save the uploaded file to the specified directory
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_photo = Photo(description=description, filename=filename)
        db.session.add(new_photo)
        db.session.commit()

        flash('Image uploaded successfully', 'success')
    uploaded_images = Photo.query.all()
    return redirect(url_for('photos',uploaded_images=uploaded_images))




@app.route('/delete_student/<int:student_id>', methods=['GET', 'POST'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    
    if student:
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully', 'success')
    else:
        flash('Student not found', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/about')
def about():
    about_items = About.query.all()
    return render_template('about.html', about_items=about_items)

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('department'))

@app.route('/display_assignment/<int:assignment_id>')
def display_assignment(assignment_id):
    # Assuming you have a database model for assignments
    assignment = Assignments.query.get(assignment_id)

    if assignment:
        return render_template('assignment.html', assignment=assignment)
    else:
        flash('Assignment not found.', 'danger')
        return redirect(url_for('student_dashboard'))



@app.route('/pictures')
def pictures():
    uploaded_images = Photo.query.all()
    return render_template('pictures.html', uploaded_images=uploaded_images)



@app.route('/insert_teacher', methods=['POST'])
def insert_teacher():
    if request.method == 'POST':
        job_no = request.form['job_no']
        name = request.form['name']
        classes = request.form['classes']
        subject1 = request.form['subject1']
        subject2 = request.form['subject2']
        password = request.form['password']
        department = request.form['department']
        posts = request.form['posts']  # Get the value from the hidden input field

        # Convert the 'posts' value to a boolean
        posts = posts == 'true'

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)

        existing_teacher = Teacher.query.filter_by(job_no=job_no).first()

        if existing_teacher:
            flash('Teacher with Job Number already exists', 'error')
        else:
            teacher = Teacher(
                job_no=job_no,
                name=name,
                classes=classes,
                subject1=subject1,
                subject2=subject2,
                password=hashed_password,  # Store the hashed password
                posts=posts,
                department=department
            )

            db.session.add(teacher)
            db.session.commit()
            flash('Teacher added successfully', 'success')
        return redirect(url_for('add_staff'))



# Modify the admin_dashboard route to retrieve teachers
@app.route('/add_staff')
def add_staff():
    teachers = Teacher.query.all()
    
    return render_template('add_staff.html', teachers=teachers)



@app.route('/delete_teacher/<int:teacher_id>', methods=['GET', 'POST'])
def delete_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        db.session.delete(teacher)
        db.session.commit()
        flash('Teacher deleted successfully', 'success')
    else:
        flash('Teacher not found', 'danger')
    return redirect('/add_staff')  # Redirect to the page where the teachers are listed



@app.route("/departments")
def departments():
    return render_template('department.html')

@app.route('/delete_assignment/<int:assignment_id>', methods=['POST'])
def delete_assignment(assignment_id):
    # Check if the teacher is logged in (has a session)
    if 'teacher_job_no' in session:
        teacher_job_no = session['teacher_job_no']

        # Query the assignment with the given assignment_id and teacher_job_no
        assignment = Assignments.query.filter_by(id=assignment_id, teacher_post=teacher_job_no).first()

        if assignment:
            # Delete the assignment from the database
            db.session.delete(assignment)
            db.session.commit()
            flash('Assignment deleted successfully!', 'success')
        else:
            flash('Assignment not found or you do not have permission to delete it.', 'danger')

        return redirect(url_for('teacher_dashboard'))
    else:
        # Redirect to the login page if the teacher is not logged in
        return redirect(url_for('staff_login'))




@app.route('/insert_assignment', methods=['GET', 'POST'])
def insert_assignment():
    if request.method == 'POST':
        level = request.form['level']
        subject = request.form['subject']
        teacher_post = request.form['teacher_post']
        title = request.form['title']
        body = request.form['body']

        # Create a new assignment object
        new_assignment = Assignments(
            level=level,
            subject=subject,
            teacher_post=teacher_post,
            title=title,
            body=body
        )

        # Add the assignment to the database
        db.session.add(new_assignment)
        db.session.commit()

        flash('Assignment added successfully!', 'success')
        return redirect(url_for('teacher_dashboard'))  # Redirect to the teacher dashboard

    return render_template('add_assignment.html')



@app.route('/insert_news', methods=['GET', 'POST'])
def insert_news():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        # Create a new news post
        news_post = News(title=title, body=body)
        db.session.add(news_post)
        db.session.commit()

        flash('News added successfully!', 'success')

        return redirect(url_for('add_news'))

    # Handle GET request (display the form)
    return render_template('add_news.html')

@app.route('/hods')
def hods():
    # Check if the teacher is logged in (has a session)
    if 'teacher_name' in session:
        teacher_name = session['teacher_name']
        teacher_job_no = session['teacher_job_no'] 
        assignments = Assignments.query.filter_by(teacher_post=teacher_job_no).all()
        return render_template('teacher_dashboard.html', teacher_name=teacher_name, teacher_job_no=teacher_job_no, assignments=assignments)
    else:
        # Redirect to the login page if the teacher is not logged in
        return redirect(url_for('staff_login'))

@app.route('/hod_login', methods=['POST', 'GET'])
def hod_login():
    if request.method == 'POST':
        job_no = request.form['job_no']
        password = request.form['password']

        # Check if the teacher exists and their password is correct
        teacher = Teacher.query.filter_by(job_no=job_no).first()

        if teacher and teacher.department == 'science' and teacher.posts:
           
             assignments = Assignments.query.filter(or_(Assignments.subject == 'mathematics',
                                            Assignments.subject == 'biology',
                                            Assignments.subject == 'chemistry',
                                            Assignments.subject == 'physics')).all()
             return render_template('science.html', teacher_name=teacher.name, teacher_job_no=teacher.job_no, assignments=assignments)

        elif teacher and teacher.department == 'humanities' and teacher.posts:

             assignments = Assignments.query.filter(or_(Assignments.subject == 'history',
                                            Assignments.subject == 'cre',
                                            Assignments.subject == 'geography')).all()
             return render_template('humanities.html', teacher_name=teacher.name, teacher_job_no=teacher.job_no, assignments=assignments)

        elif teacher and teacher.department == 'technicals' and teacher.posts:
            
             assignments = Assignments.query.filter(or_(Assignments.subject == 'computer',
                                            Assignments.subject == 'agriculture',
                                            Assignments.subject == 'business')).all()

        elif teacher and teacher.department == 'languages' and teacher.posts:
             
             assignments = Assignments.query.filter(or_(Assignments.subject == 'english',
                                            Assignments.subject == 'kiswahili',
                                            Assignments.subject == 'french')).all()
             return render_template('languages.html', teacher_name=teacher.name, teacher_job_no=teacher.job_no, assignments=assignments)

        elif teacher:
            flash('You do not have permission to access this page.', 'error')
        else:
            flash('Invalid job number or password.', 'error')

    return render_template('hod_login.html')

from flask import request, flash, redirect, url_for, render_template, session

# ... your other imports ...

@app.route('/edit_assignment/<int:assignment_id>', methods=['GET', 'POST'])
def edit_assignment(assignment_id):
    # Check if the teacher is logged in (has a session)
    if 'teacher_job_no' in session:
        teacher_job_no = session['teacher_job_no']

        # Query the assignment with the given assignment_id and teacher_job_no
        assignment = Assignments.query.filter_by(id=assignment_id, teacher_post=teacher_job_no).first()

        if not assignment:
            flash('Assignment not found or you do not have permission to edit it.', 'danger')
            return redirect(url_for('teacher_dashboard'))

        if request.method == 'POST':
            # Handle form submission for editing the assignment
            assignment.title = request.form['title']
            assignment.body = request.form['body']
            
            # Check if the checkbox is checked and update the 'posts' field accordingly
            if 'posts' in request.form:
                assignment.posts = True
            else:
                assignment.posts = False
            
            db.session.commit()
            flash('Assignment updated successfully!', 'success')
            return redirect(url_for('assignments'))

        # Render the form for editing the assignment
        return render_template('edit_assignment.html', assignment=assignment)

    else:
        return redirect(url_for('staff_login'))



@app.route('/delete_image/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    # Find the image with the specified ID in the database
    image = Photo.query.get(image_id)

    if image:
        # Delete the image from the database
        db.session.delete(image)
        db.session.commit()

        # Delete the actual image file from the file system
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        if os.path.exists(image_path):
            os.remove(image_path)

        flash('Image deleted successfully', 'success')
    else:
        flash('Image not found', 'error')

    return redirect(url_for('photos'))  # Redirect to the image upload page


@app.route('/upload_notes')
def upload_notes():
    files = File.query.all()
    return render_template('upload_notes.html', files=files)

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' in request.files:
        uploaded_file = request.files['file']  # Use 'file', not 'file_name'
        if uploaded_file.filename != '':
            file_name = uploaded_file.filename
            uploaded_file.save(os.path.join('static/notes', file_name))
            new_file = File(file_name=file_name, teacher=request.form['teacher'])
            db.session.add(new_file)
            db.session.commit()
    return redirect(url_for('upload_notes'))


@app.route('/delete_note/<int:file_id>', methods=['POST'])
def delete_notes(file_id):
    file = File.query.get(file_id)

    if file:
        # Remove the file from the file system
        file_path = os.path.join('static/notes', file.file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete the file from the database
        db.session.delete(file)
        db.session.commit()

        flash('File deleted successfully!', 'success')
    else:
        flash('File not found.', 'danger')

    return redirect(url_for('upload_notes'))


@app.route('/files', methods=['GET', 'POST'])
def files():
    if request.method == 'POST':
        file_id = request.form.get('file_id')  # Get the file_id from the form
        checked = request.form.get('checked')  # Get the value of the checkbox
        
        file = File.query.get(file_id)  # Retrieve the File object by file_id
        if file:
            file.posts = checked  # Update the 'posts' column based on the checkbox
            db.session.commit()
    
    files = File.query.all()  # Get all files from the database
    return render_template('files.html', files=files)


@app.route('/update_file/<int:file_id>', methods=['POST'])
def update_file(file_id):
    if request.method == 'POST':
        checked = request.form.get('checked')  # Get the checkbox value

        # Query the file with the given file_id
        file = File.query.get(file_id)

        if file:
            # Convert the checkbox value to a boolean
            posts = checked == 'on'
            
            # Update the 'posts' column and commit the changes
            file.posts = posts
            db.session.commit()

    # Redirect back to the list of files
    return redirect(url_for('files'))



@app.route('/notes', methods=['GET', 'POST'])
def notes(): 
    posts = File.query.filter_by(posts=True).all()
    return render_template('notes.html', posts=posts)

static_password = "PHOENIXINCHESI@SUPER"

@app.route('/admin_pannel', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == static_password:
            return redirect(url_for('add_staff'))
    return render_template('admin_login.html')

static_password = "PHOENIXINCHESI@SUPER"
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == static_password:
            session['logged_in'] = True  # Set a session variable to indicate login
            return redirect(url_for('add_staff'))
    return render_template('admin_login.html')



@app.route('/student_dashboard')
def student_dashboard():
    if 'user_name' in session:
        user_name = session['user_name']
        user_id = session['user_id']
        assignments = Assignments.query.filter_by(posts=True).all()
        memos = Memo.query.filter_by(audience='student').all()
        return render_template('student_dashboard.html', user_name=user_name,assignments=assignments, memos=memos)
    else:
        return redirect(url_for('staff_login'))

@app.route('/st_password')
def st_password():
    if 'user_id' not in session:
        flash('You need to log in to access this page.', 'warning')
        return redirect(url_for('student_login'))
    
    # Only logged-in students can access this page
    return render_template('st_password.html')




@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        # Get form data
        adm = request.form['adm']
        old_password = request.form['old_password']
        new_password = request.form['new_password']

        # Query the database to find the user by ADM
        student = Student.query.filter_by(adm=adm).first()

        if student and student.password == old_password:
            # Update the password
            student.password = new_password
            db.session.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('st_password'))

    # Display the flash message for both success and failure cases
    flash('Incorrect ADM or old password. Please try again.', 'error')

    # Render the password change form
    return render_template('st_password.html')


@app.route('/assignments')
def assignments():
    assignments = Assignments.query.all() 
    return render_template('assignments.html', assignments=assignments)



@app.route('/delete_news/<int:id>', methods=['POST'])
def delete_news(id):
    news_post = News.query.get_or_404(id)  # Get the news post by its ID or return a 404 if not found

    db.session.delete(news_post)
    db.session.commit()
    flash('The news post has been deleted.', 'success')
    return redirect(url_for('add_news'))  # Redirect to the desired page after delet



@app.route('/te_password', methods=['GET', 'POST'])
def te_password():
    if request.method == 'POST':
        job_no = request.form['job_no']
        current_password = request.form['current_password']
        new_password = request.form['new_password']

        # Query the database to find the teacher by job number
        teacher = Teacher.query.filter_by(job_no=job_no).first()

        if teacher:
            # Check if the current password matches the stored password
            if teacher.password == current_password:
                # Update the password with the new password
                teacher.password = new_password
                db.session.commit()
                flash('Password changed successfully!', 'success')
            else:
                flash('Current password is incorrect. Please try again.', 'error')
        else:
            flash('Teacher with this job number does not exist.', 'error')

    return render_template('te_password.html')


@app.route('/addabout')
def addabout():
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Redirect to login page if not logged in\
    else:
        about_items = About.query.all()
        return render_template('addabout.html', about_items=about_items)

@app.route('/add_about', methods=['POST'])
def add_about():
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Redirect to login page if not logged in\
    else:
        title = request.form['title']
        description = request.form['description']
        note = request.form['note']
    
        image = None  # Initialize image as None by default

    # Handle image upload
        if 'image' in request.files:
            uploaded_image = request.files['image']
            if uploaded_image.filename != '':
                # Generate a unique filename to prevent overwriting
                filename = secure_filename(uploaded_image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDERS'], filename)
                uploaded_image.save(image_path)
                image = f'uploads/{filename}'  # Store the relative path in the database

        about_item = About(title=title, description=description, note=note, image=image)

    # Add the about item to the database
        db.session.add(about_item)
        db.session.commit()

        return redirect(url_for('addabout'))


@app.route('/delete_about/<int:id>', methods=['POST'])
def delete_about(id):
    about_item = About.query.get_or_404(id)
    
    # Delete the post from the database
    db.session.delete(about_item)
    db.session.commit()

    return redirect(url_for('addabout'))



@app.route('/teacher_password')
def teacher_password():
    # Check if the teacher is logged in (has a session)
    if 'teacher_name' in session:
        teacher_name = session['teacher_name']
        teacher_job_no = session['teacher_job_no'] 
        return render_template('te_password.html', teacher_name=teacher_name, teacher_job_no=teacher_job_no)
    else:
        # Redirect to the login page if the teacher is not logged in
        flash('You need to log in to access this page.', 'warning')
        return redirect(url_for('staff_login'))


@app.route('/alumni')
def alumni():
    images = Image.query.all()
    return render_template('alumni.html', images=images)
    
@app.route('/alumnis')
def alumnis():
    images = Image.query.all()
    return render_template('alumnis.html', images=images)


@app.route('/delete_alumni/<int:image_id>', methods=['POST'])
def delete_alumni(image_id):
    image = Image.query.get(image_id)

    if image:
        # Delete the associated image file from the server
        if os.path.exists(image.filename):
            os.remove(image.filename)

        # Delete the image record from the database
        db.session.delete(image)
        db.session.commit()
        flash('Alumni deleted successfully!', 'success')
    else:
        flash('Alumni not found.', 'error')

    return redirect(url_for('alumni'))

@app.route('/upload_alumni', methods=['POST'])
def upload_alumni():
    name = request.form['name']
    story = request.form['story']
    image = request.files['image']

    if name and story and image:
        filename = os.path.join('static/uploads', image.filename)
        image.save(filename)
        new_image = Image(name=name, story=story, filename=filename)
        db.session.add(new_image)
        db.session.commit()
        flash('Alumni uploaded successfully!', 'success')
    return redirect(url_for('alumni'))

def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/memo')
def memo():
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Redirect to login page if not logged in\
    else:
        memos = Memo.query.all()
        return render_template('memo.html', memos=memos)

@app.route('/add_memo', methods=['POST'])
def add_memo():
    title = request.form.get('title')
    body = request.form.get('body')
    audience = request.form.get('audience').lower()  # Convert to lowercase
    
    memo = Memo(title=title, body=body, audience=audience)
    db.session.add(memo)
    db.session.commit()
    flash('Memo added successfully', 'success')
    return redirect(url_for('memo'))

@app.route('/delete_memo/<int:memo_id>', methods=['POST'])
def delete_memo(memo_id):
    memo = Memo.query.get_or_404(memo_id)
    db.session.delete(memo)
    db.session.commit()

    flash('Memo deleted successfully', 'success')  # Flash success message
    return redirect(url_for('memo'))

if __name__ == "__main__":
    app.run(debug=True)