SELECT menu_name_bludo, menu_ves_bludo, menu_chec_bludo
FROM pizza.menu
WHERE 1=1
    AND menu_name_bludo like $idmenu

