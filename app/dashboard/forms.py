from flask_wtf import FlaskForm
from wtforms import DecimalField
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError

from app.models import Account


class AddAccountForm(FlaskForm):
    account_type = SelectField('Account Type', choices=[('', 'Select an Account Type'), ('Checking', 'Checking'), ('Savings', 'Savings'), ('Cash', 'Cash'), ('Credit Card', 'Credit Card')], validators=[DataRequired()])
    account_name = StringField('Account Name', validators=[DataRequired()])
    account_balance = DecimalField('Current Balance', places=2, validators=[DataRequired(message='Please enter a number.')])
    submit = SubmitField('Done')


    def __init__(self, budget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.budget = budget


    def validate_account_name(self, account_name):
        account = Account.query.filter_by(budget=self.budget).filter_by(name=account_name.data).first()
        if account is not None:
            raise ValidationError('Please use a different account name.')


class AddCategoryGroupForm(FlaskForm):
    category_group = StringField('New Category Group', validators=[DataRequired()])
    submit = SubmitField('Ok')


    def __init__(self, budget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.budget = budget


    def validate_category_group(self, category_group):
        account = Account.query.filter_by(budget=self.budget).filter(Account.parent.has(name='Budget')).filter_by(name=category_group.data).first()
        if account is not None:
            raise ValidationError('There is already a category group with this name.')