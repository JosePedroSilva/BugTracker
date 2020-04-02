from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_login import logout_user, login_required, current_user, login_user
import pygal
from pygal.style import CleanStyle, BlueStyle
from . import app, db
from .forms import LoginForm, RegistrationForm, TicketForm, ChangePassword, EditProfileForm, TakeOwnership, CommentForm, ChangeStatus
from .models import User, Ticket, Team, Role, Comment, Topic
from .decorators import admin_required, permission_required
from .graph import GraphicalGauge

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    try:
        # if there is no data related to that user this block clear the graphic error
        gauge_author = GraphicalGauge.gauge_author(user)
    except ZeroDivisionError:
        gauge_author = None
    page = request.args.get('page', 1, type=int)
    tickets = Ticket.query.filter_by(owner_id=None).order_by(Ticket.timestamp.desc()).paginate(
        page, app.config['TICKETS_PER_PAGE'], False)
    next_url = url_for('index', page=tickets.next_num) \
        if tickets.has_next else None
    prev_url = url_for('index', page=tickets.prev_num) \
        if tickets.has_prev else None
    return render_template('index.html', title='HomePage',
                            tickets=tickets.items, next_url=next_url,
                           prev_url=prev_url, user=user, gauge_author=gauge_author)

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

##########################
#   Tickets
##########################

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
            status_id=1,
            topics=form.topic.data.id)
        db.session.add(ticket)
        db.session.commit()
        flash('Your ticket has been raised.')
        return redirect(url_for('index'))
    return render_template('create.html', title='Createticket', form=form)

@app.route('/ticket/<id>', methods=['GET', 'POST'])
@login_required
def ticket_view(id):
    form = TakeOwnership()
    commentForm = CommentForm()
    statusForm = ChangeStatus()
    comments = Comment.query.filter_by(ticket_id=id).order_by(Comment.timestamp.desc()).all()
    ticket = Ticket.query.filter_by(id=id).first_or_404()
    if form.submit.data and form.validate():
        ticket.owner_id = form.ticket_owner.data.id
        ticket.status_id = 2
        db.session.commit()
        flash(f'Ticket attributed to {ticket.ticket_owner.username}')
        return redirect(url_for('ticket_view', id=ticket.id))
    elif statusForm.submit3.data and statusForm.validate():
        ticket.status_id = statusForm.current_status.data.id
        db.session.commit()
        flash('Ticket status updated')
        return redirect(url_for('ticket_view', id=ticket.id))
    elif commentForm.submit2.data and commentForm.validate():
        comment = Comment(body=commentForm.body.data, ticket_id=ticket.id, 
                            author_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added')
        return redirect(url_for('ticket_view', id=ticket.id))
    elif request.method == 'GET':
        form.ticket_owner.data = ticket.ticket_owner
        statusForm.current_status.data = ticket.ticket_status
    return render_template('ticket.html', ticket=ticket, title='ticket', 
                            form=form, commentForm=commentForm, comments=comments,
                            statusForm=statusForm)


@app.route('/mytickets/<username>')
@login_required
def mytickets_raised(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    tickets = current_user.created_tickets().filter(Ticket.status_id < 3).paginate(
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


@app.route('/tickets_handling/<username>')
@login_required
def handling(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    tickets = current_user.owner_tickets().filter(Ticket.status_id < 3).paginate(
        page, app.config['TICKETS_PER_PAGE'], False)
    created_count = current_user.handling_count()
    next_url = url_for('mytickets_raised', page=tickets.next_num, username=username) \
        if tickets.has_next else None
    prev_url = url_for('mytickets_raised', page=tickets.prev_num, username=username) \
        if tickets.has_prev else None
    return render_template('user_handling.html', title='handling',
                            user=user, tickets=tickets.items,
                            created_count=created_count, next_url=next_url,
                           prev_url=prev_url)

##########################
#   Options
##########################

@app.route('/settings/<username>')
@login_required
def settings(username):
    user = User.query.filter_by(username=username).first_or_404()
    team_elements = User.query.filter_by(team_id=current_user.team_id).all()
    return render_template('settings.html', user=user, title='settings',
                            team_elements=team_elements)


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

##########################
#   Admin required
##########################

@app.route('/admin_overview')
@login_required
@admin_required
def overview():
    tickets_total = Ticket.count_total()
    tickets_per_team = GraphicalGauge.tickets_per_team()
    tickets_per_status = GraphicalGauge.tickets_per_status()
    tickets_per_sev = GraphicalGauge.tickets_per_sev()   
    return render_template('overview.html', title='Overview',
                            tickets_per_team=tickets_per_team,
                           tickets_total=tickets_total, tickets_per_status=tickets_per_status,
                           tickets_per_sev=tickets_per_sev)

@app.route('/register', methods=['GET', 'POST'])
@login_required
@admin_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                        email=form.email.data, team_id=form.team.data.id,
                        role_id=form.role.data.id)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'User: {form.username.data} created!')
        return redirect(url_for('register'))
    return render_template('register.html', title='Register', form=form)


@app.route('/all_tickets', methods=['GET', 'POST'])
@login_required
@admin_required
def all_tickets():
    page = request.args.get('page', 1, type=int)
    tickets = Ticket.query.order_by(Ticket.timestamp.desc()).paginate(
        page, app.config['TICKETS_PER_PAGE'], False)
    next_url = url_for('all_tickets', page=tickets.next_num) \
        if tickets.has_next else None
    prev_url = url_for('all_tickets', page=tickets.prev_num) \
        if tickets.has_prev else None
    return render_template('allTickets.html', title='AllTickets',
                            tickets=tickets.items, next_url=next_url,
                            prev_url=prev_url)


@app.route('/choice_profile')
@login_required
@admin_required
def choice_profile():
    users = User.query.order_by(User.username.asc())
    return render_template('user_profile.html', title='Users', users=users)

@app.route('/edit_profile/<username>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile(username):
    user = User.query.filter_by(username=username).first()
    form = EditProfileForm(user.username)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role_id = form.role.data.id
        user.team_id = form.team.data.id
        db.session.commit()
        flash(f'Your changes on user {user.username} have been saved.')
        return redirect(url_for('choice_profile'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.role.data = user.role
        form.team.data = user.team_members
    return render_template('user_edit.html',title='edit_profile', 
                            form=form, user=user)


@app.route('/edit_teams')
@login_required
@admin_required
def edit_teams():
    teams = Team.query.order_by(Team.id.asc())
    return render_template('admin_team_view.html', title='edit_team', 
                            teams=teams)

