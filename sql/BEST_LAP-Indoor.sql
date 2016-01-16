select trackConfig, driverName, MIN(bestLapTime) AS 'BEST LAP', count(*) AS RACES
from races
where driverClass = 'INDOOR'
group by trackConfig