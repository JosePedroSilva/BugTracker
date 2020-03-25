import click
from flask.cli import with_appcontext

from app import app, db
from app.models import User, Ticket, Team, Severity, Status, Role, Permission

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()

def create_admin():
    u = User(
            username=admin,
            )
    u.set_password('admin')
    db.session.add(u)
    db.session.commit()