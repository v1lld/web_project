SELECT menu.idmenu, basket.kol_prod, menu_name_bludo
FROM menu JOIN basket ON menu.idmenu = basket.idmenu
WHERE 1=1 AND menu.idmenu IN ($item_ids);