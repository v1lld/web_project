SELECT date_mes, kol, sum_or
FROM pizza.otchet_sum
WHERE date_god = $god;