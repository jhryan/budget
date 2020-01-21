from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms import DecimalField
from wtforms import IntegerField
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError

from app.models import Account


class AddAccountForm(FlaskForm):
    account_type = SelectField('Account Type',
                               choices=[('', 'Select an Account Type'),
                                        ('Checking', 'Checking'),
                                        ('Savings', 'Savings'),
                                        ('Cash', 'Cash'),
                                        ('Credit Card', 'Credit Card')],
                               validators=[DataRequired()])

    account_name = StringField('Account Name', validators=[DataRequired()])

    account_balance = DecimalField('Current Balance',
                                   places=2,
                                   validators=[DataRequired(
                                            message='Please enter a number.')])
    submit = SubmitField('Done')

    def __init__(self, budget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.budget = budget

    def validate_account_name(self, account_name):
        account = Account.query.filter_by(budget=self.budget) \
            .filter_by(name=account_name.data).first()
        if account is not None:
            raise ValidationError('Please use a different account name.')


class AddCategoryGroupForm(FlaskForm):
    category_group = StringField('New Category Group',
                                 validators=[DataRequired()])
    submit = SubmitField('Ok')

    def __init__(self, budget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.budget = budget

    def validate_category_group(self, category_group):
        account = Account.query.filter_by(budget=self.budget) \
            .filter(Account.parent.has(name='Budget')) \
            .filter_by(name=category_group.data).first()
        if account is not None:
            raise ValidationError(
                    'There is already a category group with this name.')


class EditCategoryGroupForm(FlaskForm):
    new_category_group = StringField('Edit Category Group',
                                     validators=[DataRequired()])
    submit = SubmitField('Ok')

    def __init__(self, budget, original_category_group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.budget = budget
        self.original_category_group = original_category_group

    def validate_new_category_group(self, new_category_group):
        if new_category_group.data != self.original_category_group:
            account = Account.query.filter_by(budget=self.budget) \
                .filter(Account.parent.has(name='Budget')) \
                .filter_by(name=new_category_group.data).first()
            if account is not None:
                raise ValidationError(
                        'There is already a category group with this name.')


class AddCategoryForm(FlaskForm):
    category = StringField('New Category', validators=[DataRequired()])
    submit = SubmitField('Ok')

    def __init__(self, budget, category_group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.budget = budget
        self.category_group = category_group

    def validate_category(self, category):
        account = Account.query.filter_by(budget=self.budget) \
            .filter(Account.parent.has(name=self.category_group)) \
            .filter_by(name=category.data).first()
        if account is not None:
            raise ValidationError(
                    'There is already a category with this name.')


class EditCategoryForm(FlaskForm):
    new_category = StringField('Edit Category', validators=[DataRequired()])
    submit = SubmitField('Ok')

    def __init__(self, budget, category_group, original_category, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.budget = budget
        self.category_group = category_group
        self.original_category = original_category

    def validate_new_category(self, new_category):
        if new_category.data != self.original_category:
            account = Account.query.filter_by(budget=self.budget) \
                .filter(Account.parent.has(name=self.category_group)) \
                .filter_by(name=new_category.data).first()
            if account is not None:
                raise ValidationError(
                        'There is already a category with this name.')


class EditTransactionForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    payee = StringField('Payee')
    category = SelectField('Category',
                           choices=[('', 'Category')],
                           validators=[DataRequired()])
    description = StringField('Memo')
    outflow = DecimalField('Outflow', places=2)
    inflow = DecimalField('Inflow', places=2)

    posting_id = IntegerField()

    submit = SubmitField('Save')
