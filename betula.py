from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, flash, request

from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email
from wtforms import SelectMultipleField, widgets


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    login = SubmitField('Login')

class JoinForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Create Password', validators=[DataRequired()])
    rePassword = StringField('Re-enter Password', validators=[DataRequired()])
    accountType = SelectField('Account Type', choices=[('club','Club'), ('regular', 'Event-Goer')], validators=[DataRequired()])
    login = SubmitField('Join')




@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    email = None
    password = None
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
    return render_template('login.html', form=form, email=email, password=password)


@app.route('/join', methods=['GET', 'POST'])
def join():
    email = None
    username = None
    password = None
    rePassword = None
    accountType = None
    form = JoinForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        rePassword = form.rePassword.data
        accountType = form.accountType.data
    return render_template('join.html', form=form, email=email, username=username, password=password, rePassword=rePassword, accountType=accountType)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/eventsdemo', methods=['GET', 'POST'])
def events():
    events = [['Event Name', 'Host Name' , "Social, Sports", "Description"], ['Event Name 2', 'Host Name 2' , "Free, Food", "Description 2"], ['Event Name 3', 'Host Name 3' , "Professional", "Description 3"]]
    return render_template('event.html', events=events)





class FilterForm(FlaskForm):
    filter = SelectMultipleField('Select Filters', choices=[('Filter 1', 'Filter 1'), ('Filter 2', 'Filter 2'), ('Filter 3', 'Filter 3'), ('Filter 4', 'Filter 4')], widget=widgets.ListWidget(prefix_label=False), option_widget=widgets.CheckboxInput())
    submit = SubmitField('Apply Filters')  


@app.route('/userprofile', methods=['GET', 'POST'])
def userprofile():
    # Initialize from session or default values
    session.setdefault('name', 'Guest')
    session.setdefault('phone', '123-456-7890')
    session.setdefault('email', 'guest@guest.com')
    session.setdefault('selected_filters', [])

    form = FilterForm()

    # # Check if 'filter_form' is submitted (indicating the FilterForm is submitted)
    if 'filter_form' in request.form and form.validate_on_submit():
        session['selected_filters'] = form.filter.data
    # # Else, check for name updating functionality
    # elif 'name' in request.form:
    #     session['name'] = request.form.get('name')
    # elif 'email' in request.form:
    #     session['email'] = request.form.get('email')
    # elif 'phone' in request.form:
    #     session['phone'] = request.form.get('phone')

    if request.method == 'POST':
        if 'filter_form' in request.form and form.validate_on_submit():
            session['selected_filters'] = request.form.getlist('filters[]')
        elif 'name' in request.form:
            session['name'] = request.form.get('name')
        elif 'email' in request.form:
            session['email'] = request.form.get('email')
        elif 'phone' in request.form:
            session['phone'] = request.form.get('phone')

    return render_template('userprofile.html', name=session['name'], email=session['email'], form=form, phone=session['phone'], selected_filters=session['selected_filters'])




