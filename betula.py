from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, flash, request, Response
from wtforms.widgets import ListWidget, CheckboxInput

from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email
from wtforms import SelectMultipleField, widgets
import csv
from io import StringIO

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
    filter = SelectMultipleField('Select Filters', choices=[('Tag 1', 'Tag 1'), ('Tag 2', 'Tag 2'), ('Tag 3', 'Tag 3'), ('Tag 4', 'Tag 4')], widget=ListWidget(prefix_label=False), option_widget=CheckboxInput())
    submit = SubmitField('Apply Filters')  

def save_to_csv():
    name = session.get('name', 'Guest')
    email = session.get('email', 'guest@guest.com')
    phone = session.get('phone', '123-456-7890')
    tags = session.get('selected_filters', [])
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
    session.setdefault('name', 'Guest')
    session.setdefault('phone', '123-456-7890')
    session.setdefault('email', 'guest@guest.com')
    session.setdefault('selected_filters', [])
    form = FilterForm()
    if request.method == 'POST' and form.validate():
    # Your code here

        # This check should be adjusted:
        if form.validate_on_submit():
            session['selected_filters'] = request.form.getlist('filters[]')
            session['name'] = request.form.get('name', session['name'])
            session['email'] = request.form.get('email', session['email'])
            session['phone'] = request.form.get('phone', session['phone'])
    return render_template('userprofile.html', name=session['name'], email=session['email'], form=form, phone=session['phone'], selected_filters=session['selected_filters'])
