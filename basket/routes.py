from flask import Blueprint, request, render_template, current_app, session, redirect
from database.sql_provider import SQLProvider
from database.operations import select
from database.connection import DBContextManager
from access import login_required
import redis, time

basket_bp = Blueprint('basket',
                    __name__,
                    template_folder='Templates',
                    static_folder='static'
)


sql_provider = SQLProvider('basket/sql')

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def rediska():
    if r.keys("*") != [] and r.ttl(r.keys("*")[0]) < 0 or r.keys("*") == [] or 'message' in session:
        sql_code = sql_provider.get('all_items.sql', {})
        items = select(current_app.config['DB_CONFIG'], sql_code)
        if 'message' in session:
            print(session['message'])
        for item in items:
            if item['kol_prod'] == 0:
                print(item['idmenu'])
                r.delete(item['idmenu'])  # Удалить ключ из Redis
            else:
                r.hset(item['idmenu'], "menu_name_bludo", item['menu_name_bludo'])
                r.hset(item['idmenu'], "menu_chec_bludo", item['menu_chec_bludo'])
                r.hset(item['idmenu'], "kol_prod", item['kol_prod'])
                r.hset(item['idmenu'], "idmenu", item['idmenu'])
                r.expire(item['idmenu'], 60)
    items=[]
   # print(r.get())
    for i in sorted(r.keys("*")):
        items.append(r.hgetall(i))
    return items



@basket_bp.route('/', methods=['GET', 'POST'])
@login_required()
def basket_index():

    basket = session.get('basket', {})
    message=''
    items = rediska()
    if 'message' in session:
        message = session['message']
        session.pop('message')

    if request.method == 'POST':
        item_id = request.form['item_id']
        item_name = request.form['item_name']
        item_price = request.form['item_price']
        item_amount = request.form['item_amount']
        # print(item_amount)
        for index, item in enumerate(items):
            if int(item['idmenu']) == int(item_id):
                item_im = str(index)
        item = items[int(item_im)]
        if item_id in basket:
            item_description = basket[item_id]
            sum = int(item_description['count']) + int(item_amount)
            if int(sum) < int(item['kol_prod']):
                item_description['count'] = sum
                item_description['menu_chec_bludo'] = int(item_description['menu_chec_bludo']) + int(item_price) * int(
                    item_amount)
            else:
                item_description['count'] = int(item['kol_prod'])
                item_description['menu_chec_bludo'] = int(item_price) * int(item['kol_prod'])
            item_description['menu_name_bludo'] = item_name
            basket[item_id] = item_description
        else:
            if int(item['kol_prod']) < int(item_amount):
                basket[item_id] = {'count': int(item['kol_prod']), 'menu_name_bludo': item_name, 'menu_chec_bludo': int(item_price) * int(item['kol_prod'])}
            else:
                basket[item_id] = {'count': item_amount, 'menu_name_bludo': item_name, 'menu_chec_bludo': int(item_price)*int(item_amount)}
        session['basket'] = basket
    return render_template(
        'basket_index.html', items = items, basket = basket, message=message
    )


@basket_bp.route('/clear')
def clear_basket():
    if 'basket' in session:
        session.pop('basket')
    return redirect('/basket')


@basket_bp.route('/buy')
def buy_basket():
    basket = session.get('basket', {})

    if basket:
        with DBContextManager(current_app.config['DB_CONFIG']) as cursor:
            item_ids = [item_id for item_id in basket]

            total_summa=0

            for i in item_ids:
                total_summa += basket[i]['menu_chec_bludo']
            item_ids = ','.join(item_ids)

            sql_code = sql_provider.get('item_by_id.sql', {'item_ids': item_ids})

            cursor.execute(sql_code)
            schema = [col[0] for col in cursor.description]

            item_descriptions = [dict(zip(schema, row)) for row in cursor.fetchall()]

           # print(item_descriptions)
            for item_description in item_descriptions:
                n_inserts = int(basket[str(item_description['idmenu'])]['count'])
                n_left = int(item_description['kol_prod']) - n_inserts
               # print(n_inserts, n_left)
                if n_left < 0:
                    message = "Товара нет в наличии"
                    session['message'] = message
                    return redirect('/basket')
            sql_code = sql_provider.get('kyrer.sql', {})
            cursor.execute(sql_code)
            kyrer_id = cursor.fetchone()
            if kyrer_id:
                id_qq = int(kyrer_id[0])
                orders_poss = 'Готовим'
            else:
                id_qq = 0
                orders_poss = 'Ожидает'
            print(kyrer_id)
            sql_code = sql_provider.get('create_order.sql', {'user_id': session['idlogpas'], 'total_summa': total_summa, 'orders_poss': "'" + orders_poss + "'", 'id_qq': id_qq})
            cursor.execute(sql_code)
            order_id = cursor.lastrowid
            if id_qq!=0:
                sql_code = sql_provider.get('kyrer_ord_up.sql', {'id_qq': id_qq, 'order_id': order_id })
                cursor.execute(sql_code)
            else:
                print('ожидаем')
           # print(item_descriptions)

            for item_description in item_descriptions:
                n_inserts = basket[str(item_description['idmenu'])]['count']
                n_left = int(item_description['kol_prod']) - int(n_inserts)
                r.hset(str(item_description['idmenu']), "kol_prod", str(n_left))
                sql_code = sql_provider.get('update_storage.sql', {'n_left': n_left, 'item_id': item_description['idmenu']})
                #print(sql_code)
                cursor.execute(sql_code)
                #order_id+=1
                #print(item_description)
                sql_code = sql_provider.get('create_order_details.sql', {'order_id': order_id,
                                                                         'item_id': item_description['idmenu'],
                                                                         'total': n_inserts,
                                                                         'price': r.hget(str(item_description['idmenu']), "menu_chec_bludo"),
                                                                         'id_user': session['idlogpas'],
                                                                         'name_piz': "'" + item_description['menu_name_bludo'] + "'"
                                                                         })
                cursor.execute(sql_code)

        message = "Заказ создан"
        session['message'] = message
        if 'message' in session:
            session.pop('basket')
    return redirect('/basket')



