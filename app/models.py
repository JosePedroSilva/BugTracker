from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login
from .search import add_to_index, query_index

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


class User(UserMixin, db.Model):
    """Creates User model"""
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
    comments = db.relationship('Comment', backref='comment_author', lazy='dynamic')
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def created_tickets(self):
        """Returns the tickets that the user has open"""
        created = Ticket.query.filter_by(user_id=self.id)
        return created.order_by(Ticket.timestamp.desc())

    def owner_tickets(self):
        """Returns the tickets that the user is handling"""
        owner = Ticket.query.filter_by(owner_id=self.id)
        return owner.order_by(Ticket.timestamp.desc())

    def created_count(self):
        count = Ticket.query.filter_by(user_id=self.id).filter(Ticket.status_id < 3).count()
        return count

    def handling_count(self):
        count = Ticket.query.filter_by(owner_id=self.id).filter(Ticket.status_id < 3).count()
        return count

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)


class Ticket(SearchableMixin, db.Model):
    """Creates ticket model"""
    __searchable__=['title', 'description', 'id']
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
    comments = db.relationship('Comment', backref='comment_ticket', lazy='dynamic')
    topics = db.Column(db.Integer, db.ForeignKey('topics.id'))

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
    """Creates role model"""
    __tablename__='roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
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
        """Populates roles
        Upon first time implementation run Role.insert_roles() to populate the user roles
        """

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

    @staticmethod
    def insert_teams():    
        """Populates teams
            Upon first time implementation run Team.insert_teams() to populate the user teams
            To change the team name just alter the teams variable
        """

        teams = ['Front Office', 'Middle Office', 'Back Office', 'Support']
        for t in teams:
            team = Team.query.filter_by(name=t).first()
            if team is None:
                team = Team(name=t)
            db.session.add(team)
        db.session.commit()

class Severity(db.Model):
    __tablename__='severity'
    id = db.Column(db.Integer, primary_key=True)
    degree = db.Column(db.String(32), unique=True)
    tickets_sev = db.relationship('Ticket', backref='ticket_severity')

    def __repr__(self):
        return f'{self.degree}'

    @staticmethod
    def insert_severity():
        """Populates severity
            Upon first time implementation run Severity.insert_severity() to populate the ticket severity
            To change the severity name just alter the status sevs
        """
        sevs = ['low', 'medium', 'high', 'critical']
        for s in sevs:
            sev = Severity.query.filter_by(degree=s).first()
            if sev is None:
                sev = Severity(degree=s)
            db.session.add(sev)
        db.session.commit()

class Status(db.Model):
    __tablename__='status'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(32), unique=True)
    tickets_status = db.relationship('Ticket', backref='ticket_status')

    def __repr__(self):
        return f'{self.status}'

    @staticmethod
    def insert_status():
        """Populates status
            Upon first time implementation run Status.insert_status() to populate the ticket status
            To change the status name just alter the status variable
        """
        status = ['created', 'in progress', 'closed']
        for s in status:
            stat = Status.query.filter_by(status=s).first()
            if stat is None:
                stat = Status(status=s)
            db.session.add(stat)
        db.session.commit()

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))

class Topic(db.Model):
    __tablename__='topics'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(32), unique=True)
    ticket_topic = db.relationship('Ticket', backref='ticket_topic')

    @staticmethod
    def insert_topics():
        """
        Populates topics
        """
        topicsList = ['Report', 'Bug', 'Fix', 'Implementation']
        for t in topicsList:
            top = Topic.query.filter_by(topic=t).first()
            if top is None:
                top = Topic(topic=t)
            db.session.add(top)
        db.session.commit()

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

