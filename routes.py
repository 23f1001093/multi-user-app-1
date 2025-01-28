from flask import render_template, request, redirect, url_for, flash
from app import app
from models import db, User, Subject, Chapter, Quiz, Question, Option, Score
from werkzeug.security import generate_password_hash
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html') 

@app.route('/login', methods=['POST'])
def login_post():
    return 'Login post'

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    qualification = request.form.get('qualification')
    dob = request.form.get('dob')
    
    if not username or not password or not confirm_password :
        flash('Please fill out all required fields.')
        return redirect(url_for('register'))
    
    if password != confirm_password:
        flash('Passwords do not match.')
        return redirect(url_for('register'))
    
    user = User.query.filter_by(username = username).first()
    if user:
        flash('Email address already exists.')
        return redirect(url_for('register'))
    
    dob = datetime.strptime(dob, '%Y-%m-%d').date()

    password_hash = generate_password_hash(password)
   
    new_user = User(username=username, password=password_hash, qualification=qualification, dob=dob)
    db.session.add(new_user)
    db.session.commit()
    flash('Registration successful! Please log in.')
    return redirect(url_for('login'))
