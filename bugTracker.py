"""BugTracker Flask application.
This is a demo Flask application of a ticket management system with multiple user level
"""


from app import app, db
from app.models import User, Ticket, Team, Severity, Status, Role, Permission, Topic

@app.shell_context_processor
def make_shell_context():
    return{'db':db, 'User':User, 'Ticket':Ticket,
    'Team':Team, 'Severity': Severity, 'Status': Status,
    'Role': Role, 'Permission':Permission, 'Topic':Topic}