select id_orders, o.id_user, total_sum, item_id, total, price, name_piz, orders_pos, id_kyrer
	from orders o join order_details od
    on o.id_orders = od.order_id
