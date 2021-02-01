from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length

class RegisterForm(FlaskForm):
    """Form for registering user."""
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[Email(), Length(max=50)])
    firstname = StringField("First Name", validators=[InputRequired(), Length(max=30)])
    lastname = StringField("Last Name", validators=[InputRequired(), Length(max=30)])

class LoginForm(FlaskForm):
    """Form to login user."""
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    """Form for registering user."""
    title = StringField("Title", validators=[InputRequired(), Length(max=100)])
    content = TextAreaField("Content", validators=[InputRequired()])

