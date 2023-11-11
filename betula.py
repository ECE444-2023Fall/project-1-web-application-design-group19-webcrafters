from datetime import datetime

from flask import Flask, render_template, session, redirect, url_for, flash, request, Response, jsonify
from wtforms.widgets import ListWidget, CheckboxInput

from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import widgets, StringField, SubmitField, SelectField, SelectMultipleField, DateField, PasswordField, TextAreaField, TimeField
from wtforms.validators import DataRequired, Email
from wtforms import SelectMultipleField, widgets
import csv
import json
from io import StringIO

from pypyodbc_main import pypyodbc as odbc
#import pypyodbc as odbc
from credentials import db_username, db_password

import logging
from logging import handlers

import pandas as pd

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

#Event class for easy access of event information when rendering
class Event():
    def __init__(self, name, organization, where, when, tags, description, contact, registered, event_id):
        self.name = name
        self.organization = organization
        self.where = where
        self.when = when
        self.tags = tags
        self.description = description
        self.contact = contact
        self.registered = registered
        self.event_id = event_id

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

app.add_url_rule('/custom_static/images/user.png', endpoint='custom_static', view_func=app.send_static_file)

bootstrap = Bootstrap(app)
moment = Moment(app)

#Session Variables for Use in Backend Functions

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
        session["email"] = email
        print("Got email!")
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
    
    # Link form to User_Data Table in DB
    connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:betula-server.database.windows.net,1433;Database=BetulaDB;Uid=betula_admin;Pwd="+db_password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    connection = odbc.connect(connection_string)

    #Get the user from the USER_DATA table
    get_user_table_data_query = f"SELECT * FROM USER_DATA WHERE User_Email = \'{session['email']}\'"
    select_user_cursor = connection.cursor()
    select_user_cursor.execute(get_user_table_data_query)
    dataset = select_user_cursor.fetchall()

    # Get Column Names
    headers = [column[0] for column in select_user_cursor.description]
    user_df = pd.DataFrame(columns=headers, data=dataset)

    print(user_df.head)
    
    #Get the user's tags and stringency
    userTags = None

    try:    
        userTags = user_df['user_tags'].values[0]
    except:
        print('User was not found')

    if userTags is not None:
        userTags = userTags.split(',')
        userStringency = user_df['recs_must_match'].values[0]
    else:
        userStringency = 0

    print('These are the user tags: ', userTags)

    userRegisteredEvents = user_df['event_id'].values[0]

    if userRegisteredEvents is not None:
        userRegisteredEvents = userRegisteredEvents.split(',')

    print(f"User Registered Events {userRegisteredEvents}")
        
    #Now that we have the user information, let's grab the events
    eventsList = []
    get_user_table_data_query = f"SELECT * FROM EVENT_DATA"
    select_user_cursor.execute(get_user_table_data_query)
    dataset = select_user_cursor.fetchall()

    # Get Column Names and match dataframe
    headers = [column[0] for column in select_user_cursor.description]
    events_df = pd.DataFrame(columns=headers, data=dataset)
    
    #Randomize our database
    events_df = events_df.sample(frac=1)

    #print(events_df.head)

    #Maximum amount of recommendations to give to user at a time
    MAX_RECOMMENDATIONS = 10

    #Iterate through events and add matches matches
    for index, row in events_df.iterrows():
        #Get the event_id
        event_id = row['event_id']

        registered = False

        print(event_id)
        if userRegisteredEvents is not None:
            if str(event_id) in userRegisteredEvents:
                print('Registered!')
                registered = True
            else:
                print('Not registered!')
                registered = False

        #If we are stringent, only add events that match with our tags
        if (userStringency):
            tagMatch = False

            try:
                #Check if it has tags
                rowTags = row['tags'].split(',')
            except:
                #Otherwise skip!
                continue

            #Try to get organization, otherwise state it as unavailable
            try:
                organization = row['organization_name']
            except:
                organization = "Not available"

            for tag in rowTags:
                if tag in userTags or organization in userTags:
                    tagMatch = True

            if tagMatch:
                
                try:
                    where = row['event_location_common_name'] + ", " + row['event_street_address'] + ", " + row['event_city']
                except:
                    where = "Not available"
                try:
                    when = row['event_date'] + " | " + row['event_start_time'] + " to " + row['event_end_time']
                except:
                    when = "Not available"

                currEvent = Event(name = row['event_name'], organization = organization, where = where, when = when, tags = row['tags'], description = row['event_description'], contact = row['coordinator_email'], event_id = event_id, registered = registered)
                eventsList.append(currEvent)
        #Otherwise, add any event!
        else:
            try:
                where = row['event_location_common_name'] + ", " + row['event_street_address'] + ", " + row['event_city']
            except:
                where = "Not available"
            try:
                when = row['event_date'] + " | " + row['event_start_time'] + " to " + row['event_end_time']
            except:
                when = "Not available"

            #Try to get organization, otherwise state it as unavailable
            try:
                organization = row['organization_name']
            except:
                organization = "Not available"

            currEvent = Event(name = row['event_name'], organization = organization, where = where, when = when, tags = row['tags'], description = row['event_description'], contact = row['coordinator_email'], event_id = event_id, registered = registered)
            eventsList.append(currEvent)

        #If we have reached the maximum amount of recommendations, break out of loop
        if (len(eventsList) == MAX_RECOMMENDATIONS):
            break


     #The user pressed a button
    if request.method == 'POST':
        
        event_pressed = None

        #Get the button pressed from the events on the screen
        index = 0
        for event in eventsList:
            if str(event.event_id) in request.form:
                event_pressed = event.event_id
                if eventsList[index].registered == True:
                    eventsList[index].registered = False
                else:
                    eventsList[index].registered = True
                break

            index += 1
        
        print(f"Clicked {event_pressed}")

        print(f"User Registered Events: {userRegisteredEvents}")

        #Add it to the user's registered events
        if userRegisteredEvents is not None:
 
            #Remove any blank space if there are any
            for element in userRegisteredEvents:
                if element == '':
                    userRegisteredEvents.remove(element)
            
            amountRegistered = len(userRegisteredEvents)

            print(f"Removed Spaces?: {userRegisteredEvents}")

            #if the event clicked is not already counted add it
            if not(str(event_pressed) in userRegisteredEvents):
                #userRegisteredEvents = str(userRegisteredEvents)
                userRegisteredEvents = str(','.join(userRegisteredEvents))
                if (amountRegistered > 0):
                    userRegisteredEvents = userRegisteredEvents + "," + str(event_pressed)
                else:
                    userRegisteredEvents = str(event_pressed)
            #if they have clicked it a second time, unregister them!
            else:
                userRegisteredEvents.remove(str(event_pressed))
                print(f"Current Registered Events {userRegisteredEvents}")
                if userRegisteredEvents is not None:
                    userRegisteredEvents = ','.join(userRegisteredEvents)
            
            userRegisteredEvents = str(userRegisteredEvents)

        else:
            userRegisteredEvents = str(event_pressed)

        print(f"USER REGISTERED EVENTS: {userRegisteredEvents}")

        #placeholders = ",".join(["?"] * len(userRegisteredEvents))

        #Update the user table with what the user pressed
        params = [userRegisteredEvents, session['email']]
        update_table_query = f"UPDATE USER_DATA SET event_id = \'" + userRegisteredEvents + f"\' WHERE User_Email = \'{session['email']}\'"
        print(update_table_query)
        select_user_cursor.execute(update_table_query)

    #Save table and close database
    connection.commit()
    select_user_cursor.close()
    connection.close()

    return render_template('dashboard.html', events = eventsList)

  
