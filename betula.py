from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, flash

from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email

#Event class for easy access of event information when rendering
class Event():
    def __init__(self, name, organization, where, when, tags, description, contact):
        self.name = name
        self.organization = organization
        self.where = where
        self.when = when
        self.tags = tags
        self.description = description
        self.contact = contact

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

app.add_url_rule('/custom_static/images/user.png', endpoint='custom_static', view_func=app.send_static_file)

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
    # need to create db object from sql database and import models.py file into this file
    #events = db.session.query(models.Event)
    #user = db.session.query(models.User)
    events = [['Event Name', 'Host Name' , "Social, Sports", "Description"], ['Event Name 2', 'Host Name 2' , "Free, Food", "Description 2"], ['Event Name 3', 'Host Name 3' , "Professional", "Description 3"]]
    return render_template('dashboard.html', events = events)
    #return render_template('dashboard.html', events = events, user = user)

@app.route('/eventsdemo', methods=['GET', 'POST'])
def events():
    events = [['Event Name', 'Host Name', 'UofT', 'October 31st', "Social, Sports", "Description", "sean.pourgoutzidis@mail.utoronto.ca"], ['Event Name 2', 'Host Name 2' , "UofT", "October 31st", "Free, Food", "Description 2", "sean.pourgoutzidis@mail.utoronto.ca"], ['Event Name 3', 'Host Name 3' , "UofT", "October 31st", "Professional", "Description 3", "sean.pourgoutzidis@mail.utoronto.ca"]]
    return render_template('event.html', events=events)

