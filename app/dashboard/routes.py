from datetime import datetime
from dateutil import relativedelta
from decimal import Decimal

from flask import abort
from flask import current_app
from flask import flash
from flask import g
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required

from app import db
from app.dashboard import bp
from app.dashboard.forms import AddAccountForm
from app.dashboard.forms import AddCategoryForm
from app.dashboard.forms import AddCategoryGroupForm
from app.dashboard.forms import EditCategoryForm
from app.dashboard.forms import EditCategoryGroupForm
from app.models import Account
from app.models import AssetType
from app.models import Budget
from app.models import Journal
from app.models import Posting
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
    
    category_groups = Account.query.filter_by(budget=budget).filter(Account.parent.has(name='Budget')).all()
    category_group_names = [category_group.name for category_group in category_groups]
    accounts = Account.query.filter_by(budget=budget).filter(Account.name != 'Budget').filter(~Account.parent.has(Account.name =='Budget')).filter(~Account.parent.has(Account.name.in_(category_group_names))).all()
    
    g.user = user
    g.budget = budget
    g.accounts = accounts


@bp.route('/<username>/budget/', defaults={'budget_id': None, 'month': datetime.utcnow().strftime('%Y%m')})
@bp.route('/<username>/budget/<int:budget_id>', defaults={'month': datetime.utcnow().strftime('%Y%m')})
@bp.route('/<username>/budget/<int:budget_id>/<month>')
@login_required
def budget(month):
    category_groups = Account.query.filter_by(budget=g.budget).filter(Account.parent.has(name='Budget')).all()
    return render_template('dashboard/budget.html', title='Dashboard', month=datetime.strptime(month, '%Y%m'), add_account_form=AddAccountForm(g.budget), category_group_form=AddCategoryGroupForm(g.budget), edit_category_group_form=EditCategoryGroupForm(g.budget, ''), add_category_form=AddCategoryForm(g.budget, ''), edit_category_form=EditCategoryForm(g.budget, '', ''), user=g.user, budget=g.budget, accounts=g.accounts, category_groups=category_groups)


@bp.route('/<username>/budget/<int:budget_id>/<month>/prev_month')
@login_required
def budget_prev_month(month):
    prev_month = datetime.strptime(month, '%Y%m') - relativedelta.relativedelta(months=1)
    return redirect(url_for('dashboard.budget', month=prev_month.strftime('%Y%m')))


@bp.route('/<username>/budget/<int:budget_id>/<month>/next_month')
@login_required
def budget_next_month(month):
    next_month = datetime.strptime(month, '%Y%m') + relativedelta.relativedelta(months=1)
    return redirect(url_for('dashboard.budget', month=next_month.strftime('%Y%m')))


@bp.route('/<username>/budget/<int:budget_id>/<month>/budget_amount', methods=['POST'])
@login_required
def budget_amount(month):
    category_id = request.form['category_id']
    amount = Decimal(request.form['amount'])

    month = datetime.strptime(month, '%Y%m')
    default_asset_type = AssetType.query.filter_by(name='USD').first()

    category = Account.query.filter_by(id=category_id).first()
    budget_equity = Account.query.filter_by(budget=g.budget).filter_by(type='Equity').filter_by(name='Budget Equity').first()

    if amount != category.balance():
        # only submit posting for the difference in budgeted amount
        amount -= category.balance()
    
        journal_entry = Journal(date=month)

        category_posting = Posting(account=category, journal_entry=journal_entry, amount=amount, asset_type=default_asset_type)
        budget_equity_posting = Posting(account=budget_equity, journal_entry=journal_entry, amount=-amount, asset_type=default_asset_type)


        db.session.add(journal_entry)
        db.session.add(category_posting)
        db.session.add(budget_equity_posting)
        
        db.session.commit()

    return jsonify(data={'category_balance': str(category.balance()), 'group_balance': str(category.parent.balance())})


@bp.route('/<username>/budget/<int:budget_id>/reports')
@login_required
def reports():
    return render_template('dashboard/reports.html', title='Dashboard', add_account_form=AddAccountForm(g.budget), user=g.user, budget=g.budget, accounts=g.accounts)


@bp.route('/<username>/budget/<int:budget_id>/accounts/', defaults={'account_id': None})
@bp.route('/<username>/budget/<int:budget_id>/accounts/<int:account_id>')
@login_required
def accounts(account_id):
    account = None
    if account_id is not None:
        account = Account.query.filter_by(id=account_id).first()
        if account is None or account.budget.user != current_user:
            abort(401)
    return render_template('dashboard/accounts.html', title='Dashboard', add_account_form=AddAccountForm(g.budget), user=g.user, budget=g.budget, accounts=g.accounts, account=account)


