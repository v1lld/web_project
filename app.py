import json
import time
from flask import Flask, render_template, request, redirect, session
from auth.routes import auth_s_app
from auth.routes import auth_ss_app
from login.routes import log_app
from auth.routes import auth_app
from otchet.otchet import otch_app
from basket.routes import basket_bp
from view import view


app = Flask(__name__)

app.register_blueprint(otch_app, url_prefix='/otch')
app.register_blueprint(auth_app, url_prefix='/auth')
app.register_blueprint(auth_ss_app, url_prefix='/authss')
app.register_blueprint(auth_s_app, url_prefix='/auths')
app.register_blueprint(log_app, url_prefix='/log')
app.register_blueprint(basket_bp, url_prefix='/basket')
app.config['access_config'] = json.load(open('configs/access_config.json'))
app.config['DB_CONFIG'] = json.load(open('configs/db.json'))

app.secret_key = '123wqe'



@app.route('/', methods=['GET'])
def index():
    return view('index.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)
