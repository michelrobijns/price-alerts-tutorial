from flask import Flask, render_template
from pricealerts.common.database import Database
from pricealerts import app


@app.before_first_request
def init_db():
    Database.initialize()


@app.route('/')
def home():
    return render_template('home.html')


from pricealerts.models.users.views import user_blueprint
from pricealerts.models.alerts.views import alert_blueprint
from pricealerts.models.stores.views import store_blueprint
app.register_blueprint(user_blueprint, url_prefix='/users')
app.register_blueprint(alert_blueprint, url_prefix='/alerts')
app.register_blueprint(store_blueprint, url_prefix='/stores')
