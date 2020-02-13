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
    

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def created_posts(self):
        created = Ticket.query.filter_by(user_id=self.id)
        return created.order_by(Ticket.timestamp.desc())


class Ticket(db.Model):
    __tablename__='tickets'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # Defines the user has the author of the issue
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id')) # Defines the user has the person in charge/handling the issue

    def __repr__(self):
        return f'<Ticket {self.id}: {self.description}>'

    # def take_ownership(self, user):
    #     self.owner_id.append(user)

class Severity():
    pass

@login.user_loader
def load_user(id):
    return User.query.get(int(id))