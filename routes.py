from flask import render_template, request, redirect, url_for, flash, session
from app import app
from models import db, User, Subject, Chapter, Quiz, Question, Score
from werkzeug.security import generate_password_hash, check_password_hash
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

    user = User.query.filter_by(email=email).first()

    if not user:
        flash('Username does not exist')
        return redirect(url_for('login'))

    if not check_password_hash(user.password, password):
        flash('Password is incorrect')
        return redirect(url_for('login'))

    session['user_id'] = user.id
    flash('Login successful!')
    if user.is_admin:
        return redirect(url_for('admin'))
    else:
        print("Redirecting to index (login_post)")
        return redirect(url_for('user_dashboard'))


# ------Register route-------

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

    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email address already exists.')
        return redirect(url_for('register'))

    if dob:
        dob = datetime.strptime(dob, '%Y-%m-%d').date()
    else:
        dob = None

    password_hash = generate_password_hash(password)

    new_user = User(email=email, password=password_hash, qualification=qualification, dob=dob, full_name=full_name)
    db.session.add(new_user)
    db.session.commit()

    flash('Registration successful! Please log in.')
    return redirect(url_for('login'))


# -------Authorization Decorator--------
def auth_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if 'user_id' in session:
            return f(*args, **kwargs)
        else:
            flash('Login to continue')
            return redirect(url_for('login'))
    return inner


# -------Admin Decorator--------
def admin_required(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Login to continue')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user.is_admin:
            flash('You do not have permission to access this page')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return inner


@app.route('/')
@auth_required
def index():
    user = User.query.get(session['user_id'])
    quizzes = Quiz.query.limit(5).all() #get 5 available quizzes
    scores = Score.query.filter_by(user_id = user.id).limit(5).all() # get 5 recent score
    return render_template('index.html', user=user, quizzes = quizzes, scores = scores) # Check this part

@app.route('/profile')
@auth_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)


@app.route('/logout')
@auth_required
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))


# --------Admin routes-----------


@app.route('/admin')
@admin_required
def admin():
    subjects = Subject.query.all()

    
    user_count = User.query.count()
    subject_count = Subject.query.count()
    quiz_count = Quiz.query.count()
    chapter_count = Chapter.query.count()

    return render_template('admin.html', 
                           subjects=subjects, 
                           user_count=user_count, 
                           subject_count=subject_count, 
                           quiz_count=quiz_count, 
                           chapter_count=chapter_count)

@app.route('/subject/add')
@admin_required
def add_subject():
    return render_template('subjects/add.html')


@app.route('/subject/add', methods=['POST'])
@admin_required
def add_subject_post():
    name = request.form.get('name')
    description = request.form.get('description')
    if not name:
        flash('Please fill out all the required fields.')
        return redirect(url_for('add_subject'))

    subject = Subject(name=name, description=description)

    db.session.add(subject)
    db.session.commit()

    flash('Subject added successfully!')
    return redirect(url_for('admin'))


