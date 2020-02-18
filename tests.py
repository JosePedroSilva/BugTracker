from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Ticket

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:2427@localhost/bugtest'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='testSubject')
        u.set_password('house')
        self.assertFalse(u.check_password('build'))
        self.assertTrue(u.check_password('house'))

    def test_ticket_author(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        now = datetime.utcnow()

        t1 = Ticket(description="ticket from john", author=u1,
                        timestamp=now + timedelta(seconds=1))
        t2 = Ticket(description="ticket from susan", author=u2,
                timestamp=now + timedelta(seconds=4))
        t3 = Ticket(description="ticket from mary", author=u3,
                    timestamp=now + timedelta(seconds=3))
        t4 = Ticket(description="ticket from david", author=u4,
                timestamp=now + timedelta(seconds=2))
        db.session.add_all([t1, t2, t3, t4])
        db.session.commit()


if __name__ == '__main__':
    unittest.main(verbosity=2)
