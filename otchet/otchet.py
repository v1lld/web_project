from flask import Blueprint, render_template, current_app, request, session, redirect
from access import login_required
from database.sql_provider import SQLProvider
from database.operations import call_procedure, select
from otchet.view import view
import json

otch_app = Blueprint('otch_app', __name__, template_folder='templates')
sql_provider = SQLProvider('otchet/sql')




@otch_app.route('/sql/')
@login_required()
def main_sql_handler():
    return render_template('main.html', message=session['vgroup'])

@otch_app.route('/sql/create_choice/')
@login_required()
def main_sql_handlerrt():
    return render_template('create_choice.html')

@otch_app.route('/sql/read_choice/')
@login_required()
def main_sql_handler_red():
    return render_template('read_choice.html')

@otch_app.route('/sql/create/')
@login_required()
def create_handler():
    result = select(current_app.config['DB_CONFIG'], sql_provider.get('zakaz_date.sql', {}))
    formatted_dates = [date['date_or'].strftime('%Y-%m') for date in result]
    res = select(current_app.config['DB_CONFIG'], sql_provider.get('otchet_date.sql', {}))

    print(formatted_dates)
    formated_dates = [f"{entry['rep_yaer']}-{entry['rep_month']:02d}" for entry in res]

    print(formated_dates)
    combined_list = list(set(formatted_dates) - set(formated_dates))
    result = list(combined_list)
    print(result)
    context = {"result": result}

    return render_template('create.html', item=context, massage = "1")

@otch_app.route('/sql/create_or/')
@login_required()
def create_handlerr():
    result = select(current_app.config['DB_CONFIG'], sql_provider.get('zakaz_date.sql', {}))
    formatted_dates = [date['date_or'].strftime('%Y') for date in result]
    res = select(current_app.config['DB_CONFIG'], sql_provider.get('otchet_sum.sql', {}))
    formated_dates = [str(date['date_god']) for date in res]
    print(formated_dates)
    print(formatted_dates)
    combined_list = list(set(formatted_dates) - set(formated_dates))
    result = list(combined_list)
    print(result)
    # Используйте set для удаления дубликатов
    context = {"result": result}

    return render_template('create.html', item=context, massage = "2")
def controller(base, argument):
    args = {}
    args['request_type'] = base[base.find('/sql/') + 5:base.rfind('/')]
    for item in argument:
        if argument[item] != '':
            args[item] = argument[item]
    return args
def bus_logic_create(db_config, args):
    if args['request_type'] == 'create/sales':
        sql_statement = 'otchet'
        mes = args.get('mes')
       # print(mes)
        # god, mes = mes.split('-')
        mes = mes[:7]
        #print(mes)
        god = mes[:4]
        mes = mes[-2:]
       # print(god, mes)
        return call_procedure(current_app.config['DB_CONFIG'], sql_statement, god, mes)
    else:
        sql_statement = 'get_report'
        god = args.get('god')
        #print(god)
        return call_procedure(current_app.config['DB_CONFIG'], sql_statement, god)


def bus_logic_read(db_config, args):
    sql_statement = ''
    print(args['request_type'])
    if args['request_type'] == 'read/sales':
        god = args.get('mes')
        if len(god) == 6:
            mes = god[-1:]
        else:
            mes = god[-2:]
        god = god[:4]
        sql_statement = sql_provider.get('read_sales_report.sql', {'god': "'" + god + "'", 'mes': "'" + mes + "'"})
    elif args['request_type'] == 'read/sales_or':
        god = args.get('god')
        sql_statement = sql_provider.get('read_sales_or.sql', {'god':  god })
        print(sql_statement)
    return select(db_config, sql_statement)


@otch_app.route('/sql/read/')
@login_required()
def read_del_handler():
    result = select(current_app.config['DB_CONFIG'], sql_provider.get('sales_years.sql', {}))
   # print(result)
    context = {"result": result}
    return render_template('read_del.html', item = context, massage = "1")


@otch_app.route('/sql/read_or/')
@login_required()
def read_del_handlerii():
    result = select(current_app.config['DB_CONFIG'], sql_provider.get('sales_years_or.sql', {}))
   # print(result)
    context = {"result": result}
    print(context)
    return render_template('read_del.html', item = context, massage = "2")


@otch_app.route('/sql/read/sales/', methods=['GET', 'POST'])
@otch_app.route('/sql/read/sales_or/', methods=['GET', 'POST'])
@login_required()
def read_handler():
    connector_args = controller(request.base_url, request.args)
    result = bus_logic_read(current_app.config['DB_CONFIG'], connector_args)
    context = {"result": result,
               "tags": json.load(open('configs/tags.json', "r", encoding='utf-8'))
               }
    return view('table.html', context)

@otch_app.route('/sql/create/sales/')
@otch_app.route('/sql/create/sales_or/')
@login_required()
def report_handler():
    connector_args = controller(request.base_url, request.args)
    res, ress = bus_logic_create(current_app.config['DB_CONFIG'], connector_args)
    print(ress)
    if res != 1:
        return render_template('errr.html')
    else:
        return render_template('ok.html')



