import pygal
from flask import url_for
from werkzeug.urls import url_parse
from flask_login import current_user
from .models import User, Ticket

class GraphicalGauge:
    
    def gauge_author(user):
        myTicketsTotal = Ticket.query.filter_by(user_id=user.id).count()
        myTicketsCreated = Ticket.query.filter_by(user_id=user.id, status_id=1).count()
        myTicketsInProgress = Ticket.query.filter_by(user_id=user.id, status_id=2).count()
        myTicketsClosed = Ticket.query.filter_by(user_id=user.id, status_id=3).count()
        gauge = pygal.SolidGauge(inner_radius=0.70, width=2000)
        gauge.add('Total', [{'value': myTicketsTotal, 'max_value': myTicketsTotal}])
        gauge.add('Created', [{'value': myTicketsCreated, 'max_value': myTicketsTotal}])
        gauge.add('In progress', [{'value': myTicketsInProgress, 'max_value': myTicketsTotal}])
        gauge.add('Closed', [{'value': myTicketsClosed, 'max_value': myTicketsTotal}])
        gauge = gauge.render_data_uri()
        return gauge

    def tickets_per_team():
        tickets_per_team = Ticket.count_per_team()
        team_chart = pygal.Pie(width=2000)
        team_chart.title = 'Team count'
        for k,v in tickets_per_team.items():
            team_chart.add(k, v)
        team_chart = team_chart.render_data_uri()
        return team_chart

    def tickets_per_status():
        tickets_per_status = Ticket.count_per_status()
        status_chart = pygal.Pie(width=2000)
        status_chart.title = 'Status count'
        for k,v in tickets_per_status.items():
            status_chart.add(k,v)
        status_chart = status_chart.render_data_uri()
        return status_chart

    def tickets_per_sev():
        tickets_per_sev = Ticket.count_per_severity()
        severity_chart = pygal.Pie(width=2000)
        severity_chart.title = 'Priority count'
        for k,v in tickets_per_sev.items():
            severity_chart.add(k,v)
        severity_chart = severity_chart.render_data_uri()
        return severity_chart