from app import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30),nullable = False, unique = True )
    password = db.Column(db.String(100),nullable = False)
    full_name = db.Column(db.String(50),nullable = False)
    qualification = db.Column(db.String(400))
    dob = db.Column(db.Date, nullable = False)
    
    quizez = db.relationship('Score', backref="user", lazy = True)
    
    is_admin = db.Column(db.Boolean, default=False, nullable=False)


class Subject(db.Model):
    __tablename__= 'subject'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20),nullable = False)
    description = db.Column(db.String(180), nullable = False)

    chapters = db.relationship('Chapter', backref="subject", lazy = True)

class Chapter(db.Model):
    __tablename__= 'chapter'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20),nullable = False)
    description = db.Column(db.String(180), nullable = False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
   
    quizzes = db.relationship('Quiz', backref="chapter", lazy = True)

    
class Quiz(db.Model):
    __tablename__= 'quiz'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20),nullable = False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable = False)
    date_of_quiz = db.Column(db.Date, nullable = False)
    time_duration = db.Column(db.String(5), nullable=False)
    remarks = db.Column(db.String(180))

    questions = db.relationship('Question', backref="quiz", lazy = True)
    scores = db.relationship('Score', backref='quiz', lazy=True)


class Question(db.Model):
    __tablename__= 'question'
    id = db.Column(db.Integer, primary_key = True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable = False)
    question_statement = db.Column(db.String(500), nullable=False)
    
    options = db.relationship('Option', backref="question", lazy = True)
    

class Option(db.Model):
    __tablename__ = 'option'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
  
    option1 = db.Column(db.String(100), nullable=False)
    option2 = db.Column(db.String(100), nullable=False)
    option3 = db.Column(db.String(100), nullable=False)
    option4 = db.Column(db.String(100), nullable=False)
   
    correct_option = db.Column(db.String(10), nullable=False)
    
   
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()
   


