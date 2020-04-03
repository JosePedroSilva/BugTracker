from app import db
from app.models import User

def create_admin():
    u = User(username='firstAdmin')
    u.set_password('firstAdmin')
    db.session.add(u)
    db.session.commit()

create_admin()