from datetime import datetime

from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user
from flask_login import login_required

from app import db
from app.dashboard import bp
from app.models import Account


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    accounts = [Account(name='Account 1'), Account(name='Account 2'), Account(name='Account 3')]
    return render_template('dashboard/index.html', title='Dashboard', budget_name='Budget', email='Email', accounts=accounts)


