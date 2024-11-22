SELECT
    klient_num, klient_name, klient_adres, klient_data
FROM pizza.klient
WHERE 1=1
    AND klient_name like $idklient




