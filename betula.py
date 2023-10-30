from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, flash, request

from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import widgets, StringField, SubmitField, SelectField, SelectMultipleField, DateField, PasswordField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Email

from pypyodbc_main import pypyodbc as odbc
#import pypyodbc as odbc
from credentials import db_username, db_password

import logging
from logging import handlers

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

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
    
    # Link form to User_Data Table in DB
    connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:betula-server.database.windows.net,1433;Database=BetulaDB;Uid=betula_admin;Pwd="+db_password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    connection = odbc.connect(connection_string)

    create_user_query = f'''
                        INSERT INTO USER_DATA (User_Email, Username, Password, Account_Type)
                        VALUES ('{email}', '{username}', '{password}', '{accountType}')
                        '''
    
    cursor = connection.cursor()

    try:
        cursor.execute(create_user_query)
        cursor.commit() # Line needed to ensure DB on server is updated
        print("User added successfully")
    except:
        print("User not added")
    
    cursor.close()
    connection.close()

    print("Cursors and DB Closed")

    return render_template('join.html', form=form, email=email, username=username, password=password, rePassword=rePassword, accountType=accountType)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')


@app.route('/eventsdemo', methods=['GET', 'POST'])
def events():
    events = [['Event Name', 'Host Name' , "Social, Sports", "Description"], ['Event Name 2', 'Host Name 2' , "Free, Food", "Description 2"], ['Event Name 3', 'Host Name 3' , "Professional", "Description 3"]]
    return render_template('event.html', events=events)


@app.route('/posting', methods=['GET'])
def render_posting():
    form = PostingForm()
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
    return render_template('posting.html', form=form, organization=organization, campus = campus, event = event, description = description, date = date, startTime = startTime, endTime = endTime, street = street, city = city, postal = postal, commonName = commonName, college = college, faculty = faculty, cost = cost, tags = tags)


@app.route('/post_success', methods=['POST'])
def submit_posting():
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

    if request.method == 'POST':
        organization = request.form['organization']
        campus = request.form.getlist('campus')
        event = request.form['event']
        description = request.form['description']
        date = request.form['date']
        startTime = request.form['startTime']
        endTime = request.form['endTime']
        street = request.form['street']
        city = request.form['city']
        postal = request.form['postal']
        commonName = request.form['commonName']
        college = request.form['college']
        faculty = request.form.getlist('faculty')
        cost = request.form['cost']
        tags = request.form['tags']


        connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:betula-server.database.windows.net,1433;Database=BetulaDB;Uid=betula_admin;Pwd="+db_password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        connection = odbc.connect(connection_string)

        #VALUES ('{event}', '{organization}', '{campus}', '{description}', '{date}', '{startTime}', '{endTime}', '{street}', '{city}', '{postal}', '{commonName}', '{college}', '{faculty}', '{cost}', '{tags}')
        #how to get Coordinator_Name, Coordinator_Email, Coordinator_Username into database
        create_user_query = f'''
                            INSERT INTO EVENT_DATA (Event_name, Organization_Name, Event_Description, Event_Street_Address, Event_City, Event_Postal_Code, Event_Location_Common_Name, Tags)
                            VALUES ('{event}', '{organization}', '{description}', '{street}', '{city}', '{postal}', '{commonName}', '{tags}')
                            '''
        
        cursor = connection.cursor()

        try:
            cursor.execute(create_user_query)
            connection.commit() # Line needed to ensure DB on server is updated
            print("Event added successfully")
        except:
            print("Event not added")
        
        cursor.close()
        connection.close()

        print("Cursors and DB Closed")

    return render_template('post_success.html', form=form, organization=organization, campus = campus, event = event, description = description, date = date, startTime = startTime, endTime = endTime, street = street, city = city, postal = postal, commonName = commonName, college = college, faculty = faculty, cost = cost, tags = tags)