@app.route('/subject/<int:id>/')
@admin_required
def show_subject(id):
    subject = Subject.query.get(id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    return render_template('subjects/show.html', subject=subject)


@app.route('/subject/<int:id>/edit')
@admin_required
def edit_subject(id):
    subject = Subject.query.get(id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    return render_template('subjects/edit.html', subject=subject)


@app.route('/subject/<int:id>/edit', methods=['POST'])
@admin_required
def edit_subject_post(id):
    subject = Subject.query.get(id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    name = request.form.get('name')
    description = request.form.get('description')
    if not name:
        flash('Please fill out all the required fields.')
        return redirect(url_for('edit_subject', id=id))
    subject.name = name
    subject.description = description
    db.session.commit()
    flash('Subject updated successfully!')
    return render_template('subjects/edit.html', subject=subject)


@app.route('/subject/<int:id>/delete')
@admin_required
def delete_subject(id):
    subject = Subject.query.get(id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    return render_template('subjects/delete.html', subject=subject)


@app.route('/subject/<int:id>/delete', methods=['POST'])
@admin_required
def delete_subject_post(id):
    subject = Subject.query.get(id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!')
    return redirect(url_for('admin'))

@app.route('/admin/search', methods=['GET'])
@admin_required
def admin_search():
    query = request.args.get('q', '').strip()
    
    print(f"Search Query: '{query}'")  

    if not query:
        flash("Please enter a search statement.", "warning")
        return redirect(url_for('admin'))  

    users = User.query.filter(User.full_name.ilike(f"%{query}%")).all()
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{query}%")).all()
    chapters = Chapter.query.filter(Chapter.name.ilike(f"%{query}%")).all()

    return render_template('admin/search.html', 
                           query=query, 
                           users=users, 
                           subjects=subjects, 
                           quizzes=quizzes, 
                           chapters=chapters)

# -----------------Chapter routes---------------

@app.route('/chapter/add/<int:subject_id>')
@admin_required
def add_chapter(subject_id):
    subjects = Subject.query.all()
    subject = Subject.query.get(subject_id)
    if not subject:
        flash('Subject does not exist')
        return redirect(url_for('admin'))
    return render_template('chapter/add.html', subject=subject, subjects=subjects)


@app.route('/chapter/add/', methods=['POST'])
@admin_required
def add_chapter_post():
    name = request.form.get('name')
    description = request.form.get('description')
    subject_id = request.form.get('subject_id')

    if not name or not subject_id:
        flash('Please fill out all the required fields.')
        return redirect(url_for('add_chapter', subject_id=subject_id))
    # Convert subject_id to integer
    try:
        subject_id = int(subject_id)
    except ValueError:
        flash('Invalid subject selected.')
        return redirect(url_for('admin'))

    # Check if subject exists
    subject = Subject.query.get(subject_id)
    if not subject:
        flash('Subject does not exist.')
        return redirect(url_for('admin'))

    # Add the chapter
    chapter = Chapter(name=name, description=description, subject_id=subject_id)
    db.session.add(chapter)
    db.session.commit()

    flash('Chapter added successfully!')
    return redirect(url_for('show_subject', id=subject_id))


@app.route('/chapter/<int:id>')
def show_chapter(id):
    chapter = Chapter.query.get(id)
    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('admin'))
    return render_template('chapters/show.html', chapter=chapter)


@app.route('/chapter/<int:id>/edit')
@admin_required
def edit_chapter(id):
    subjects = Subject.query.all()
    chapter = Chapter.query.get(id)
    return render_template('chapter/edit.html', chapter=chapter, subjects=subjects)


@app.route('/chapter/<int:id>/edit', methods=['POST'])
@admin_required
def edit_chapter_post(id):
    name = request.form.get('name')
    description = request.form.get('description')
    subject_id = request.form.get('subject_id')

    if not name or not subject_id:
        flash('Please fill out all the required fields.')
        return redirect(url_for('add_chapter', subject_id=subject_id))
    # Convert subject_id to integer
    try:
        subject_id = int(subject_id)
    except ValueError:
        flash('Invalid subject selected.')
        return redirect(url_for('admin'))

    # Check if subject exists
    subject = Subject.query.get(subject_id)
    if not subject:
        flash('Subject does not exist.')
        return redirect(url_for('admin'))

    # Add the chapter
    chapter = Chapter.query.get(id)
    chapter.name = name
    chapter.description = description
    chapter.subject_id = subject_id
    db.session.add(chapter)
    db.session.commit()

    flash('Chapter edited successfully!')
    return redirect(url_for('show_subject', id=subject_id))


@app.route('/chapter/<int:id>/delete')
@admin_required
def delete_chapter(id):
    chapter = Chapter.query.get(id)
    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('admin'))
    return render_template('chapter/delete.html', chapter=chapter)


@app.route('/chapter/<int:id>/delete', methods=['POST'])
@admin_required
def delete_chapter_post(id):
    chapter = Chapter.query.get(id)

    subject_id = chapter.subject.id
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully!')
    return redirect(url_for('show_subject', id=subject_id))


# -----------------Quiz routes-----------------

@app.route('/quiz/add/<int:chapter_id>')
@admin_required
def add_quiz(chapter_id):
    chapters = Chapter.query.all()
    chapter = Chapter.query.get(chapter_id)

    if not chapter:
        flash('Chapter does not exist')
        return redirect(url_for('admin'))
    return render_template('quiz/add.html', chapter=chapter, chapters=chapters)


@app.route('/quiz/add', methods=['POST'])
@admin_required
def add_quiz_post():
    name = request.form['name']
    chapter_id = request.form['chapter_id']
    remarks = request.form.get('remarks', '')

    date_of_quiz = request.form['date_of_quiz']
    date_of_quiz = datetime.strptime(date_of_quiz, '%Y-%m-%d').date()  # Convert string to date

    time_duration = request.form['time_duration']

    new_quiz = Quiz(
        name=name,
        chapter_id=chapter_id,
        date_of_quiz=date_of_quiz,
        time_duration=time_duration,
        remarks=remarks
    )

    db.session.add(new_quiz)
    db.session.commit()

    flash('Quiz added successfully!')
    return redirect(url_for('show_quizzes', chapter_id=chapter_id))


@app.route('/quiz/<int:id>/edit')
@admin_required
def edit_quiz(id):
    quiz = Quiz.query.get(id)
    chapters = Chapter.query.all()
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('admin'))
    return render_template('quiz/edit.html', quiz=quiz, chapters=chapters)


@app.route('/quiz/<int:id>/edit', methods=['POST'])
@admin_required
def edit_quiz_post(id):
    quiz = Quiz.query.get(id)
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('admin'))

    date_str = request.form.get('date_of_quiz')
    try:
        quiz.date_of_quiz = datetime.strptime(date_str, "%Y-%m-%d").date()  # Convert string to date
    except ValueError:
        flash('Invalid date format! Use YYYY-MM-DD.')
        return redirect(url_for('edit_quiz', id=id))

    quiz.time_duration = request.form.get('time_duration')  # Time is stored as string
    quiz.remarks = request.form.get('remarks')

    db.session.commit()
    flash('Quiz updated successfully!')
    return redirect(url_for('show_subject', id=quiz.chapter.subject.id))


@app.route('/quiz/<int:id>/delete')
@admin_required
def delete_quiz(id):
    quiz = Quiz.query.get(id)
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('admin'))
    return render_template('quiz/delete.html', quiz=quiz)


