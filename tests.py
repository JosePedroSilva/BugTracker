from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Ticket, Role, Severity, Team, Status, Comment

class UserModelCase(unittest.TestCase):
    def setUp(self):
        """Creates db"""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:2427@localhost/bugtest'
        db.create_all()

    def tearDown(self):
        """Removes db"""
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        """ Password hashing test """
        u = User(username='testSubject')
        u.set_password('house')
        self.assertFalse(u.check_password('build'))
        self.assertTrue(u.check_password('house'))

    def test_ticket(self):
        """ User, ticket and comment test """
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

        c1 = Comment(body='Comment #1', timestamp=now, author_id=1, ticket_id=1)
        c2 = Comment(body='Comment #2', timestamp=now, author_id=2, ticket_id=2)
        c3 = Comment(body='Comment #3', timestamp=now, author_id=3, ticket_id=3)
        c4 = Comment(body='Comment #4', timestamp=now, author_id=4, ticket_id=4)
        db.session.add_all([c1, c2, c3, c4])
        db.session.commit()

    def roles_pop(self):
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

    def teams_pop(self):
        insert_teams()

    def sev_pop(self):
        insert_severity()
    
    def stat_pop(self):
        insert_status()



if __name__ == '__main__':
    unittest.main(verbosity=2)
