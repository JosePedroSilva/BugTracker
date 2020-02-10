from datetime import datetime
from app import db

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    tickets = db.relationship('Ticket', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

class Ticket(db.Model):
    __tablename__='tickets'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Ticket {self.id}: {self.description}>'