UPDATE orders
SET id_kyrer = $id_qq, orders_pos = "Готовим"
where id_orders = $order_number;