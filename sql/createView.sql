------------------------------------------------------------
------------------------------------------------------------
CREATE VIEW IF NOT EXISTS RANKING_INDOOR AS
	SELECT
		kartNumber,
		driverName,
		MIN(bestLapTime) AS 'BEST_LAP',
		AVG(bestLapTime) AS 'AVG_LAP',
		COUNT(*) AS RACES
	FROM
		races
	WHERE
		driverClass = 'INDOOR'
		AND trackConfig = 'CIRCUITO 01'
		AND raceId IN (SELECT DISTINCT raceId FROM races ORDER BY raceId DESC LIMIT 100)
	GROUP BY
		kartNumber
	ORDER BY
		BEST_LAP
	LIMIT 20
;
-----------------------------------------------------------
------------------------------------------------------------
CREATE VIEW IF NOT EXISTS RANKING_PAROLIN AS
	SELECT
		kartNumber,
		driverName,
		MIN(bestLapTime) AS 'BEST_LAP',
		AVG(bestLapTime) AS 'AVG_LAP',
		COUNT(*) AS RACES
	FROM
		races
	WHERE
		driverClass = 'PAROLIN'
		AND trackConfig = 'CIRCUITO 01'
		AND raceId IN (SELECT DISTINCT raceId FROM races ORDER BY raceId DESC LIMIT 100)
	GROUP BY
		kartNumber
	ORDER BY
		BEST_LAP
	LIMIT 20
;
------------------------------------------------------------
------------------------------------------------------------
CREATE VIEW IF NOT EXISTS RANKING_TRACK AS
	SELECT
		trackConfig,
		driverName,
		driverClass,
		MIN(bestLapTime) AS 'BEST_LAP',
		COUNT(*) AS RACES
	FROM
		races
	GROUP BY
		trackConfig
;
------------------------------------------------------------
------------------------------------------------------------
CREATE VIEW IF NOT EXISTS RANKING_C01 AS
	SELECT
		driverClass,
		driverName,
		MIN(bestLapTime) AS 'BEST_LAP',
		COUNT(*) AS RACES
	FROM
		races
	WHERE
		trackConfig = 'CIRCUITO 01'
	GROUP BY
		driverClass
	ORDER BY
		BEST_LAP
;
------------------------------------------------------------
------------------------------------------------------------
