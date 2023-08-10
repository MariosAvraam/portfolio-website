from flask import Flask, render_template

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
    return "Resume Page - Here we will serve the resume file."

if __name__ == "__main__":
    app.run(debug=True)
