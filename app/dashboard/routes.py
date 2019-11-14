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

@bp.before_request
def before_request():
    user = User.query.filter_by(username=g.username).first()
    if user is None or user != current_user:
        abort(401)

    budget = Budget.query.filter_by(user=user).filter_by(id=g.budget_id).first_or_404()
    user.last_budget = budget
    db.session.commit()
    
    accounts = Account.query.filter_by(budget=budget).all()

    g.user = user
    g.budget = budget
    g.accounts = accounts


@bp.route('/<username>/budget/', defaults={'budget_id': None})
@bp.route('/<username>/budget/<int:budget_id>')
@login_required
def budget():
    return render_template('dashboard/budget.html', title='Dashboard', user=g.user, budget=g.budget, accounts=g.accounts)


@bp.route('/<username>/budget/<int:budget_id>/reports')
@login_required
def reports():
    return render_template('dashboard/reports.html', title='Dashboard', user=g.user, budget=g.budget, accounts=g.accounts)


@bp.route('/<username>/budget/<int:budget_id>/accounts/', defaults={'account_id': None})
@bp.route('/<username>/budget/<int:budget_id>/accounts/<int:account_id>')
@login_required
def accounts(account_id):
    account = None
    if account_id is not None:
        account = Account.query.filter_by(id=account_id).first()
        if account is None or account.budget.user != current_user:
            abort(401)
    return render_template('dashboard/accounts.html', title='Dashboard', user=g.user, budget=g.budget, accounts=g.accounts, account=account)