@app.route('/quiz/<int:id>/delete', methods=['POST'])
@admin_required
def delete_quiz_post(id):
    quiz = Quiz.query.get(id)
    subject_id = quiz.chapter.subject.id
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!')
    return redirect(url_for('show_quizzes', chapter_id=quiz.chapter.id))


@app.route('/quizzes/<int:chapter_id>')
@admin_required
def show_quizzes(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        flash('Chapter does not exist.')
        return redirect(url_for('admin'))

    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    subject = chapter.subject if chapter else None
    return render_template('quiz/show.html', chapter=chapter, quizzes=quizzes, subject=subject)


# ----------------Question routes----------------

@app.route('/question/add/<int:quiz_id>')
@admin_required
def add_question(quiz_id):
    quizzes = Quiz.query.all()
    quiz = Quiz.query.get(quiz_id)

    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('admin'))

    return render_template('question/add.html', quiz=quiz, quizzes=quizzes)


@app.route('/question/add', methods=['POST'])
@admin_required
def add_question_post():
    quiz_id = request.form.get('quiz_id')
    question_statement = request.form.get('question_statement')
    option1 = request.form.get('option1')
    option2 = request.form.get('option2')
    option3 = request.form.get('option3')
    option4 = request.form.get('option4')
    correct_option = request.form.get('correct_option')

    # Ensure all fields are filled
    if not all([question_statement, option1, option2, option3, option4, correct_option]):
        flash('Please fill in all fields.')
        return redirect(url_for('add_question', quiz_id=quiz_id))

    new_question = Question(
        quiz_id=quiz_id,
        question_statement=question_statement,
        option1=option1,
        option2=option2,
        option3=option3,
        option4=option4,
        correct_option=correct_option
    )

    db.session.add(new_question)
    db.session.commit()

    flash('Question added successfully!')
    return redirect(url_for('show_questions', quiz_id=quiz_id))


@app.route('/question/<int:id>/edit')
@admin_required
def edit_question(id):
    question = Question.query.get(id)
    if not question:
        flash('Question does not exist')
        return redirect(url_for('admin'))
    return render_template('question/edit.html', question=question)


@app.route('/question/<int:id>/edit', methods=['POST'])
@admin_required
def edit_question_post(id):
    question = Question.query.get(id)
    if not question:
        flash('Question does not exist')
        return redirect(url_for('admin'))

    question.question_statement = request.form['question_statement']
    question.option1 = request.form['option1']
    question.option2 = request.form['option2']
    question.option3 = request.form['option3']
    question.option4 = request.form['option4']
    question.correct_option = request.form['correct_option']

    db.session.commit()
    flash('Question updated successfully!')
    return redirect(url_for('show_questions', quiz_id=question.quiz_id))


@app.route('/question/<int:id>/delete')
@admin_required
def delete_question(id):
    question = Question.query.get(id)
    if not question:
        flash('Question does not exist')
        return redirect(url_for('admin'))
    return render_template('question/delete.html', question=question)


