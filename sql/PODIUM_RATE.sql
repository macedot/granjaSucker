DROP TABLE IF EXISTS LAST_100_RACES;
DROP TABLE IF EXISTS KART_POS_FINISH;

CREATE TABLE LAST_100_RACES AS SELECT DISTINCT raceId FROM races ORDER BY raceId DESC LIMIT 100;

CREATE TABLE KART_POS_FINISH AS 
SELECT kartNumber, positionFinish, COUNT(*) AS posCount FROM races
WHERE driverClass = 'INDOOR' AND trackConfig = 'CIRCUITO 01' AND raceId IN LAST_100_RACES
GROUP BY kartNumber, positionFinish;


SELECT *, (0.45*ifnull(qt1,0) + 0.25*ifnull(qt2,0) + 0.15*ifnull(qt3,0) + 0.1*ifnull(qt4,0) + 0.05*ifnull(qt5,0) + 0.05*ifnull(qt6,0)) / qtTotal AS PODIUM_RATE
FROM (
	SELECT kartNumber,
		SUM(posCount) AS qtTotal,
		(SELECT i.posCount FROM KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=1) AS qt1,
		(SELECT i.posCount FROM KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=2) AS qt2,
		(SELECT i.posCount FROM KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=3) AS qt3,
		(SELECT i.posCount FROM KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=4) AS qt4,
		(SELECT i.posCount FROM KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=5) AS qt5,
		(SELECT i.posCount FROM KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=6) AS qt6
	FROM KART_POS_FINISH e
	GROUP BY kartNumber
)
ORDER BY PODIUM_RATE DESC;