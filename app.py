from os import getenv
from dotenv import load_dotenv
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import requests


load_dotenv()

DIRECTORY = getenv("DIRECTORY")
ADMIN_PASSWORD = getenv("ADMIN_PASSWORD")

app = Flask(__name__)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.mailgun.org'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = getenv("MAILGUN_USERNAME")
app.config['MAIL_PASSWORD'] = getenv("MAILGUN_PASSWORD")

mail=Mail(app)

# Secret Key
app.config['SECRET_KEY'] = getenv("SECRET_KEY")

# SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
db = SQLAlchemy(app)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300))
    github_url = db.Column(db.String(300), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html', active='home')

@app.route('/projects')
def projects():
    projects = Project.query.all()
    return render_template('projects.html', projects=projects, active='projects')

@app.route('/blog')
def blog():
    return render_template('blog.html', active='blog')

@app.route('/resume')
def resume():
    return send_from_directory(directory=DIRECTORY, path='Resume.pdf')

@app.route('/send_message', methods=['POST'])
def send_message():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message_body = request.form['message']
        
        message = Message(subject="New Contact Form Submission",
                          sender=email,
                          recipients=["marios_2510@hotmail.com"], 
                          body=f"Name: {name}\nEmail: {email}\n\n{message_body}")
        
        try:
            mail.send(message)
            flash('Your message has been sent successfully!', 'success')
        except:
            flash('Error occurred. Please try again later.', 'danger')
        
        return redirect(url_for('index'))
    
@app.route('/admin/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            title = request.form.get('title')
            description = request.form.get('description')
            image_url = request.form.get('image_url')
            github_url = request.form.get('github_url')
            project = Project(title=title, description=description, image_url=image_url, github_url=github_url)
            db.session.add(project)
            db.session.commit()
            flash('Project added successfully!', 'success')
        else:
            flash('Incorrect password!', 'danger')
    return render_template('add_project.html')

if __name__ == "__main__":
    app.run(debug=True)
