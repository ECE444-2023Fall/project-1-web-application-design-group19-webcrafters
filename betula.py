from flask import Flask, render_template, session, redirect, url_for, flash

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
