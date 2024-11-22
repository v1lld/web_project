from flask import Blueprint, render_template, current_app, request, session
from database.operations import select
from database.sql_provider import SQLProvider
from access import login_required
from auth.view import view
import json

auth_app = Blueprint('auth_app', __name__, template_folder='templates')
auth_s_app = Blueprint('auth_s_app', __name__, template_folder='templates')
auth_ss_app = Blueprint('auth_ss_app', __name__, template_folder='templates')
sql_provider = SQLProvider('auth/sql')


@auth_app.route('/sql/')
@login_required()
def sql_index_handler():
    return render_template('sql.html')

@auth_app.route('/sql_us/')
@login_required()
def sql_index_handler_us():
    return render_template('sql_us.html')

@auth_app.route('/sql_kas/')
@login_required()
def sql_index_handler_kas():
    return render_template('sql_kas.html')

@auth_app.route('/sql/all/')
@login_required()
def sql_index_handler_rab():
    return render_template('all.html', message=session['vgroup'])

@auth_app.route('/sql/id/')
@login_required()
def sql_index_handler_prod():
    return render_template('id.html', message=session['vgroup'])


@auth_app.route('/sql/5_h/')
def sql_index_handler_5_h():
    return render_template('5_h.html')

@auth_app.route('/sql/product/')
def sql_index_handler_poduct():
    return render_template('id_product.html')


@auth_app.route('/sql/all_id/')
def sql_index_handler_allid():
    return render_template('pizza_id.html')

@auth_app.route('/sql/id_kl/')
def sql_index_handler_id_kl():
    return render_template('id_kl.html')


def bus_log(db_config, args):

    sql_statement = ''
    if args['request_type'] == 'menu':
        idmenu = args.get('idmenu', None)
        if idmenu is None:
            sql_statement = sql_provider.get('all_menu.sql', {})
        else:
            idmenu = "'" + '%' + idmenu + '%' + "'"
            sql_statement = sql_provider.get('menu_by_id.sql', {'idmenu': idmenu})
    elif args['request_type'] == 'klient':
        idklient = args.get('idklient', None)

        if idklient is None:
            sql_statement = sql_provider.get('all_klient.sql', {})
        else:
            idklient = "'" + '%' + idklient + '%' + "'"
            sql_statement = sql_provider.get('klient_by_id.sql', {'idklient': idklient})
    elif args['request_type'] == '5_h':
        god = args.get('god')
        mes = args.get('mes', 1)
        sql_statement = sql_provider.get('5_h.sql', {'god': god, 'mes': mes})
    elif args['request_type'] == '6_h':
        sql_statement = sql_provider.get('6_h.sql', {})
    elif args['request_type'] == 'popylar':
        sql_statement = sql_provider.get('popylar_pizza.sql', {})

    elif args['request_type'] == 'product':
        prod_id = args.get('prod_id', None)
        if prod_id is None:
            sql_statement = sql_provider.get('product.sql', {})
        else:
            prod_id = "'" + '%' + prod_id + '%' + "'"
            sql_statement = sql_provider.get('product_id.sql', {'prod_id': prod_id})

    return select(db_config, sql_statement)


def BL_data(url_base_line, url_args_dict):
    args = {}
    args['request_type'] = url_base_line[url_base_line.find('/sql/') + 5:url_base_line.rfind('')]
    print(args['request_type'])
    if args['request_type'] == 'all/klient/' or args['request_type'] == 'all/menu/' or args['request_type'] == 'all/3_h/' or args['request_type'] == 'all/4_h/' or args['request_type'] == 'all/6_h/' or args['request_type'] == 'all/popylar/' or args['request_type'] == 'all/product/':
        args['request_type'] = url_base_line[url_base_line.find('/sql/all') + 9:url_base_line.rfind('/')]
    elif args['request_type'] == 'id/klient/' or args['request_type'] == 'id/menu/' or args['request_type'] == 'id/2_h/' or args['request_type'] == 'id/1_h/' or args['request_type'] == 'id/5_h/' or args['request_type'] == 'id/product/':
        args['request_type'] = url_base_line[url_base_line.find('/sql/id') + 8:url_base_line.rfind('/')]

    for item in url_args_dict:
        if url_args_dict[item] != '':
            args[item] = url_args_dict[item]
    return args



# def sql_request_handler_prod():
#     b_logic_args = BL_data(request.base_url, request.args)
#     result = bus_log(current_app.config['DB_CONFIG'], b_logic_args)
#     return render_template('table_menu.html', item=result)


@auth_app.route('/sql/id/5_h/')
@auth_app.route('/sql/all/6_h/')
@auth_app.route('/sql/all/product/')
@auth_app.route('/sql/id/product/')
@login_required()
def sql_request_handler_admin():
    b_logic_args = BL_data(request.base_url, request.args)
    result = bus_log(current_app.config['DB_CONFIG'], b_logic_args)
    context = {"result": result, "title": "title",
               "tags": json.load(open('configs/tags.json', "r", encoding='utf-8'))}
    return view(context)

@auth_s_app.route('/sql/all/menu/')
@auth_s_app.route('/sql/id/menu/')
@auth_s_app.route('/sql/all/popylar/')
@login_required()
def sql_request_handler_klient():
    b_logic_args = BL_data(request.base_url, request.args)
    result = bus_log(current_app.config['DB_CONFIG'], b_logic_args)
    context = {"result": result, "title": "title",
               "tags": json.load(open('configs/tags.json', "r", encoding='utf-8'))}
    return view(context)

@auth_s_app.route('/sql/id/menu/')
@auth_ss_app.route('/sql/all/menu/')
@auth_ss_app.route('/sql/id/menu/')
@auth_ss_app.route('/sql/all/klient/')
@auth_ss_app.route('/sql/id/klient/')
@login_required()
def sql_request_handler_kasir():
    b_logic_args = BL_data(request.base_url, request.args)
    result = bus_log(current_app.config['DB_CONFIG'], b_logic_args)
    context = {"result": result, "title": "title",
               "tags": json.load(open('configs/tags.json', "r", encoding='utf-8'))}
    return view(context)


