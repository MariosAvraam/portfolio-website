from os import getenv
from dotenv import load_dotenv
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash
from flask_mail import Mail, Message
import requests


load_dotenv()

DIRECTORY = getenv("DIRECTORY")

app = Flask(__name__)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.mailgun.org'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = getenv("MAILGUN_USERNAME")
app.config['MAIL_PASSWORD'] = getenv("MAILGUN_PASSWORD")

app.config['SECRET_KEY'] = getenv("SECRET_KEY")

mail=Mail(app)

@app.route('/')
def index():
    return render_template('index.html', active='home')

@app.route('/projects')
def projects():
    return render_template('projects.html', active='projects')

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

if __name__ == "__main__":
    app.run(debug=True)
