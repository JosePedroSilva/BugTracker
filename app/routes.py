from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_login import logout_user, login_required, current_user, login_user
from app import app, db
from app.forms import LoginForm, RegistrationForm, TicketForm, ChangePassword
from app.models import User, Ticket, Team

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    tickets = Ticket.query.order_by(Ticket.timestamp.desc()).all()
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
@login_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        # , team_id=Team.query.get(form.team.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit() 
        flash(f'User: {form.username.data} created!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@app.route('/mytickets/<username>')
@login_required
def mytickets_raised(username):
    user = User.query.filter_by(username=username).first_or_404()
    tickets = current_user.created_posts().all()
    return render_template('user_tickets.html', user=user, tickets=tickets)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = TicketForm()
    if form.validate_on_submit():
        ticket = Ticket(description=form.ticket.data, 
            author=current_user, title=form.title.data)
        db.session.add(ticket)
        db.session.commit()
        flash('Your ticket has been raised.')
        return redirect(url_for('index'))
    return render_template('create.html', title='Createticket', form=form)

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePassword(current_user.username)
    if form.validate_on_submit():
        user = current_user
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Password changed successfully.')
        return redirect(url_for('settings'))
    return render_template('changePass.html', title='Change Password', form=form)
    
