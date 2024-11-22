select kyrer_pasport, kyrer_priem, kyrer_yvolen, kyrer_birth, col
from kyrer ky join
(select id_kyrer, count(*) as col
from orders
group by id_kyrer) o
on ky.idkyrer = o.id_kyrer;