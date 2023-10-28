from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, flash

from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import widgets, StringField, SubmitField, SelectField, SelectMultipleField, DateField, PasswordField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    login = SubmitField('Login')

class JoinForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Create Password', validators=[DataRequired()])
    rePassword = PasswordField('Re-enter Password', validators=[DataRequired()])
    accountType = SelectField('Account Type', choices=[('club','Club'), ('regular', 'Event-Goer')], validators=[DataRequired()])
    login = SubmitField('Join')

class PostingForm(FlaskForm):
    organization = StringField('Organization Name', validators=[DataRequired()])
    campus = SelectMultipleField('Campus', choices=[('stgeorge','St. George'), ('utm', 'Mississauga'), ('uts', 'Scarborough')], validators=[DataRequired()])
    event = StringField('Event Name', validators=[DataRequired()])
    description = TextAreaField('Event Description', validators=[DataRequired()])
    date = DateField('Date and Time', validators=[DataRequired()])
    startTime = TimeField('Start Time', validators=[DataRequired()])
    endTime = TimeField('End Time', validators=[DataRequired()])
    street = StringField('Street Address')
    city = StringField('City')
    postal = StringField('Postal Code')
    commonName = StringField('Commonly Referred to as (i.e. if space has a student-given name like "the pit" or "Back Campus")')
    college = SelectField('College', choices=[('none', 'None'), ('innis','Innis College'), ('new', 'New College'), ('stmikes', "St. Michael's College"), ('trinity', 'Trinity College'), ('uc','University College'), ('vic', 'Victoria College'), ('woodsworth', 'Woodsworth College')], validators=[DataRequired()])
    faculty = SelectMultipleField('Faculty', choices=[('engineering','Applied Science and Engineering'), ('architecture', 'Architecture, Landscape and Design'), ('artsci', 'Arts and Science'), ('continuing', "Continuing Studies"), ('dentistry','Dentistry'), ('edu', 'Education'), ('info', 'Information'), ('kpe', 'Kinesiology and Physical Education'), ('law', 'Law'), ('management', 'Management'), ('med', 'Medicine'), ('music', 'Music'), ('nursing', 'Nursing'), ('pharm', 'Pharmacy'), ('publichealth', 'Public Health'), ('socwork', "Social Work")], validators=[DataRequired()])
    cost = SelectField('Cost', choices=[('free','Free'), ('under5', 'Under $5'), ('under10', 'Under $10'), ('under20', 'Under $20'), ('above20','$20+')], validators=[DataRequired()])
    tags = StringField('Tags')
    post = SubmitField('Make Post')


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
        return redirect(url_for('dashboard'))
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
        return redirect(url_for('dashboard'))
    return render_template('join.html', form=form, email=email, username=username, password=password, rePassword=rePassword, accountType=accountType)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')


@app.route('/eventsdemo', methods=['GET', 'POST'])
def events():
    events = [['Event Name', 'Host Name' , "Social, Sports", "Description"], ['Event Name 2', 'Host Name 2' , "Free, Food", "Description 2"], ['Event Name 3', 'Host Name 3' , "Professional", "Description 3"]]
    return render_template('event.html', events=events)


@app.route('/posting', methods=['GET', 'POST'])
def posting():
    organization = None
    campus = None
    event = None
    description = None
    date = None
    startTime = None
    endTime = None
    street = None
    city = None
    postal = None
    commonName = None
    college = None
    faculty = None
    cost = None
    tags = None
    form = PostingForm()
    if form.validate_on_submit():
        organization = form.organization.data
        campus = form.campus.data
        event = form.event.data
        description = form.description.data
        date = form.date.data
        startTime = form.startTime.data
        endTime = form.endTime.data
        street = form.street.data
        city = form.city.data
        postal = form.postal.data
        commonName = form.commonName.data
        college = form.college.data
        faculty = form.faculty.data
        cost = form.cost.data
        tags = form.tags.data
    return render_template('posting.html', form=form)