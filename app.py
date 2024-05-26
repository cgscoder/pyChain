#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL

from passwords import _mysql_password
from sql_helpers import *
from forms import *

app = Flask(__name__)

# DB Access
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = _mysql_password
app.config['MYSQL_DB'] = 'crypto'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def log_in_user(username):
    users = Table("users", "name", "username", "email", "password")
    user = users.getone("username", username)
    
    session['logged_in'] = True
    session['username'] = username
    session['name'] = user.get('name')
    session['email'] = user.get('email')
    
    
#Routes
@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/register", methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    users = Table("users", "name", "username", "email", "password")
    
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        name = form.name.data
        
        if isnewuser(username): # check if a new user
            password = sha256_crypt.hash(form.password.data)
            users.insert(name, username, email, password)
            log_in_user(username)
            return redirect(url_for('dashboard'))
        else:
            flash('User already exists', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html', form=form)

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html', session=session)

@app.route("/")
def index():
    users = Table("users", "name", "username", "email", "password")
    #users.insert("Jake", "rake-handel", "jh@gmail.com", "hash")
    #users.deleteall()
    return render_template('index.html')

# Run server
if __name__ == '__main__':
    app.secret_key = 'kitkat'
    app.run(debug=True)