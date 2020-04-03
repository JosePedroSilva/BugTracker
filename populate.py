from app import db
from sqlalchemy.exc import IntegrityError
from app.models import User, Role, Status, Topic, Team

def create_admin():
    u = User(username='firstAdmin', role_id=3)
    u.set_password('firstAdmin')
    db.session.add(u)
    db.session.commit()

def insert_teams():    
        teams = ['Front Office', 'Middle Office', 'Back Office', 'Support']
        for t in teams:
            team = Team.query.filter_by(name=t).first()
            if team is None:
                team = Team(name=t)
            db.session.add(team)
        db.session.commit()

class Permission:
    RAISE = 1
    COMMENT = 2
    OWNER = 4
    CLOSE = 8
    ADMIN = 16

def insert_roles():
    roles = {
        'User': [Permission.RAISE, Permission.COMMENT],
        'Manager': [Permission.RAISE, Permission.COMMENT,
                    Permission.OWNER, Permission.CLOSE],
        'Administrator': [Permission.RAISE, Permission.COMMENT,
                            Permission.OWNER, Permission.CLOSE,
                            Permission.ADMIN],}
    for r in roles:
        role = Role.query.filter_by(name=r).first()
        if role is None:
            role = Role(name=r)
        role.reset_permissions()
        for perm in roles[r]:
            role.add_permission(perm)
        db.session.add(role)
    db.session.commit()

def insert_status():
    status = ['created', 'in progress', 'closed']
    for s in status:
        stat = Status.query.filter_by(status=s).first()
        if stat is None:
            stat = Status(status=s)
        db.session.add(stat)
    db.session.commit()

def insert_topics():
    topicsList = ['Report', 'Bug', 'Fix', 'Implementation']
    for t in topicsList:
        top = Topic.query.filter_by(topic=t).first()
        if top is None:
            top = Topic(topic=t)
        db.session.add(top)
    db.session.commit()


db.create_all()

insert_teams()
insert_roles()
insert_status()
insert_topics()
create_admin()