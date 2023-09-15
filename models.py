from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    adm = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    stream = db.Column(db.String(50))


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
        self.department = department

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


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255))
    teacher = db.Column(db.String(255))
    posts = db.Column(db.Boolean, default=False)

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
        self.subject = subject
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