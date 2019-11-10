from datetime import datetime

from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import current_user
from flask_login import login_required

from app import db
from app.dashboard import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('dashboard/index.html', title='Dashboard')


