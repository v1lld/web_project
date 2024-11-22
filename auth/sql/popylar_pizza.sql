SELECT ky.idmenu, 
       menu_name_bludo,
       menu_ves_bludo,
       menu_chec_bludo
FROM menu ky 
JOIN order_details za ON ky.idmenu = za.item_id 
GROUP BY za.item_id 
ORDER BY COUNT(za.item_id) DESC;
