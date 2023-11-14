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
import json

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
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def __init__(self, iden, name, organization, where, when, tags, description, contact, registered, event_id):
        self.iden = iden
        self.name = name
        self.organization = organization
        self.where = where
        self.when = when
        self.tags = tags
        self.description = description
        self.contact = contact
        self.registered = registered
        self.event_id = event_id

# jsonEvent = {iden:iden, name:name, organization:organization, where:where, when:when, tags:tags, description:description, contact:contact}

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
    college = SelectField('College', choices=[('none', 'None'), ('innis','Innis College'), ('new', 'New College'), ('stmikes', "St. Michaels College"), ('trinity', 'Trinity College'), ('uc','University College'), ('vic', 'Victoria College'), ('woodsworth', 'Woodsworth College')], validators=[DataRequired()])
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
        
        # Set Up Connection to DB
        connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:betula-server.database.windows.net,1433;Database=BetulaDB;Uid=betula_admin;Pwd="+db_password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        connection = odbc.connect(connection_string)

        check_user_exists_query = f'''SELECT COUNT(*) 
                                FROM USER_DATA
                                WHERE USER_EMAIL = '{email}' and PASSWORD = '{password}'
                            '''
        
        cursor = connection.cursor()

        try:
            cursor.execute(check_user_exists_query)
            # Only attempt to redirect user to dashboard if login credentials are valid and exists in User_Data table
            if cursor.fetchone()[0] > 0:
                print("Login Successful")
                cursor.close()
                connection.close()
                print("Cursors and DB Closed")
                return redirect(url_for('dashboard'))
            else:
                # Keep invalid login message general for security measures 
                # to not alert hackers of which part of the login credentials is incorrect
                flash("Invalid Login")
                print("Login Unsuccessful")
        except:
            flash("Server down. Try again later.")
            print("Connection Failed")
    
        cursor.close()
        connection.close()
        print("Cursors and DB Closed")
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
    facultyTags = ["Faculty of Applied Science and Engineering", "Trinity College", "University College", "St. Michaels College", "Victoria College"]
    topicTags = ["Professional", "Cultural", "Social Work/Charity", "Fitness", "Social", "Sports"]
    priceTags = ["Free", "Paid", "Free Food"]
    # Link form to User_Data Table in DB
    connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:betula-server.database.windows.net,1433;Database=BetulaDB;Uid=betula_admin;Pwd="+db_password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    connection = odbc.connect(connection_string)

    #Get the user from the USER_DATA table
    try:
        get_user_table_data_query = f"SELECT * FROM USER_DATA WHERE User_Email = \'{session['email']}\'"
    except:
        return redirect(url_for('login'))
      
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
        userTags = None
        userStringency = 0

    print('These are the user tags: ', userTags)

    userRegisteredEvents = user_df['event_id'].values[0]

    if userRegisteredEvents is not None:
        userRegisteredEvents = userRegisteredEvents.split(',')

    print(f"User Registered Events {userRegisteredEvents}")
        
    #Now that we have the user information, let's grab the events
    eventsList = []
    jsonEventsList = []
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
    MAX_RECOMMENDATIONS = 10000

    #Iterate through events and add matches matches
    for index, row in events_df.iterrows():
        #Get the event_id
        event_id = row['event_id']

        registered = False

        if userRegisteredEvents is not None:
            if str(event_id) in userRegisteredEvents:
                registered = True
            else:
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
                if tag.capitalize() in userTags or organization in userTags:
                    tagMatch = True

            if tagMatch:
                
                try:
                    location_name = row['event_location_common_name']
                    street_address = row['event_street_address']
                    city = row['event_city']

                    non_empty_values = [value for value in [location_name, street_address, city] if value is not None and value != '']
                    where = ", ".join(map(str, non_empty_values)) if non_empty_values else "No location given"
                except:
                    where = "Not available"
                try:
                    when = row['event_date'] + " | " + row['event_start_time'] + " to " + row['event_end_time']
                except:
                    when = "Not available"

                currEvent = Event(iden = index, name = row['event_name'], organization = organization, where = where, when = when, tags = row['tags'], description = row['event_description'], contact = row['coordinator_email'], event_id = event_id, registered = registered)

                eventsList.append(currEvent)
                jsonEventsList.append(currEvent.__dict__)
        #Otherwise, add any event!
        else:
            try:
                location_name = row['event_location_common_name']
                street_address = row['event_street_address']
                city = row['event_city']

                non_empty_values = [value for value in [location_name, street_address, city] if value is not None and value != '']
                where = ", ".join(map(str, non_empty_values)) if non_empty_values else "No location given"
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

            tags = row['tags'] if row['tags'] else "No tags given"

            currEvent = Event(iden = index, name = row['event_name'], organization = organization, where = where, when = when, tags=tags, description = row['event_description'], contact = row['coordinator_email'], event_id = event_id, registered = registered)

            eventsList.append(currEvent)
            jsonEventsList.append(currEvent.__dict__)

        #If we have reached the maximum amount of recommendations, break out of loop
        if (len(eventsList) == MAX_RECOMMENDATIONS):
            break


     #The user pressed a button
    if request.method == 'POST':
        
        button_pressed = None
        event_pressed = None
        organization_pressed = None

        print(request.form)

        #Get the button pressed from the events on the screen
        index = 0
        for event in eventsList:
            if str(event.event_id) in request.form:
                button_pressed = "register"
                event_pressed = event.event_id
                if eventsList[index].registered == True:
                    eventsList[index].registered = False
                else:
                    eventsList[index].registered = True
                break

            elif str(event.organization) in request.form:
                button_pressed = "follow"
                organization_pressed = event.organization
                break

            index += 1

        print(f"Button pressed is {button_pressed}")
        
        
        # register or unregister the event
        if button_pressed == "register":
            print(f"Clicked {event_pressed}")

            print(f"User Registered Events: {userRegisteredEvents}")

            #Add it to the user's registered events
            if userRegisteredEvents is not None:
    
                #Remove any blank space if there are any
                for element in userRegisteredEvents:
                    if element == '':
                        userRegisteredEvents.remove(element)
                
                amountRegistered = len(userRegisteredEvents)

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


        # follow or unfollow the organization
        elif button_pressed == "follow":
            if userTags == None:
                userTags = [organization_pressed]
            elif organization_pressed in userTags:
                userTags.remove(organization_pressed)
            else:
                userTags.append(organization_pressed)

            # Joining the tags properly for the SQL query
            updated_user_tags = ','.join(userTags)

            # Prepare the SQL query with proper placeholders to avoid SQL injection
            update_table_query = "UPDATE USER_DATA SET user_tags = \'" + updated_user_tags + f"\' WHERE User_Email = \'{session['email']}\'"

            # Execute the query using placeholders and the updated user tags
            select_user_cursor.execute(update_table_query)


    #Save table and close database
    connection.commit()
    select_user_cursor.close()
    connection.close()

    return render_template('dashboard.html', userTags = userTags, jsonEvents = json.dumps(jsonEventsList), events = eventsList, facultyTags = facultyTags, topicTags=topicTags, priceTags=priceTags, curPage = "dash")


  
