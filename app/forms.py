from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from .models import User, Team, Severity, Role, Topic, Status

def team_choice():
    return Team.query

def severity_choice():
    return Severity.query

def user_choice():
    return User.query.filter_by(active=True).order_by(User.username).all()

def role_choice():
    return Role.query

def topic_choice():
    return Topic.query

def status_choice():
    return Status.query

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
    topic = QuerySelectField('Topic:',
                            query_factory=topic_choice, get_label='topic',
                            allow_blank=False)
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

class TakeOwnership(FlaskForm):
    ticket_owner = QuerySelectField('Owner:',
                                    query_factory=user_choice, get_label='username',
                                    allow_blank=True)
    submit = SubmitField('Change Owner')

class ChangeStatus(FlaskForm):
    current_status = QuerySelectField('Status:',
                                    query_factory=status_choice, get_label='status',
                                    allow_blank=False)
    submit3 = SubmitField('Change Status')
    

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = QuerySelectField('Access:', 
                                query_factory=role_choice, get_label='name',
                                allow_blank=False)
    team = QuerySelectField('Team:', 
                                query_factory=team_choice, get_label='name',
                                allow_blank=False)
    active = BooleanField('Active user:  ')
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Username in use, please use a different username.')
        
class CommentForm(FlaskForm):
    body = TextAreaField('New Comment:', validators=[DataRequired(), Length(min=1, max=1000)])
    submit2 = SubmitField('Submit Comment')

class EditTeams(FlaskForm):
    name = StringField('New team name:', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_name, *args, **kwargs):
        super(EditTeams, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            team = Team.query.filter_by(name=self.name.data).first()
            if team is not None:
                raise ValidationError('Team name in use, please use a diferent name.')

class CreateTeamForm(FlaskForm):
    name = StringField('Team name', validators=[DataRequired()])
    submit = SubmitField('Submit')

    # def not running, app is not catching error, it is raising on jinja error
    def validate_team(self, team):
        newteam = Team.query.filter_by(name=team.data).first()
        if newteam is not None:
            raise ValidationError('Team already created')


class CreateTopicForm(FlaskForm):   
    topic = StringField('New topic', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_topic(self, topic):
        topic = Topic.query.filter_by(topic=topic.data).first()
        if topic is not None:
            raise ValidationError('Topic already created')


class EditTopicsForm(FlaskForm):
    topic = StringField('New topic name:', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_topic, *args, **kwargs):
        super(EditTopicsForm, self).__init__(*args, **kwargs)
        self.original_topic = original_topic

    def validate_topic(self, topic):
        if topic.data != self.original_topic:
            topic = Topic.query.filter_by(topic=self.topic.data).first()
            if topic is not None:
                raise ValidationError('Topic already created, please choose a diferent topic name.')

class SearchForm(FlaskForm):
    q = StringField(('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)