# def order(order_numberr):
#     with DBContextManager(current_app.config['DB_CONFIG']) as cursor:
#



@basket_bp.route('/order', methods=['GET', 'POST'])
@login_required()
def buy_order():
    if session['vgroup'] == 'klient':
        sql_code = sql_provider.get('order.sql', {'user_id': session['idlogpas']})
    elif session['vgroup'] == 'kasir':
        sql_code = sql_provider.get('order_all.sql', {})
    print(session['vgroup'])

    if not sql_code:
        return "нет заказов"
    orders = select(current_app.config['DB_CONFIG'], sql_code)
    # cursor.execute(sql_code)
    # schema = [col[0] for col in cursor.description]
    #
    # orders = [dict(zip(schema, row)) for row in cursor.fetchall()]

    unique_orders = []  # Создание пустого списка для хранения уникальных значений
    seen_ids = set()  # Создание множества для отслеживания уже увиденных id_orders

    for order in orders:  # Итерация по каждому словарю в списке
        if order['id_orders'] not in seen_ids:  # Проверка, был ли уже рассмотрен id_orders
            unique_order = {'id_orders': order['id_orders'], 'total_sum': order['total_sum'], 'orders_pos': order['orders_pos']}  # Создание нового словаря с уникальным 'id_orders' и 'total_sum'
            unique_orders.append(unique_order)  # Добавление нового словаря в список уникальных значений
            seen_ids.add(order['id_orders'])  # Добавление id_orders в множество

   # print(unique_orders)
    return render_template(
        'orders.html', orders=orders, unique_orders=unique_orders, ses=session['vgroup']
    )

@basket_bp.route('/orders', methods=['GET', 'POST'])
@login_required()
def buy_orders():
    with DBContextManager(current_app.config['DB_CONFIG']) as cursor:
        if session['vgroup'] == 'kasir' and request.method == 'POST':
            order_number = request.form.get('order_number')
            sql_code = sql_provider.get('order_apdate.sql', {'order_number': order_number})
            #print(sql_code)
            cursor.execute(sql_code)
            sql_code = sql_provider.get('order_id.sql', {'order_number': order_number})
            cursor.execute(sql_code)
            kyrer_id = cursor.fetchone()
            id_qq = int(kyrer_id[0])
            print(id_qq)
            sql_code = sql_provider.get('kyrer_zero.sql', {'order_number': order_number})
            cursor.execute(sql_code)
    return redirect('/basket/order')


@basket_bp.route('/orders_time', methods=['GET', 'POST'])
@login_required()
def buy_orders_time():
    with DBContextManager(current_app.config['DB_CONFIG']) as cursor:
        if session['vgroup'] == 'kasir' and request.method == 'POST':
            order_number = request.form.get('order_number_t')
            sql_code = sql_provider.get('kyrer.sql', {})
            cursor.execute(sql_code)
            kyrer_id = cursor.fetchone()

            if kyrer_id:
                print(kyrer_id)
                id_qq = int(kyrer_id[0])
            else:
                return render_template('err.html')
            sql_code = sql_provider.get('order_apdate_ky.sql', {'order_number': order_number, 'id_qq': id_qq})
            cursor.execute(sql_code)
            sql_code = sql_provider.get('kyrer_ord_up.sql', {'id_qq': id_qq, 'order_id': order_number})
            cursor.execute(sql_code)
    return redirect('/basket/order')


@basket_bp.route('/orders_delite', methods=['GET', 'POST'])
@login_required()
def buy_orders_delite():
    with DBContextManager(current_app.config['DB_CONFIG']) as cursor:
        if session['vgroup'] == 'klient' and request.method == 'POST':
            order_number = request.form.get('order_number_del')
            sql_code = sql_provider.get('kyrer_delit_orders.sql', {'order_number': order_number})
            cursor.execute(sql_code)
            kyrer_id = cursor.fetchone()
            if kyrer_id:
                print(kyrer_id)
                id_qq = int(kyrer_id[0])
                sql_code = sql_provider.get('kyrer_zero.sql', {'order_number': order_number})
                cursor.execute(sql_code)
            sql_code = sql_provider.get('delite_order.sql', {'order_number': order_number})
            cursor.execute(sql_code)
    return redirect('/basket/order')