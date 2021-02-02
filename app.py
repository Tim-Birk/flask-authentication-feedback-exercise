"""Feedback application."""

from flask import Flask, render_template, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from models import User, Feedback, db, connect_db
from forms import RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','SECRET!')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

debug = DebugToolbarExtension(app)

@app.route("/")
def index_page():
    """Redirect to /register."""
    return redirect("/register")

@app.route("/register", methods=["GET","POST"])
def show_register_form():
    """GET: Show a form that when submitted will register/create a user.
    
    POST: Process the registration form by adding a new user. Then redirect to their user page"""
    
    if 'username' in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        firstname = form.firstname.data
        lastname = form.lastname.data

        new_user = User.register(username, password)
        new_user.email = email
        new_user.firstname = firstname
        new_user.lastname = lastname

        db.session.add(new_user)
        
        try:
            db.session.commit()
        except IntegrityError as e:
            errorInfo = e.orig.args
            if 'email' in e.orig.args[0]:
                form.email.errors.append('Email taken.  Please pick another')
            elif 'username' in e.orig.args[0]:
                form.username.errors.append('Username taken.  Please pick another')
            return render_template('register.html', form=form)
        session['username'] = new_user.username
        flash(f'Welcome!  Your new account has been created for {new_user.username}', "success")
        return redirect(f'/users/{new_user.username}')
    else:
        return render_template(
            "register.html", form=form)
    

@app.route("/login", methods=["GET","POST"])
def login_user():
    """GET: Show a form that when submitted will login a user. 
    
    POST: Authenticates user and adds them to session. Then redirects to their user page"""

    if 'username' in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "success")
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    """Log user out by removing them from the session"""
    session.pop('username')
    flash("You are logged out.", "success")
    return redirect('/')

@app.route("/users/<username>")
def show_user_page(username):
    """Show information about the given user.
    Show all of the feedback that the user has given.
    """

    user = User.query.get_or_404(username)
    if not 'username' in session:
        flash('You must be logged in to view that page.', 'error')
        return redirect('/login')
    elif not session['username'] == username:
        flash("You don't have permission to view that page.", 'error')
        return redirect('/login')
    else:
        return render_template('user_page.html', user=user)

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """Remove the user from the database and delete all of their feedback. 
    Clear any user information in the session and redirect to /. 
    Only the user who is logged in can successfully delete their account"""

    user = User.query.get_or_404(username)
    try:
        user = User.query.filter_by(username=username).first()
        db.session.delete(user)
        db.session.commit()

        flash("User deleted", "success")
        session.pop('username')
        return redirect('/')
    except Exception as e:
        flash(f"There was an error deleting the user: {e}", "error")
        return redirect(f"/users/{username}")

    return redirect(f"/")


@app.route("/users/<username>/feedback/add", methods=["GET","POST"])
def add_feedback(username):
    """GET: Display a form to add feedback. Only the user who is logged in can see this form
    
    POST: Add a new piece of feedback and redirect to /users/<username> 
    Only the user who is logged in can successfully add feedback"""

    if not 'username' in session:
        flash('You must be logged in to view that page.', 'error')
        return redirect('/login')
    elif not session['username'] == username:
        flash("You don't have permission to view that page.", 'error')
        return redirect('/login')

    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        fb = Feedback(title=title, content=content, username=username)
        try:
            db.session.add(fb)
            db.session.commit()
        
            flash(f"Feedback submitted!", "success")
            return redirect(f'/users/{username}')
        except:
            flash(f"Error submitting feedback.", "error")

    return render_template('add_feedback.html', form=form)


@app.route("/feedback/<id>/update", methods=["GET", "POST"])
def edit_feedback(id):
    """GET: Display a form to edit feedback 
    Only the user who has written that feedback can see this form 
    
    POST: Update a specific piece of feedback and redirect to /users/<username>
    Only the user who has written that feedback can update it"""

    fb = Feedback.query.get_or_404(id)
    if not 'username' in session:
        flash('You must be logged in to view that page.', 'error')
        return redirect('/login')
    elif not session['username'] == fb.user.username:
        flash("You don't have permission to view that page.", 'error')
        return redirect('/login')

    form = FeedbackForm(obj=fb)

    if form.validate_on_submit():
        fb.title = form.title.data
        fb.content = form.content.data
        
        db.session.commit()
        flash(f"Updated feedback: {fb.title}","success")
        return redirect(f"/users/{fb.user.username}")

    else:
        return render_template("edit_feedback.html", form=form)


@app.route("/feedback/<id>/delete", methods=["POST"])
def delete_feedback(id):
    """Delete a specific piece of feedback and redirect to /users/<username> — 
    Only the user who has written that feedback can delete it"""

    try:
        fb = Feedback.query.filter_by(id=id).first()
        if not 'username' in session:
            flash('You must be logged in to view that page.', 'error')
            return redirect('/login')
        elif not session['username'] == fb.user.username:
            flash("You don't have permission to view that page.", 'error')
            return redirect('/login')
            
        db.session.delete(fb)
        db.session.commit()
        flash("Feedback deleted", "success")
    except Exception as e:
        flash(f"There was an error deleting the feedback: {e}", "error")
        
    return redirect(f"/users/{fb.user.username}")