@app.route('/eventsdemo', methods=['GET', 'POST'])
def events():
    events = [['Event Name', 'Host Name', 'UofT', 'October 31st', "Social, Sports", "Description", "sean.pourgoutzidis@mail.utoronto.ca"], ['Event Name 2', 'Host Name 2' , "UofT", "October 31st", "Free, Food", "Description 2", "sean.pourgoutzidis@mail.utoronto.ca"], ['Event Name 3', 'Host Name 3' , "UofT", "October 31st", "Professional", "Description 3", "sean.pourgoutzidis@mail.utoronto.ca"]]
    return render_template('event.html', events=events)




@app.route('/print-tags', methods=['POST'])
def print_tags():
    data = request.json
    tags = data.get('tags', [])
    print('Received tags:', tags)

    # Link form to User_Data Table in DB
    connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:betula-server.database.windows.net,1433;Database=BetulaDB;Uid=betula_admin;Pwd="+db_password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    connection = odbc.connect(connection_string)
    select_user_cursor = connection.cursor()

    tagsString = str(",".join(tags))

    #Update the user's tags based on what was returned
    update_table_query = f"UPDATE USER_DATA SET user_tags = \'" + tagsString + f"\' WHERE User_Email = \'{session['email']}\'"
    print(update_table_query)
    select_user_cursor.execute(update_table_query)

    #Save table and close database
    connection.commit()
    select_user_cursor.close()
    connection.close()
    
    # Convert tags to CSV format
    csv_data = '"Tags"\n"' + ",".join(tags) + '"'
    
    # Create a response with the CSV data
    response = Response(csv_data, content_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=tags.csv"
    return response



class FilterForm(FlaskForm):
    filter = SelectMultipleField('Select Filters', choices=[('Tag 1', 'Tag 1'), ('Tag 2', 'Tag 2'), ('Tag 3', 'Tag 3'), ('Tag 4', 'Tag 4'), ('Tag 5', 'Tag 5'), ('Tag 6', 'Tag 6'), ('Tag 7', 'Tag 7'), ('Tag 8', 'Tag 8'), ('Tag 9', 'Tag 9'), ('Tag 10', 'Tag 10'), ('Tag 11', 'Tag 11'),('Tag 12', 'Tag 12'), ('Tag 13', 'Tag 13'), ('Tag 14', 'Tag 14')], widget=ListWidget(prefix_label=False), option_widget=CheckboxInput())
    submit = SubmitField('Apply Filters')   

def save_to_csv():
    
    name = session.get('name', 'Guest')
    email = session.get('email', 'guest@guest.com')
    phone = session.get('phone', '123-456-7890')
    tags = session.get('tags', [])
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Email', 'Phone', 'Tags'])
    writer.writerow([name, email, phone, ', '.join(tags)])
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=profileData.csv"})

@app.route('/saveToCSV', methods=['POST'])
def save_to_csv_endpoint():
    data = request.json
    session['name'] = data.get('name', 'Guest')
    session['email'] = data.get('email', 'guest@guest.com')
    session['phone'] = data.get('phone', '123-456-7890')
    session['selected_filters'] = data.get('tags', [])
    return save_to_csv()

@app.route('/download_csv', methods=['GET'])
def download_csv():
    return save_to_csv()

@app.route('/userprofile', methods=['GET', 'POST'])
def userprofile():
    #Get the user from session email
    print("SESSION PRINT:")
    print(session)
    
    # Link form to User_Data Table in DB
    connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:betula-server.database.windows.net,1433;Database=BetulaDB;Uid=betula_admin;Pwd="+db_password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    connection = odbc.connect(connection_string)

    #Get the user from the USER_DATA table
    get_user_table_data_query = f"SELECT * FROM USER_DATA WHERE User_Email = \'{session['email']}\'"
    select_user_cursor = connection.cursor()
    select_user_cursor.execute(get_user_table_data_query)
    dataset = select_user_cursor.fetchall()

    # Get Column Names
    headers = [column[0] for column in select_user_cursor.description]
    user_df = pd.DataFrame(columns=headers, data=dataset)

    print(user_df.head)

    name = str(user_df["user_first_name"].values[0])

    if name == 'None':
        name = 'Guest'

    print('This is the name: ', name)

    password = str((user_df["password"].values[0]))
    email = str(user_df["user_email"].values[0])
    
    #These are the tags we have from the user's database, can we 
    tags = user_df["user_tags"].values[0]

    print('These are the user tags: ', tags)

    tagsList = []
    if tags is not None:
        tagsList = tags.split(",")

    session['name'] = name
    session['password'] = password
    session['email'] = email
    session['selected_filters'] = json.dumps(tagsList)

    print("SESSION PRINT after updating:")
    print(session)


    if request.method == 'POST':
        print("POST!")
        if 'filter_form' in request.form:
            session['selected_filters'] = request.form.getlist('filters[]')
            print('hello!')
            print(session['selected_filters'])
        elif 'name' in request.form:
            session['name'] = request.form.get('name')

            #Update the user's name based on what was returned
            update_table_query = f"UPDATE USER_DATA SET user_first_name = \'" + session['name'] + f"\' WHERE User_Email = \'{session['email']}\'"
            print(update_table_query)
            select_user_cursor.execute(update_table_query)

        elif 'email' in request.form:
            oldEmail = session['email']
            session['email'] = request.form.get('email')

            #Update the user's name based on what was returned
            update_table_query = f"UPDATE USER_DATA SET user_email = \'" + session['email'] + f"\' WHERE User_Email = \'{oldEmail}\'"
            print(update_table_query)
            select_user_cursor.execute(update_table_query)

        elif 'password' in request.form:
            session['password'] = request.form.get('password')

            #Update the user's name based on what was returned
            update_table_query = f"UPDATE USER_DATA SET password = \'" + session['password'] + f"\' WHERE User_Email = \'{session['email']}\'"
            print(update_table_query)
            select_user_cursor.execute(update_table_query)

    #Save table and close database
    connection.commit()
    select_user_cursor.close()
    connection.close()

    return render_template('userprofile.html', name=session['name'], email=session['email'], password=session['password'], selected_filters=session['selected_filters'])


  
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

  
@app.route('/myEvents', methods=['GET', 'POST'])
def myEvents():
    
    # Link form to User_Data Table in DB
    connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:betula-server.database.windows.net,1433;Database=BetulaDB;Uid=betula_admin;Pwd="+db_password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    connection = odbc.connect(connection_string)

    #Get the user from the USER_DATA table
    get_user_table_data_query = f"SELECT * FROM USER_DATA WHERE User_Email = \'{session['email']}\'"
    select_user_cursor = connection.cursor()
    select_user_cursor.execute(get_user_table_data_query)
    dataset = select_user_cursor.fetchall()

    # Get Column Names
    headers = [column[0] for column in select_user_cursor.description]
    user_df = pd.DataFrame(columns=headers, data=dataset)

    #Get the user's saved events
    userRegisteredEvents = user_df['event_id'].values[0]

    #Stores if the user has any saved events
    hasSavedEvents = False

    
    #Store the events to render
    eventsList = []

    #If the user has saved events
    if userRegisteredEvents is not None and len(userRegisteredEvents) != 0:
        userRegisteredEvents = userRegisteredEvents.split(',')
        hasSavedEvents = True

        
        placeholders = ", ".join(["?"] * len(userRegisteredEvents))

        #Get the events from the events table
        get_events_query = f"SELECT * FROM EVENT_DATA WHERE event_id IN (" + placeholders + ")"
        select_user_cursor.execute(get_events_query, userRegisteredEvents)
        dataset = select_user_cursor.fetchall()

        # Get Column Names and match dataframe
        headers = [column[0] for column in select_user_cursor.description]
        events_df = pd.DataFrame(columns=headers, data=dataset)
            
        #close access to the databse
        #select_user_cursor.close()
        #connection.close()

        #Iterate through events and add matches matches
        for index, row in events_df.iterrows():
            #Get the event_id
            event_id = row['event_id']

            registered = True
            organization = row['organization_name']

            where = row['event_location_common_name'] + ", " + row['event_street_address'] + ", " + row['event_city']
            when = row['event_date'] + " | " + row['event_start_time'] + " to " + row['event_end_time']

            currEvent = Event(name = row['event_name'], organization = organization, where = where, when = when, tags = row['tags'], description = row['event_description'], contact = row['coordinator_email'], event_id = event_id, registered = registered)
            eventsList.append(currEvent)
    
    #Make sure to close the database as soon as possible
    #else:
        #close access to the databse
        #select_user_cursor.close()
        #connection.close()

    if request.method == 'POST':
        
        event_pressed = None

        #Get the button pressed from the events on the screen
        index = 0
        for event in eventsList:
            if str(event.event_id) in request.form:
                event_pressed = event.event_id
                eventsList[index].registered = True
                eventsList.remove(eventsList[index])
                break

            index += 1
        
        print(f"Clicked {event_pressed}")

        print(f"User Registered Events: {userRegisteredEvents}")

        #Add it to the user's registered events
        if userRegisteredEvents is not None:
 
            #if the event clicked is not already counted add it
            #if not(str(event_pressed) in userRegisteredEvents):
                #userRegisteredEvents = str(userRegisteredEvents)
            #    userRegisteredEvents = str(','.join(userRegisteredEvents))
            #    userRegisteredEvents = userRegisteredEvents + "," + str(event_pressed)
            #if they have clicked it a second time, unregister them!
            #else:
            userRegisteredEvents.remove(str(event_pressed))
            print(f"Current Registered Events {userRegisteredEvents}")
            if userRegisteredEvents is not None:
                userRegisteredEvents = ','.join(userRegisteredEvents)
            
            userRegisteredEvents = str(userRegisteredEvents)

        else:
            userRegisteredEvents = str(event_pressed)

        print(f"USER REGISTERED EVENTS: {userRegisteredEvents}")

        #placeholders = ",".join(["?"] * len(userRegisteredEvents))

        #Update the user table with what the user pressed
        params = [userRegisteredEvents, session['email']]
        update_table_query = f"UPDATE USER_DATA SET event_id = \'" + userRegisteredEvents + f"\' WHERE User_Email = \'{session['email']}\'"
        print(update_table_query)
        select_user_cursor.execute(update_table_query)
        
        if userRegisteredEvents is None or len(userRegisteredEvents) == 0:
            hasSavedEvents = False
        
    #Save table and close database
    connection.commit()
    select_user_cursor.close()
    connection.close()

    return render_template('saved.html', events = eventsList, hasSavedEvents = hasSavedEvents)

