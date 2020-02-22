from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_login import logout_user, login_required, current_user, login_user
import pygal
from pygal.style import CleanStyle
from app import app, db
from app.forms import LoginForm, RegistrationForm, TicketForm, ChangePassword
from app.models import User, Ticket, Team

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    tickets = Ticket.query.order_by(Ticket.timestamp.desc()).paginate(
        page, app.config['TICKETS_PER_PAGE'], False)
    next_url = url_for('index', page=tickets.next_num) \
        if tickets.has_next else None
    prev_url = url_for('index', page=tickets.prev_num) \
        if tickets.has_prev else None
    return render_template('index.html', title='HomePage', 
                            tickets=tickets.items, next_url=next_url,
                           prev_url=prev_url)


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
        user = User(username=form.username.data, 
                        email=form.email.data, team_id=form.team.data.id)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit() 
        flash(f'User: {form.username.data} created!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user_ticket_stats/<username>')
@login_required
def user_ticket_stats(username):
    user = User.query.filter_by(username=username).first_or_404()
    team_elements = User.query.filter_by(team_id=current_user.team_id).all()
    return render_template('user.html', user=user, title='userTicketStats', 
                            team_elements=team_elements)

@app.route('/mytickets/<username>')
@login_required
def mytickets_raised(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    tickets = current_user.created_tickets().paginate(
        page, app.config['TICKETS_PER_PAGE'], False)
    created_count = current_user.created_count()
    next_url = url_for('mytickets_raised', page=tickets.next_num, username=username) \
        if tickets.has_next else None
    prev_url = url_for('mytickets_raised', page=tickets.prev_num, username=username) \
        if tickets.has_prev else None
    return render_template('user_tickets.html', title='mytickets', 
                            user=user, tickets=tickets.items, 
                            created_count=created_count, next_url=next_url,
                           prev_url=prev_url)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = TicketForm()
    if form.validate_on_submit():
        ticket = Ticket(
            description=form.ticket.data, 
            author=current_user, 
            title=form.title.data,
            team_id=form.team.data.id, 
            severity_id=form.severity.data.id,
            status_id=1)
        db.session.add(ticket)
        db.session.commit()
        flash('Your ticket has been raised.')
        return redirect(url_for('index'))
    return render_template('create.html', title='Createticket', form=form)

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html', title='settings')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePassword(current_user.username)
    if form.validate_on_submit():
        user = current_user
        # if not user.check_password(form.currentPassword.data):
        #     flash('Invalid passsword')
        #     return redirect('settings')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Password changed successfully.')
        return redirect(url_for('settings'))
    return render_template('changePass.html', title='Change Password', form=form)

@app.route('/ticket/<id>', methods=['GET', 'POST'])
@login_required
def ticket_view(id):
    ticket = Ticket.query.filter_by(id=id).first_or_404()
    return render_template('ticket.html', ticket=ticket, title='ticket')
    

@app.route('/admin_overview')
@login_required
def overview():
    tickets_total = Ticket.count_total()
    tickets_per_team = Ticket.count_per_team()
    tickets_per_status = Ticket.count_per_status()
    tickets_per_sev = Ticket.count_per_severity()
    team_chart = pygal.Pie(style=CleanStyle)
    team_chart.title = 'Team count'
    for k,v in tickets_per_team.items():
        team_chart.add(k, v)
    team_chart = team_chart.render_data_uri()
    status_chart = pygal.Pie(half_pie=True, style=CleanStyle)
    status_chart.title = 'Status count'
    for k,v in tickets_per_status.items():
        status_chart.add(k,v)
    status_chart = status_chart.render_data_uri()
    severity_chart = pygal.Pie()
    severity_chart.title = 'Priority count'
    for k,v in tickets_per_sev.items():
        severity_chart.add(k,v)
    severity_chart = severity_chart.render_data_uri()
    return render_template('overview.html', title='Overview', 
                            tickets_per_team=tickets_per_team,
                           tickets_total=tickets_total, tickets_per_status=tickets_per_status,
                           tickets_per_sev=tickets_per_sev, team_chart=team_chart,
                           status_chart=status_chart, severity_chart=severity_chart)