@bp.route('/<username>/budget/<int:budget_id>/accounts/add_account', methods=['POST'])
@login_required
def add_account():
    form = AddAccountForm(g.budget)
    if form.validate_on_submit():
        if form.account_type.data in ('Checking', 'Savings', 'Cash'):
            account_type = 'Asset'
        else:
            account_type = 'Liability'
        account = Account(name=form.account_name.data, type=account_type, budget=g.budget)
        db.session.add(account)
        db.session.commit()
        flash('Account successfully created!')
        return jsonify(data={'message': 'success'})
    return render_template('dashboard/add_account_form.html', add_account_form=form)


@bp.route('/<username>/budget/<int:budget_id>/add_category_group', methods=['POST'])
@login_required
def add_category_group():
    form = AddCategoryGroupForm(g.budget)
    if form.validate_on_submit():
        budget_account = Account.query.filter_by(budget=g.budget).filter_by(name='Budget').first()
        account = Account(name=form.category_group.data, type='Asset', budget=g.budget, parent=budget_account)
        db.session.add(account)
        db.session.commit()
        return jsonify(data={'message': 'success'})
    return render_template('dashboard/add_category_group_form.html', category_group_form=form)


@bp.route('/<username>/budget/<int:budget_id>/edit_category_group/<category_group_name>', methods=['POST'])
@login_required
def edit_category_group(category_group_name):
    form = EditCategoryGroupForm(g.budget, category_group_name)
    category_group = Account.query.filter_by(budget=g.budget).filter_by(name=category_group_name).first()
    if form.validate_on_submit():
        category_group.name = form.new_category_group.data
        db.session.commit()
        return jsonify(data={'message': 'success'})
    form.new_category_group.label.text = category_group_name
    return render_template('dashboard/edit_category_group_form.html', edit_category_group_form=form, category_group=category_group)


@bp.route('/<username>/budget/<int:budget_id>/edit_category_group/<category_group_name>/delete', methods=['POST'])
@login_required
def delete_category_group(category_group_name):
    Account.query.filter_by(budget=g.budget).filter_by(name=category_group_name).delete()
    db.session.commit()
    return jsonify(data={'message': 'success'})


@bp.route('/<username>/budget/<int:budget_id>/<category_group_name>/add_category', methods=['POST'])
@login_required
def add_category(category_group_name):
    category_group = Account.query.filter_by(budget=g.budget).filter_by(name=category_group_name).first()
    form = AddCategoryForm(g.budget, category_group.name)
    if form.validate_on_submit():
        category = Account.query.filter_by(budget=g.budget).filter(Account.parent == category_group).filter_by(name=form.category.data).first()
        if category is not None:
            form.category.errors.append('This category name is already in use.')
            return render_template('dashboard/add_category_form.html', add_category_form=form, category_group=category_group)
        account = Account(name=form.category.data, type='Asset', budget=g.budget, parent=category_group)
        db.session.add(account)
        db.session.commit()
        return jsonify(data={'message': 'success'})
    return render_template('dashboard/add_category_form.html', add_category_form=form, category_group=category_group)


@bp.route('/<username>/budget/<int:budget_id>/<category_group_name>/edit_category/<category_name>', methods=['POST'])
@login_required
def edit_category(category_group_name, category_name):
    form = EditCategoryForm(g.budget, category_group_name, category_name)
    category_group = Account.query.filter_by(budget=g.budget).filter_by(name=category_group_name).first()
    category = Account.query.filter_by(budget=g.budget).filter(Account.parent.has(name=category_group_name)).filter_by(name=category_name).first()
    if form.validate_on_submit():
        category.name = form.new_category.data
        db.session.commit()
        return jsonify(data={'message': 'success'})
    form.new_category.label.text = category_name
    return render_template('dashboard/edit_category_form.html', edit_category_form=form, category_group=category_group, category=category)


@bp.route('/<username>/budget/<int:budget_id>/<category_group_name>/edit_category/<category_name>/delete', methods=['POST'])
@login_required
def delete_category(category_group_name, category_name):
    Account.query.filter_by(budget=g.budget).filter(Account.parent.has(name=category_group_name)).filter_by(name=category_name).delete(synchronize_session='fetch')
    db.session.commit()
    return jsonify(data={'message': 'success'}) 


@bp.route('/<username>/budget/<int:budget_id>/change_category_group', methods=['POST'])
@login_required
def change_category_group():
    category = Account.query.filter_by(budget=g.budget).filter(Account.parent.has(name=request.form['old_category_group'])).filter_by(name=request.form['category']).first()
    new_category_group = Account.query.filter_by(budget=g.budget).filter(Account.parent.has(name='Budget')).filter_by(name=request.form['new_category_group']).first()
    category.parent = new_category_group
    db.session.commit()
    return jsonify(data={'message': 'success'}) 