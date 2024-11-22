from flask import Blueprint, render_template, current_app, request, session, redirect
from access import login_required
from database.operations import select
from database.sql_provider import SQLProvider
import json

log_app = Blueprint('log_app', __name__, template_folder='templates')
sql_provider = SQLProvider('login/sql')


def groups(login, password):
    db_config = current_app.config['DB_CONFIG']
    sql_statement = sql_provider.get('pizza_log.sql', {'login': "'" + login + "'", 'password': "'" + password + "'"})
    res = select(db_config, sql_statement)
    return res
def log():
    message = ''
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        data = groups(login, password)

        if len(data) > 0:
            session['vgroup'] = data[0]['vgroup']
            session['idlogpas'] = data[0]['idlogpas']
            return 'index.html', ' '
        else:
            message = "Неверный логин или пароль"
            return 'login.html', message
    else:
        if 'vgroup' in session:
            message = session['vgroup']
            return 'user.html', message
    return 'login.html', message


@log_app.route('/login/', methods=['GET', 'POST'])
def login_handler():
    name_html, message = log()
    if name_html == 'index.html':
        return redirect('/')
    else:
        return render_template(name_html, message=message)


@log_app.route('/authentication')
def authentication_handler(): pass


@log_app.route('/user/')
@login_required()
def user_handler():
    return render_template('user.html', message=session['vgroup'])


@log_app.route("/logout")
@login_required()
def logout():
    # session.pop("vgroup", None)
    # session.pop("login", None)
    # session.pop("idlogpas", None)
    session.clear()
    return redirect("/")



