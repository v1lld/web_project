SELECT
    idlogpas, vgroup
FROM
    pizza.logpas
WHERE
    login = $login
    AND
    password = $password