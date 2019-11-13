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


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


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
        budget = Budget.query.filter_by(user=user).first()
    else:
        budget = Budget.query.filter_by(user=user, id=budget_id).first()
    if budget is None:
        abort(404)
    
    accounts = Account.query.filter_by(budget=budget).all()
    return render_template('dashboard/budget.html', title='Dashboard', budget_name=budget.name, email=user.email, accounts=accounts)


