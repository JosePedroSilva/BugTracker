from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models import User, Team, Severity, Role

def team_choice():
    return Team.query

def severity_choice():
    return Severity.query

def user_choice():
    return User.query

def role_choice():
    return Role.query

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In') 

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = QuerySelectField('Access:', 
                                query_factory=role_choice, get_label='name',
                                allow_blank=False)
    team = QuerySelectField('Team:', 
                                query_factory=team_choice, get_label='name',
                                allow_blank=False)
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class TicketForm(FlaskForm):
    title = TextAreaField('Title:', validators=[
        DataRequired(), Length(min=1, max=50)
    ])
    severity = QuerySelectField('Priority/Impact:', 
                            query_factory=severity_choice, get_label='degree',
                            allow_blank=False)
    team = QuerySelectField('Team:', 
                            query_factory=team_choice, get_label='name',
                            allow_blank=False)
    ticket = TextAreaField('Please describe the issue.', validators=[
        DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Submit')

class ChangePassword(FlaskForm):
    #currentPassword = PasswordField('Current Password', validator=[DataRequired()])
    password = PasswordField('New password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change password')

    def __init__(self, username, *args, **kwargs):
        super(ChangePassword, self).__init__(*args, **kwargs)
        self.username = username

# class TakeOwnership(FlaskForm):
#     userField = QuerySelectField('Owner:',
#                                     query_factory=user_choice, get_label='username')
    
    # def __init__(self, username, *args, **kwargs):
    #     super(TakeOwnership, self).__init__(*args, **kwargs)
    #     self.username = username

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = QuerySelectField('Access:', 
                                query_factory=role_choice, get_label='name',
                                allow_blank=False)
    team = QuerySelectField('Team:', 
                                query_factory=team_choice, get_label='name',
                                allow_blank=False)
    submit = SubmitField('Submit')


