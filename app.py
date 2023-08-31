from os import getenv
from dotenv import load_dotenv
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

load_dotenv()

DIRECTORY = getenv("DIRECTORY")
ADMIN_PASSWORD = getenv("ADMIN_PASSWORD")

MAX_ATTEMPTS = 3
LOCKOUT_TIME = 15

def check_failed_attempts():
    last_attempt_time = session.get('last_failed_time')
    if last_attempt_time:
        duration_since_last_attempt = datetime.now() - datetime.strptime(last_attempt_time, '%Y-%m-%d %H:%M:%S')
        if duration_since_last_attempt < timedelta(minutes=LOCKOUT_TIME):
            return False
        else:
            # Reset the counter if the lockout time has passed
            session.pop('failed_attempts', None)
            session.pop('last_failed_time', None)
    return True

app = Flask(__name__)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.mailgun.org'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = getenv("MAILGUN_USERNAME")
app.config['MAIL_PASSWORD'] = getenv("MAILGUN_PASSWORD")

mail = Mail(app)

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
        if not check_failed_attempts():
            flash(f'You have entered the password incorrectly too many times. Please wait {LOCKOUT_TIME} minutes before trying again.', 'danger')
            return redirect(url_for('add_project'))
        
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_verified'] = True
            session.pop('failed_attempts', None)
            return redirect(url_for('admin_create_project'))
        else:
            session['failed_attempts'] = session.get('failed_attempts', 0) + 1
            if session['failed_attempts'] >= MAX_ATTEMPTS:
                session['last_failed_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            flash('Incorrect password!', 'danger')
            return redirect(url_for('add_project'))
    return render_template('enter_password.html')

@app.route('/admin/admin_create_project', methods=['GET', 'POST'])
def admin_create_project():
    if not session.get('admin_verified'):
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        github_url = request.form.get('github_url')
        project = Project(title=title, description=description, image_url=image_url, github_url=github_url)
        db.session.add(project)
        db.session.commit()
        session.pop('admin_verified', None)  # Clear the session variable
        flash('Project added successfully!', 'success')
        return redirect(url_for('projects'))
    return render_template('admin_create_project.html')

@app.route('/admin/select_edit_project', methods=['GET', 'POST'])
def select_edit_project():
    if request.method == 'POST':
        if not check_failed_attempts():
            flash(f'You have entered the password incorrectly too many times. Please wait {LOCKOUT_TIME} minutes before trying again.', 'danger')
            return redirect(url_for('select_edit_project'))
        
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_verified'] = True
            session.pop('failed_attempts', None)
            projects = Project.query.all()
            return render_template('select_edit_project.html', projects=projects)
        else:
            session['failed_attempts'] = session.get('failed_attempts', 0) + 1
            if session['failed_attempts'] >= MAX_ATTEMPTS:
                session['last_failed_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            flash('Incorrect password!', 'danger')
            return redirect(url_for('select_edit_project'))
    return render_template('enter_password.html')

@app.route('/admin/select_delete_project', methods=['GET', 'POST'])
def select_delete_project():
    if request.method == 'POST':
        if not check_failed_attempts():
            flash(f'You have entered the password incorrectly too many times. Please wait {LOCKOUT_TIME} minutes before trying again.', 'danger')
            return redirect(url_for('select_delete_project'))
        
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_verified'] = True
            session.pop('failed_attempts', None)
            projects = Project.query.all()
            return render_template('select_delete_project.html', projects=projects)
        else:
            session['failed_attempts'] = session.get('failed_attempts', 0) + 1
            if session['failed_attempts'] >= MAX_ATTEMPTS:
                session['last_failed_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            flash('Incorrect password!', 'danger')
            return redirect(url_for('select_delete_project'))
    return render_template('enter_password.html')

@app.route('/admin/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if not session.get('admin_verified'):
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('index'))
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.image_url = request.form.get('image_url')
        project.github_url = request.form.get('github_url')
        db.session.commit()
        session.pop('admin_verified', None)  # Clear the session variable
        flash('Project updated successfully!', 'success')
        return redirect(url_for('projects'))
    return render_template('edit_project.html', project=project)


@app.route('/admin/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    if not session.get('admin_verified'):
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('index'))
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    session.pop('admin_verified', None)  # Clear the session variable
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('projects'))

@app.errorhandler(500)
def internal_server_error(e):
    db.session.rollback()  # Rollback any active transactions
    flash('A server error occurred. Please try again.', 'danger')
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(debug=True)
