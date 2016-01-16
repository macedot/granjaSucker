CREATE VIEW IF NOT EXISTS RANKING_INDOOR AS (
	SELECT
		kartNumber, 
		MIN(bestLapTime) AS 'BEST_LAP',
		count(*) AS RACES
	from 
		races
	where 
		driverClass = 'INDOOR' 
		AND trackConfig = 'CIRCUITO 01'
		AND raceId IN (SELECT DISTINCT raceId FROM races ORDER BY raceId DESC LIMIT 100)
	group by 
		kartNumber 
	order by 
		BEST 
	LIMIT 20
)
