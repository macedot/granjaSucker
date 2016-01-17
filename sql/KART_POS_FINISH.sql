CREATE VIEW IF NOT EXISTS KART_POS_FINISH AS 
SELECT kartNumber, positionFinish, COUNT(*) AS posCount FROM races
WHERE driverClass = 'INDOOR' AND trackConfig = 'CIRCUITO 01' AND raceId IN LAST_100_RACES
GROUP BY kartNumber, positionFinish