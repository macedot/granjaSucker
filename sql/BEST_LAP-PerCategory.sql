select 
	trackConfig, 
	driverName, 
	driverClass, 
	MIN(bestLapTime) AS 'BEST_LAP',
	count(*) AS RACES
from 
	races
group by 
	trackConfig