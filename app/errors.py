from flask import render_template
from flask_login import login_required
from app import app, db

@app.errorhandler(404)
@login_required
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
@login_required
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500