@app.route('/eventsdemo', methods=['GET', 'POST'])
def events():
    events = [['Event Name', 'Host Name', 'UofT', 'October 31st', "Social, Sports", "Description", "sean.pourgoutzidis@mail.utoronto.ca"], ['Event Name 2', 'Host Name 2' , "UofT", "October 31st", "Free, Food", "Description 2", "sean.pourgoutzidis@mail.utoronto.ca"], ['Event Name 3', 'Host Name 3' , "UofT", "October 31st", "Professional", "Description 3", "sean.pourgoutzidis@mail.utoronto.ca"]]
    return render_template('event.html', events=events)


def concatenate_list(items, delimiter=' '):
    return delimiter.join(items)


possible_event_tags = ["Faculty of Applied Science and Engineering","Trinity College","University College","St. Michaels College",
                       "Victoria College","Professional","Cultural","Social Work/Charity","Fitness","Social","Sports","Free",
                       "Paid","Free Food"]


@app.route('/print-tags', methods=['POST'])
def print_tags():
    data = request.json
    new_event_tags = data.get('tags', [])  # New event tags to replace existing event tags
    print("These are the new event tags: ", new_event_tags)

    # Link form to User_Data Table in DB
    connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:betula-server.database.windows.net,1433;Database=BetulaDB;Uid=betula_admin;Pwd="+db_password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    connection = odbc.connect(connection_string)
    select_user_cursor = connection.cursor()

    # Retrieve the current user tags from the database
    select_tags_query = f"SELECT user_tags FROM USER_DATA WHERE User_Email = \'{session['email']}\'"
    select_user_cursor.execute(select_tags_query)
    result = select_user_cursor.fetchone()

    if result is not None:
        user_tags_str = result[0]
        if user_tags_str:
            current_tags = set(user_tags_str.split(","))
            print("User tags:", current_tags)
        else:
            #  empty set
            current_tags = set()
            print("User has no tags yet.")
    else:
        print("User not found in the database.")

    # Determine the existing event tags
    existing_event_tags = current_tags.intersection(set(possible_event_tags))
    print("These are the existing event tags: ", existing_event_tags)

    # Determine the club tags by subtracting the existing event tags from the current tags
    club_tags = list(current_tags - existing_event_tags)
    print("These are the club tags: ", club_tags)

    # Combine the new event tags with the club tags
    final_tags = list(set(new_event_tags + club_tags))
    print("These are the final tags: ", final_tags)

    final_tags_string = ','.join(final_tags)
    final_tags_string = final_tags_string.replace("\'", "")
    final_tags_string = final_tags_string.replace("\"", "")
    print("These are the final tags in string form: ", final_tags_string)

    # Update the user's tags in the database
    update_table_query = f"UPDATE USER_DATA SET user_tags = \'" + final_tags_string + f"\' WHERE User_Email = \'{session['email']}\'"
    select_user_cursor.execute(update_table_query)

    # Save table and close database
    connection.commit()
    select_user_cursor.close()
    connection.close()

    # Convert tags to CSV format
    csv_data = '"Tags"\n"' + ",".join(final_tags) + '"'

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


    userStringency = user_df['recs_must_match'].values[0]
    if userStringency is None:
        userStringency = False


    session['name'] = name
    session['password'] = password
    session['email'] = email
    session['selected_filters'] = json.dumps(tagsList)
    session['stringency_value'] = str(userStringency)
    
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

            #Update the user's email based on what was returned
            update_table_query = f"UPDATE USER_DATA SET user_email = \'" + session['email'] + f"\' WHERE User_Email = \'{oldEmail}\'"
            print(update_table_query)
            select_user_cursor.execute(update_table_query)

        elif 'password' in request.form:
            session['password'] = request.form.get('password')

            #Update the user's password based on what was returned
            update_table_query = f"UPDATE USER_DATA SET password = \'" + session['password'] + f"\' WHERE User_Email = \'{session['email']}\'"
            print(update_table_query)
            select_user_cursor.execute(update_table_query)
        
        elif 'stringency' in request.form:
            print("IN HERE!!!")
            session['stringency_value'] = request.form.get('stringency')
            print('STRINGENCY VALUE: ', session['stringency_value'])

            #Update the user's stringency based on what was returned
            update_table_query = f"UPDATE USER_DATA SET recs_must_match = \'" + session['stringency_value'] + f"\' WHERE User_Email = \'{session['email']}\'"
            print(update_table_query)
            select_user_cursor.execute(update_table_query)

    #Save table and close database
    connection.commit()
    select_user_cursor.close()
    connection.close()

    return render_template('userprofile.html', name=session['name'], email=session['email'], password=session['password'], selected_filters=session['selected_filters'], stringency_value=session['stringency_value'])

  