@app.route('/question/<int:id>/delete', methods=['POST'])
@admin_required
def delete_question_post(id):
    question = Question.query.get(id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!')
    return redirect(url_for('show_questions', quiz_id=quiz_id))


@app.route('/question/<int:quiz_id>')
@admin_required
def show_questions(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Quiz does not exist.')
        return redirect(url_for('admin'))

    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    return render_template('question/show.html', quiz=quiz, questions=questions)


# -----------------Score routes----------------

@app.route('/score/add')
@admin_required
def add_score():
    return render_template('score/add.html')


@app.route('/score/add', methods=['POST'])
@admin_required
def add_score_post():
    user_id = request.form.get('user_id')
    quiz_id = request.form.get('quiz_id')
    score = request.form.get('score')

    if not user_id or not quiz_id or not score:
        flash('Please fill out all the required fields.')
        return redirect(url_for('add_score'))

    new_score = Score(user_id=user_id, quiz_id=quiz_id, score=score)
    db.session.add(new_score)
    db.session.commit()

    flash('Score added successfully!')
    return redirect(url_for('show_scores', id=user_id))


@app.route('/score/<int:id>/edit')
@admin_required
def edit_score(id):
    score = Score.query.get(id)
    if not score:
        flash('Score does not exist')
        return redirect(url_for('admin'))
    return render_template('score/edit.html', score=score)


# -------user routes--------

@app.route('/user/quizzes')
@auth_required
def user_quizzes():
    user = User.query.get(session['user_id'])
    quizzes = Quiz.query.all()  # Or filter quizzes by subject/chapter if needed
    return render_template('user/quizzes.html', quizzes=quizzes, user=user)


@app.route('/quiz/<int:quiz_id>')
@auth_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('user_quizzes'))

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('user/take_quiz.html', quiz=quiz, questions=questions)


@app.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@auth_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash('Quiz does not exist')
        return redirect(url_for('user_quizzes'))

    user = User.query.get(session['user_id'])
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    score = 0
    for question in questions:
        user_answer = request.form.get(f'question_{question.id}')
        
        correct_option_value = None
        if question.correct_option == "option1":
            correct_option_value = question.option1
        elif question.correct_option == "option2":
            correct_option_value = question.option2
        elif question.correct_option == "option3":
            correct_option_value = question.option3
        elif question.correct_option == "option4":
            correct_option_value = question.option4

        
        if user_answer and user_answer.strip() == correct_option_value.strip():
            score += 1

        
    new_score = Score(
       user_id=user.id, 
       quiz_id=quiz.id, 
       t_score=score, 
       time_stamp_of_attempt=datetime.utcnow()
         )
    db.session.add(new_score)
    db.session.commit()

    flash(f'Quiz submitted successfully! Your score: {score}/{len(questions)}')
    return redirect(url_for('user_dashboard'))


@app.route('/user/profile')
@auth_required
def user_profile():
    user = User.query.get(session['user_id'])
    return render_template('user/profile.html', user=user)


@app.route('/user/profile/edit', methods=['GET', 'POST'])
@auth_required
def edit_user_profile():
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.qualification = request.form.get('qualification')
        dob_str = request.form.get('dob')
        try:
            user.dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None  # Handle empty date
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.")
            return render_template('user/edit_profile.html', user=user)  # return the page with an error msg!

        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('user_profile'))

    return render_template('user/edit_profile.html', user=user)


@app.route('/user/scores')
@auth_required
def user_scores():
    user = User.query.get(session['user_id'])
    scores = Score.query.filter_by(user_id=user.id).all()
    return render_template('user/scores.html', scores=scores, user=user)  # pass user to the template so you can view their name for example.


@app.route('/quizzes')
@auth_required
def quizzes():
    quizzes = Quiz.query.all()
    return render_template('quizzes.html', quizzes=quizzes)


@app.route('/quiz/<int:id>')
@auth_required
def quiz(id):
    quiz = Quiz.query.get(id)
    return render_template('quiz.html', quiz=quiz)


@app.route('/quiz/<int:id>/submit', methods=['POST'])
@auth_required
def submit_quiz_new(id):  # Renamed to avoid conflict
    quiz = Quiz.query.get(id)
    questions = Question.query.filter_by(quiz_id=id).all()
    score = 0
    for question in questions:
        answer = request.form.get(str(question.id))
        if answer == question.correct_option:
            score += 1
    new_score = Score(quiz_id=id, user_id=session['user_id'], score=score)
    db.session.add(new_score)
    db.session.commit()
    flash('Quiz submitted successfully!')
    return redirect(url_for('quizzes'))


@app.route('/scores')
@auth_required
def scores():
    user = User.query.get(session['user_id'])
    scores = Score.query.filter_by(user_id=session['user_id']).all()
    return render_template('scores.html', scores=scores, user=user)


@app.route('/scores/<int:id>')
@auth_required
def show_scores(id):
    user = User.query.get(id)
    scores = Score.query.filter_by(user_id=id).all()
    return render_template('scores.html', scores=scores, user=user)

@app.route('/user/dashboard')
@auth_required
def user_dashboard():
    user = User.query.get(session['user_id'])
    
    # Fetch quizzes (you might want to add filtering logic here)
    quizzes = Quiz.query.all()
    
    # Fetch user's scores, ordered by time of attempt
    attempts = Score.query.filter_by(user_id=user.id).order_by(Score.time_stamp_of_attempt.desc()).all()  # Order by date

    return render_template('user/dashboard.html', user=user, quizzes=quizzes, attempts=attempts)