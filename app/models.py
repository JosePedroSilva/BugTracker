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
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

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

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)


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

    def count_per_team():
        team_total = {Team.query.filter_by(id=t).value(Team.name):
                        Ticket.query.filter_by(team_id=t).count()
                        for t in range(1, Team.query.count()+1)}
        return team_total

    def count_per_status():
        status_count = {Status.query.filter_by(id=s).value(Status.status):
                        Ticket.query.filter_by(status_id=s).count()
                        for s in range(1, Status.query.count()+1)}
        return status_count

    def count_per_severity():
        sev_count = {Severity.query.filter_by(id=s).value(Severity.degree):
                        Ticket.query.filter_by(severity_id=s).count()
                        for s in range(1, Severity.query.count()+1)}
        return sev_count


class Permission:
    RAISE = 1
    COMMENT = 2
    OWNER = 4
    CLOSE = 8
    ADMIN = 16  


class Role(db.Model):
    __tablename__='roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return f'<Role {self.name}>'

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm
    
    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.RAISE, Permission.COMMENT],
            'Manager': [Permission.RAISE, Permission.COMMENT,
                        Permission.OWNER, Permission.CLOSE],
            'Administrator': [Permission.RAISE, Permission.COMMENT,
                                Permission.OWNER, Permission.CLOSE,
                                Permission.ADMIN],}
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

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