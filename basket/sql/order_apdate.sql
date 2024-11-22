UPDATE orders
SET orders_pos = "Доставлен"
where id_orders = $order_number;