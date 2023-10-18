from datetime import datetime
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    email = StringField('Username (your UofT Email address)', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    login = SubmitField('Login')


@app.route('/', methods=['GET', 'POST'])
def index():
    email = None
    password = None
    form = NameForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
    return render_template('index.html', form=form, email=email, password=password)