from flask_wtf import FlaskForm
from wtforms import DecimalField
from wtforms import SelectField
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class AddAccountForm(FlaskForm):
    account_type = SelectField('Account Type', choices=[('', 'Select an Account Type'), ('Checking', 'Checking'), ('Savings', 'Savings'), ('Cash', 'Cash'), ('Credit Card', 'Credit Card')], validators=[DataRequired()])
    account_name = StringField('Account Name', validators=[DataRequired()])
    account_balance = DecimalField('Current Balance', places=2, validators=[DataRequired()])
    submit = SubmitField('Done')