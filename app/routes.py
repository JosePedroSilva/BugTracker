from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Joe'}
    tickets = [
        {
            'ref': 'BT-1',
            'desc': 'Bug description text'
        },
        {
            'ref': 'BT-2',
            'desc': "My app doesn't work anymore HELP"
        }
        ]
    return render_template('index.html', title='Home', user=user, tickets=tickets)