@app.route('/posting', methods=['GET', 'POST'])
def posting():
    #Initialize Variables
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

    # Check if the form is submitted using POST
    if request.method == 'POST':
        # Get form 
        # Set default values for 'name' and 'email' in session if they don't exist
        if 'name' not in session:
            session['name'] = 'Guest'
        if 'email' not in session:
            session['email'] = 'guest@guest.com'

        # Retrieve form data
        organization = request.form.get('organization')
        campus_list = request.form.getlist('campus')
        campus = concatenate_list(campus_list)
        event = request.form.get('event')
        description = request.form.get('description')
        date = request.form.get('date')
        startTime = request.form.get('startTime')
        endTime = request.form.get('endTime')
        street = request.form.get('street')
        city = request.form.get('city')
        postal = request.form.get('postal')
        commonName = request.form.get('commonName')
        college = request.form.get('college')
        faculty_list = request.form.getlist('faculty')
        faculty = concatenate_list(faculty_list)
        cost = request.form.get('cost')
        tags = request.form.get('tags')

        if not all([organization, campus, event, description, date, startTime, endTime, college, cost]):
            # Flash a reminder to fill in all fields
            flash('Please fill in all required fields', 'warning')
        else:
            # Database connection setup
            connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:betula-server.database.windows.net,1433;Database=BetulaDB;Uid=betula_admin;Pwd="+db_password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
            connection = odbc.connect(connection_string)

            # SQL query to insert event data into the database
            create_event_query = '''
                    INSERT INTO EVENT_DATA (Event_name, Coordinator_Name, Coordinator_Email, Coordinator_Username, Organization_Name, Target_Campus, Event_Description, Event_Date, Event_Start_Time, Event_End_Time, Event_Street_Address, Event_City, Event_Postal_Code, Event_Location_Common_Name, Target_College, Target_Faculty, Event_Cost, Tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''
            
            cursor = connection.cursor()

            try:
                # Execute the SQL query with form data and session values
                cursor.execute(create_event_query, (event, session['name'], session['email'], session['name'], organization, campus, description, date, startTime, endTime, street, city, postal, commonName, college, faculty, cost, tags) )
                connection.commit() # Line needed to ensure DB on server is updated

                flash('Event added successfully', 'success')

                cursor.close()
                connection.close()
                return redirect(url_for('dashboard'))
            except:
                flash('Error adding event. Please try again.', 'error')
            
            cursor.close()
            connection.close()

            print("Cursors and DB Closed")

    # Render the posting.html template with form data
    return render_template('posting.html', form=form, organization=organization, campus = campus, event = event, description = description, date = date, startTime = startTime, endTime = endTime, street = street, city = city, postal = postal, commonName = commonName, college = college, faculty = faculty, cost = cost, tags = tags)

@app.route('/saveToCSV', methods=['POST'])
def save_to_csv_endpoint():
    data = request.json
    session['name'] = data.get('name', 'Guest')
    session['email'] = data.get('email', 'guest@guest.com')
    session['phone'] = data.get('phone', '123-456-7890')
    session['selected_filters'] = data.get('tags', [])
    return save_to_csv()
  
@app.route('/myEvents', methods=['GET', 'POST'])
def myEvents():
    
    facultyTags = ["Faculty of Applied Science and Engineering", "Trinity College", "University College", "St. Michaels College", "Victoria College"]
    topicTags = ["Professional", "Cultural", "Social Work/Charity", "Fitness", "Social", "Sports"]
    priceTags = ["Free", "Paid", "Free Food"]

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

    #Get the user's tags
    userTags = None

    try:    
        userTags = user_df['user_tags'].values[0]
    except:
        print('User was not found')

    if userTags is not None:
        userTags = userTags.split(',')
        

    #Get the user's saved events
    userRegisteredEvents = user_df['event_id'].values[0]

    #Stores if the user has any saved events
    hasSavedEvents = False

    
    #Store the events to render
    eventsList = []
    jsonEventsList = []

    #If the user has saved events
    if userRegisteredEvents != None and len(userRegisteredEvents) != 0:
        userRegisteredEvents = userRegisteredEvents.split(',')
        hasSavedEvents = True

        
        # Filter out non-integer elements and convert valid ones to integers
        userRegisteredEvents = [int(event) for event in userRegisteredEvents if event.isdigit()]

        if userRegisteredEvents:
            placeholders = ', '.join(['?' for _ in userRegisteredEvents])

            # Get the events from the events table
            get_events_query = f"SELECT * FROM EVENT_DATA WHERE event_id IN ({placeholders})"
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
            try:
                organization = row['organization_name']
            except:
                organization = "Not available"

            try:
                where = row['event_location_common_name'] + ", " + row['event_street_address'] + ", " + row['event_city']
            except:
                where = "Not available"
            try:
                when = row['event_date'] + " | " + row['event_start_time'] + " to " + row['event_end_time']
            except:
                when = "Not available"

            currEvent = Event(iden = index, name = row['event_name'], organization = organization, where = where, when = when, tags = row['tags'], description = row['event_description'], contact = row['coordinator_email'], event_id = event_id, registered = registered)
            eventsList.append(currEvent)
            jsonEventsList.append(currEvent.__dict__)
    
    #Make sure to close the database as soon as possible
    #else:
        #close access to the databse
        #select_user_cursor.close()
        #connection.close()

    if request.method == 'POST':
        
        button_pressed = None
        event_pressed = None
        organization_pressed = None

        #Get the button pressed from the events on the screen
        index = 0
        for event in eventsList:
            if str(event.event_id) in request.form:
                button_pressed = "register"
                event_pressed = event.event_id
                eventsList[index].registered = True
                eventsList.remove(eventsList[index])
                break

            elif str(event.organization) in request.form:
                button_pressed = "follow"
                organization_pressed = event.organization
                break

            index += 1
        

        # unregister the event
        if button_pressed == "register":
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
                print(f"User registered event in myEvents {userRegisteredEvents}")
                print(event_pressed)
                userRegisteredEvents.remove((event_pressed))
                print(f"Current Registered Events {userRegisteredEvents}")
                if userRegisteredEvents is not None:
                    #Convert back to string to avoid error
                    userRegisteredEvents = [str(event) for event in userRegisteredEvents]
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


        # follow or unfollow the organization
        elif button_pressed == "follow":
            if userTags == None:
                userTags = [organization_pressed]
            elif organization_pressed in userTags:
                userTags.remove(organization_pressed)
            else:
                userTags.append(organization_pressed)

            # Joining the tags properly for the SQL query
            updated_user_tags = ','.join(userTags)

            # Prepare the SQL query with proper placeholders to avoid SQL injection
            update_table_query = "UPDATE USER_DATA SET user_tags = \'" + updated_user_tags + f"\' WHERE User_Email = \'{session['email']}\'"

            # Execute the query using placeholders and the updated user tags
            select_user_cursor.execute(update_table_query)

        
    #Save table and close database
    connection.commit()
    select_user_cursor.close()
    connection.close()

    return render_template('saved.html', events = eventsList, jsonEvents = json.dumps(jsonEventsList), userTags = userTags, hasSavedEvents = hasSavedEvents, curPage = "myEvents", facultyTags = facultyTags, topicTags=topicTags, priceTags=priceTags)

