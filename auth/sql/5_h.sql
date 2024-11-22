select kyrer_pasport, kyrer_priem, kyrer_yvolen, kyrer_birth
from kyrer ky left join
(select *
from pizza.orders za
where (year(date_or)=$god and month(date_or)=$mes)) zza
on ky.idkyrer=zza.id_kyrer
WHERE zza.id_orders IS NULL;