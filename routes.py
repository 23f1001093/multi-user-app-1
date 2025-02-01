from flask import render_template, request, redirect, url_for, flash, session
from app import app
from models import db, User, Subject, Chapter, Quiz, Question, Score
from werkzeug.security import generate_password_hash , check_password_hash
from datetime import datetime
from functools import wraps

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html') 

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        flash('Please fill out all the required fields.')
        return redirect(url_for('login'))

    user = User.query.filter_by(email = email).first()
    
    if user is None :
         flash('Username does not exist')
         return redirect(url_for('login'))
    
    if not check_password_hash(user.password, password):
        flash('Password is incorrect')
        return redirect(url_for('login'))
    
    session['user_id'] = user.id
    flash('Login successful!')
    return redirect(url_for('index'))
    
  
@app.route('/register', methods=['POST'])
def register_post():
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    qualification = request.form.get('qualification')
    dob = request.form.get('dob')
    full_name = request.form.get('full_name')
    
    if not email or not password or not confirm_password:
        flash('Please fill out all the required fields.')
        return redirect(url_for('register'))
    
    if password != confirm_password:
        flash('Passwords do not match.')
        return redirect(url_for('register'))
    
    user = User.query.filter_by(email = email).first()
    if user:
        flash('Email address already exists.')
        return redirect(url_for('register'))
    
    dob = datetime.strptime(dob, '%Y-%m-%d').date()
    
    password_hash = generate_password_hash(password)
   
    new_user = User(email=email, password=password_hash,qualification=qualification, dob=dob, full_name=full_name)
    db.session.add(new_user)
    db.session.commit()

    flash('Registration successful! Please log in.')
    return redirect(url_for('login'))
def auth_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if 'user_id' in session:
           return f(*args, **kwargs)
        else:
            flash('Login to continue')
            return redirect(url_for('login'))
    return inner

@app.route('/')
@auth_required
def index():
    return render_template('index.html')
   
@app.route('/profile')
@auth_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)
   
@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))
    
    