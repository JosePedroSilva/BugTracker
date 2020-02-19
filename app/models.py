from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    tickets = db.relationship('Ticket',foreign_keys='Ticket.user_id', 
                                backref='author', lazy='dynamic') # Defines the user has the author of the issue
    owner = db.relationship('Ticket', foreign_keys='Ticket.owner_id', 
                                backref='ticket_owner', lazy='dynamic') # Defines the user has the person in charge/handling the issue
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def created_tickets(self):
        created = Ticket.query.filter_by(user_id=self.id)
        return created.order_by(Ticket.timestamp.desc())

    def owner_tickets(self):
        owner = Ticket.query.filter_by(owner_id=self.id)
        return owner.order_by(Ticket.timestamp.desc())

    def created_count(self):
        count = Ticket.query.filter_by(user_id=self.id).count()
        return count

    


class Ticket(db.Model):
    __tablename__='tickets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    description = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # Defines the user has the author of the issue
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id')) # Defines the user has the person in charge/handling the issue
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    severity_id = db.Column(db.Integer, db.ForeignKey('severity.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))

    def __repr__(self):
        return f'<Ticket {self.id}: {self.description}>'

    def count_total():
        total = Ticket.query.count()
        return total
    
    def count_per_team(team_id):
        team_total = Ticket.query.filter_by(team_id=team_id).count()
        return team_total


class Team(db.Model):
    __tablename__='teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    members = db.relationship('User', backref='team_members')
    team_tickets = db.relationship('Ticket', backref='team_tickets')

    def __repr__(self):
        return f'{self.name}'

class Severity(db.Model):
    __tablename__='severity'
    id = db.Column(db.Integer, primary_key=True)
    degree = db.Column(db.String(32), unique=True)
    tickets_sev = db.relationship('Ticket', backref='ticket_severity')
    
    def __repr__(self):
        return f'{self.degree}'

class Status(db.Model):
    __tablename__='status'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(32), unique=True)
    tickets_status = db.relationship('Ticket', backref='ticket_status')

    def __repr__(self):
        return f'{self.status}'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))