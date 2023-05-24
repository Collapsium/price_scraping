
Probablemente no siga trabajando en este código, por lo que dejo ciertas consideraciones de cosas por mejorar:

Paginas que tienen mucho javascript (kia / honda), usan fuertemente selenium, siendo estas las que
mas demoran en scrapear (principal elemento a mejorar si se busca optimización de tiempo).

*Falta una revisión extensa del formato tanto del precio lista como precio final, ojo con espacios sobrantes o casteo de data que quedaron pendientes por revisar.

*La logica que considera el precio final puede no considerar todos los bonos, revisar que deberia considerarse en precio final
para cada marca, ya que ciertos bonos pueden no ser considerados relevantes para el precio final.

*volkswagen y hyundai fueron los ultimos hechos, es probable que tengan mas bugs.


