CREATE VIEW IF NOT EXISTS LAST_100_RACES AS 
SELECT DISTINCT raceId FROM races ORDER BY raceId DESC LIMIT 100;