from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from app import db
from app.models import User, Ticket

def users(count=30):
    fake = Faker()
    i = 0
    while i < count:
        u = User(
            username=fake.user_name(),
            password_hash='password',
            email=fake.email(),
            last_seen=fake.past_date(),
            team_id=1)
        db.session.add(u)
        db.session.commit()
        i += 1


def tickets(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count-1)).first()
        u2 = User.query.offset(randint(0, user_count-1)).first()
        t = Ticket(
            title=fake.name(),
            description=fake.text(),
            timestamp=fake.past_date(),
            team_id = randint(1,3),
            severity_id = randint(1,4),
            author=u,
            ticket_owner=u2,
            status_id=randint(1,3))
        db.session.add(t)
    db.session.commit()

