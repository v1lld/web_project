SELECT menu.idmenu, basket.kol_prod, menu.menu_chec_bludo, menu.menu_name_bludo
FROM menu
JOIN basket ON menu.idmenu = basket.idmenu
GROUP BY menu.idmenu, basket.id_basket;
