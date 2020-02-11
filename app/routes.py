from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_login import logout_user, login_required, current_user, login_user
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Joe'}
    tickets = [
        {
            'ref': 'BT-1',
            'desc': 'Bug description text'
        },
        {
            'ref': 'BT-2',
            'desc': "My app doesn't work anymore HELP"
        }
        ]
    return render_template('index.html', title='HomePage', tickets=tickets)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'User: {form.username.data} created!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/issuesraised/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    tickets = [
    {
        'ref': 'BT-1',
        'desc': 'Ticket raised #1'
    },
    {
        'ref': 'BT-2',
        'desc': "Ticket raised #2"
    }
    ]
    return render_template('issues.html', user=user, tickets=tickets)