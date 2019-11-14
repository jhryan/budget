from datetime import datetime

from flask import abort
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


@bp.route('/<username>/budget/', defaults={'budget_id': None})
@bp.route('/<username>/budget/<int:budget_id>')
@login_required
def budget(username, budget_id):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('main.index'))
    if user != current_user:
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
    return render_template('dashboard/budget.html', title='Dashboard', budget=budget, user=user, accounts=accounts)


@bp.route('/<username>/budget/<int:budget_id>/reports')
@login_required
def reports(username, budget_id):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('main.index'))
    if user != current_user:
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
    return render_template('dashboard/reports.html', title='Dashboard', budget=budget, user=user, accounts=accounts)


@bp.route('/<username>/budget/<int:budget_id>/accounts')
@login_required
def accounts(username, budget_id):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.')
        return redirect(url_for('main.index'))
    if user != current_user:
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
    return render_template('dashboard/accounts.html', title='Dashboard', budget=budget, user=user, accounts=accounts)