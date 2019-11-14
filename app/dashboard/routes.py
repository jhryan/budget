from datetime import datetime

from flask import abort
from flask import current_app
from flask import g
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user
from flask_login import login_required

from app import db
from app.dashboard import bp
from app.models import Account
from app.models import Budget
from app.models import User


@bp.url_defaults
def add_url_defaults(endpoint, values):
    if 'username' not in values and g.username:
        if current_app.url_map.is_endpoint_expecting(endpoint, 'username'):
            values['username'] = g.username
    if 'budget_id' not in values and g.budget_id:
        if current_app.url_map.is_endpoint_expecting(endpoint, 'budget_id'):
            values['budget_id'] = g.budget_id


@bp.url_value_preprocessor
def pull_url_values(endpoint, values):
    g.username = values.pop('username', None)
    g.budget_id = values.pop('budget_id', None)

    if g.username is None:
        g.username = current_user.username
    if g.budget_id is None:
        last_budget_id = User.query.filter_by(username=g.username).first().last_budget_id
        g.budget_id = last_budget_id if last_budget_id else Budget.query.join(Budget, User.budgets).first()


def authenticate(username, budget_id):
    user = User.query.filter_by(username=username).first()
    if user is None or user != current_user:
        abort(401)

    if budget_id is None:
        if user.last_budget is None:
            budget = Budget.query.filter_by(user=user).first_or_404()
        else:
            budget = user.last_budget
    else:
        budget = Budget.query.filter_by(user=user).filter_by(id=budget_id).first_or_404()
        user.last_budget = budget
        db.session.commit()
    
    accounts = Account.query.filter_by(budget=budget).all()
    return user, budget, accounts


@bp.route('/<username>/budget/', defaults={'budget_id': None})
@bp.route('/<username>/budget/<int:budget_id>')
@login_required
def budget():
    user, budget, accounts = authenticate(g.username, g.budget_id)
    return render_template('dashboard/budget.html', title='Dashboard', user=user, budget=budget, accounts=accounts)


@bp.route('/<username>/budget/<int:budget_id>/reports')
@login_required
def reports():
    user, budget, accounts = authenticate(g.username, g.budget_id)
    return render_template('dashboard/reports.html', title='Dashboard', user=user, budget=budget, accounts=accounts)


@bp.route('/<username>/budget/<int:budget_id>/accounts')
@login_required
def accounts():
    user, budget, accounts = authenticate(g.username, g.budget_id)
    return render_template('dashboard/accounts.html', title='Dashboard', user=user, budget=budget, accounts=accounts)