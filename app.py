from flask import Flask, render_template, send_from_directory
from os import getenv
from dotenv import load_dotenv

load_dotenv()

DIRECTORY = getenv("DIRECTORY")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/resume')
def resume():
    return send_from_directory(directory=DIRECTORY, path='Resume.pdf')

if __name__ == "__main__":
    app.run(debug=True)
