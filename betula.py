from flask import Flask, render_template, session, redirect, url_for, flash
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/eventsdemo', methods=['GET', 'POST'])
def events():
    events = [['Event Name', 'Host Name' , "Social, Sports", "Description"], ['Event Name 2', 'Host Name 2' , "Free, Food", "Description 2"], ['Event Name 3', 'Host Name 3' , "Professional", "Description 3"]]
    return render_template('event.html', events=events)
