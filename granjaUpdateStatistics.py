#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import logging
import time
import sqlite3

from os.path import basename

################################################################################
# STATIC DEF
################################################################################
PATH_GRANJA_DB = 'sqlite/granjaResult.sqlite'

################################################################################
# GLOBAL DEF
################################################################################

################################################################################
################################################################################
def updateStatistics():
	func_name = sys._getframe().f_code.co_name
	logger = logging.getLogger(func_name)
	logger.debug(PATH_GRANJA_DB)

	dbConnection = sqlite3.connect(PATH_GRANJA_DB)
	dbCursor = dbConnection.cursor()
	####################
	dbCursor.execute('''DROP TABLE IF EXISTS LAST_RACES;''')
	dbCursor.execute('''CREATE TABLE LAST_RACES AS SELECT raceId,driverClass,COUNT(kartNumber) AS gridSize FROM races GROUP BY raceId ORDER BY raceId DESC LIMIT 200;''')
	dbCursor.execute('''DROP VIEW IF EXISTS VIEW_LAST_RACES;''')
	dbCursor.execute('''CREATE VIEW VIEW_LAST_RACES AS SELECT driverClass,COUNT(raceId) AS qtRaces FROM LAST_RACES GROUP BY driverClass;''')
	####################
	dbCursor.execute('''DROP TABLE IF EXISTS INDOOR_RANKING_LAPTIME_C01;''')
	dbCursor.execute('''CREATE TABLE INDOOR_RANKING_LAPTIME_C01 AS
	SELECT kartNumber, driverName, MIN(bestLapTime) AS 'BEST_LAP', AVG(bestLapTime) AS 'AVG_LAP', COUNT(*) AS RACES
	FROM races
	WHERE driverClass = 'INDOOR' AND trackConfig = 'CIRCUITO 01' AND raceId IN (SELECT raceId FROM LAST_RACES)
	GROUP BY kartNumber
	ORDER BY BEST_LAP;''')
	####################
	dbCursor.execute('''DROP TABLE IF EXISTS PAROLIN_RANKING_LAPTIME_C01;''')
	dbCursor.execute('''CREATE TABLE PAROLIN_RANKING_LAPTIME_C01 AS
	SELECT kartNumber, driverName, MIN(bestLapTime) AS 'BEST_LAP', AVG(bestLapTime) AS 'AVG_LAP', COUNT(*) AS RACES
	FROM races
	WHERE driverClass = 'PAROLIN' AND trackConfig = 'CIRCUITO 01' AND raceId IN (SELECT raceId FROM LAST_RACES)
	GROUP BY kartNumber
	ORDER BY BEST_LAP;''')
	####################
	dbCursor.execute('''DROP TABLE IF EXISTS GERAL_RANKING_LAPTIME_C01;''')
	dbCursor.execute('''CREATE TABLE GERAL_RANKING_LAPTIME_C01 AS
	SELECT driverClass, driverName, MIN(bestLapTime) AS 'BEST_LAP', COUNT(*) AS RACES
	FROM races
	WHERE trackConfig = 'CIRCUITO 01' AND raceId IN (SELECT raceId FROM LAST_RACES)
	GROUP BY driverClass
	ORDER BY BEST_LAP;''')
	####################
	dbCursor.execute('''DROP TABLE IF EXISTS GERAL_RANKING_LAPTIME;''')
	dbCursor.execute('''CREATE TABLE GERAL_RANKING_LAPTIME AS
	SELECT trackConfig, driverName, driverClass, MIN(bestLapTime) AS 'BEST_LAP', COUNT(*) AS RACES
	FROM races 
	WHERE raceId IN (SELECT raceId FROM LAST_RACES)
	GROUP BY trackConfig;''')
	####################
	dbCursor.execute('''DROP TABLE IF EXISTS ALLTIME_RANKING_LAPTIME;''')
	dbCursor.execute('''CREATE TABLE ALLTIME_RANKING_LAPTIME AS
	SELECT trackConfig, driverName, driverClass, MIN(bestLapTime) AS 'BEST_LAP', COUNT(*) AS RACES
	FROM races 
	GROUP BY trackConfig;''')
	####################
	# CKC_BI_INDOOR
	####################
	dbCursor.execute('''DROP TABLE IF EXISTS INDOOR_KART_POS_FINISH;''')
	dbCursor.execute('''CREATE TABLE INDOOR_KART_POS_FINISH AS 
		SELECT kartNumber, positionFinish, COUNT(*) AS posCount FROM races
		WHERE driverClass='INDOOR' AND raceId IN (SELECT raceId FROM LAST_RACES)
		GROUP BY kartNumber, positionFinish;''')

	dbCursor.execute('''DROP TABLE IF EXISTS INDOOR_RANKING_PODIUM;''')
	dbCursor.execute('''CREATE TABLE INDOOR_RANKING_PODIUM AS 
		SELECT *,(0.28*ifnull(qt1,0) + 0.20*ifnull(qt2,0) + 0.17*ifnull(qt3,0) + 0.14*ifnull(qt4,0) + 0.11*ifnull(qt5,0) + 0.09*ifnull(qt6,0)) / qtRaces AS PODIUM_RATE
		FROM (
			SELECT kartNumber,
				SUM(posCount) AS qtRaces
				,(SELECT i.posCount FROM INDOOR_KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=1) AS qt1
				,(SELECT i.posCount FROM INDOOR_KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=2) AS qt2
				,(SELECT i.posCount FROM INDOOR_KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=3) AS qt3
				,(SELECT i.posCount FROM INDOOR_KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=4) AS qt4
				,(SELECT i.posCount FROM INDOOR_KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=5) AS qt5
				,(SELECT i.posCount FROM INDOOR_KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=6) AS qt6
			FROM INDOOR_KART_POS_FINISH e
			GROUP BY kartNumber
		)
		ORDER BY PODIUM_RATE DESC;''')

	dbCursor.execute('''CREATE TEMPORARY TABLE IF NOT EXISTS TEMP_INDOOR_RANKING_PODIUM AS 
	SELECT * FROM INDOOR_RANKING_PODIUM A ORDER BY A.PODIUM_RATE DESC;''') # this will create rowid as the rank!
	dbCursor.execute('''CREATE TEMPORARY TABLE IF NOT EXISTS TEMP_INDOOR_RANKING_LAPTIME_C01 AS 
	SELECT * FROM INDOOR_RANKING_LAPTIME_C01 A ORDER BY A.BEST_LAP ASC;''') # this will create rowid as the rank!

	dbCursor.execute('''DROP TABLE IF EXISTS CKC_BI_INDOOR;''')
	dbCursor.execute('''CREATE TABLE CKC_BI_INDOOR AS
		SELECT P.kartNumber
			,P.qt1,P.qt2,P.qt3,P.qt4,P.qt5,P.qt6,P.qtRaces
			,P.PODIUM_RATE
			,P.rowid AS P.RANK_PODIUM
			,T.BEST_LAP
			,T.AVG_LAP
			,T.rowid AS T.RANK_LAPTIME
			,0.0125 * (P.RANK_PODIUM + T.RANK_LAPTIME) AS SCORE
		FROM TEMP_INDOOR_RANKING_PODIUM P,TEMP_INDOOR_RANKING_LAPTIME_C01 T
		WHERE P.kartNumber=T.kartNumber
		GROUP BY P.kartNumber
		ORDER BY SCORE;''')

	####################
	# CKC_BI_PAROLIN
	####################
	dbCursor.execute('''DROP TABLE IF EXISTS PAROLIN_KART_POS_FINISH;''')
	dbCursor.execute('''CREATE TABLE PAROLIN_KART_POS_FINISH AS 
		SELECT kartNumber, positionFinish, COUNT(*) AS posCount FROM races
		WHERE driverClass='PAROLIN' AND raceId IN (SELECT raceId FROM LAST_RACES)
		GROUP BY kartNumber, positionFinish;''')

	dbCursor.execute('''DROP TABLE IF EXISTS PAROLIN_RANKING_PODIUM;''')
	dbCursor.execute('''CREATE TABLE PAROLIN_RANKING_PODIUM AS 
		SELECT *,(0.28*ifnull(qt1,0) + 0.20*ifnull(qt2,0) + 0.17*ifnull(qt3,0) + 0.14*ifnull(qt4,0) + 0.11*ifnull(qt5,0) + 0.09*ifnull(qt6,0)) / qtRaces AS PODIUM_RATE
		FROM (
			SELECT kartNumber,
				SUM(posCount) AS qtRaces
				,(SELECT i.posCount FROM PAROLIN_KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=1) AS qt1
				,(SELECT i.posCount FROM PAROLIN_KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=2) AS qt2
				,(SELECT i.posCount FROM PAROLIN_KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=3) AS qt3
				,(SELECT i.posCount FROM PAROLIN_KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=4) AS qt4
				,(SELECT i.posCount FROM PAROLIN_KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=5) AS qt5
				,(SELECT i.posCount FROM PAROLIN_KART_POS_FINISH i WHERE e.kartNumber=i.kartNumber AND i.positionFinish=6) AS qt6
			FROM PAROLIN_KART_POS_FINISH e
			GROUP BY kartNumber
		)
		ORDER BY PODIUM_RATE DESC;''')

	dbCursor.execute('''CREATE TEMPORARY TABLE IF NOT EXISTS TEMP_PAROLIN_RANKING_PODIUM AS 
	SELECT * FROM PAROLIN_RANKING_PODIUM A ORDER BY A.PODIUM_RATE DESC;''') # this will create rowid as the rank!
	dbCursor.execute('''CREATE TEMPORARY TABLE IF NOT EXISTS TEMP_PAROLIN_RANKING_LAPTIME_C01 AS 
	SELECT * FROM PAROLIN_RANKING_LAPTIME_C01 A ORDER BY A.BEST_LAP ASC;''') # this will create rowid as the rank!

	dbCursor.execute('''DROP TABLE IF EXISTS CKC_BI_PAROLIN;''')
	dbCursor.execute('''CREATE TABLE CKC_BI_PAROLIN AS
		SELECT P.kartNumber
			,P.qt1,P.qt2,P.qt3,P.qt4,P.qt5,P.qt6,P.qtRaces
			,P.PODIUM_RATE
			,P.rowid AS P.RANK_PODIUM
			,T.BEST_LAP
			,T.AVG_LAP
			,T.rowid AS T.RANK_LAPTIME
			,0.0125 * (P.RANK_PODIUM + T.RANK_LAPTIME) AS SCORE
		FROM TEMP_PAROLIN_RANKING_PODIUM P,TEMP_PAROLIN_RANKING_LAPTIME_C01 T
		WHERE P.kartNumber=T.kartNumber
		GROUP BY P.kartNumber
		ORDER BY SCORE;''')

	dbConnection.commit()

	dbConnection.execute('''VACUUM;''')
	dbConnection.commit()

	dbConnection.close()
	###
	logger.debug("DONE")

################################################################################
# MAIN
################################################################################
def main():
	appName = sys.argv[0]
	logging.basicConfig(
#		filename = './log/' + appName + '_' + time.strftime("%Y%m%d_%H%M%S") + '.log',
		datefmt = '%Y-%m%d %H:%M:%S',
		format = '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
		level = logging.INFO
	)
	func_name = sys._getframe().f_code.co_name
	logger = logging.getLogger(func_name)
	logger.info('Started')
	###
	updateStatistics()
	###
	logger.info('Finished')

################################################################################
################################################################################
if __name__ == '__main__':
	main()
