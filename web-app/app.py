from os import path

from flask import Flask, render_template, redirect, url_for, request

template_dir = path.abspath('./templates')
static_dir = path.abspath('./static')

app = Flask(__name__, template_folder = template_dir, static_folder = static_dir)

@app.route('/')
def home():
    ''' homepage with login form '''
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    ''' register form ''' 
    if request.method == 'GET':
        return render_template('register.html')
    return render_template('home.html',
        given_name = request.form.get("given-name"),
        surname = request.form.get("surname"),
        email = request.form.get("email"))

if __name__ == "__main__":
    ''' do soomething here '''