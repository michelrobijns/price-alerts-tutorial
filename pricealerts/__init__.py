from flask import Flask


app = Flask(__name__)
app.config.from_object('pricealerts.config')
app.secret_key = app.config['SECRET_KEY']


import pricealerts.views

