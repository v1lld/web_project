SELECT
    prod_name, prod_measure, prod_price
FROM pizza.product
WHERE 1=1
     AND prod_name like $prod_id

