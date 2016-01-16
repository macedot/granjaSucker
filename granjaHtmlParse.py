#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import getopt
import sys
import os
import logging
import time
import glob
import re
import json

import ThreadPool

from lxml import html
from BeautifulSoup import BeautifulSoup, Comment
from os.path import basename

import sqlite3

################################################################################
# STATIC DEF
################################################################################
PATH_GRANJA_DB = 'granjaResult.sqlite'

################################################################################
# GLOBAL DEF
################################################################################
g_inputPath = "."
g_outputPath = "."

g_raceHeader = {}
# g_raceHeader['positionFinish'] = 'POS';
# g_raceHeader['kartNumber'] = 'NO.';
# g_raceHeader['driverName'] = 'NOME';
# g_raceHeader['driverClass'] = 'CLASSE';
# g_raceHeader['numberOfLaps'] = 'VOLTAS';
# g_raceHeader['totalTime'] = 'TOTAL TEMPO';
# g_raceHeader['avgSpeed'] = 'VELOCIDADE MEDIA';
# g_raceHeader['bestLapTime'] = 'MELHOR TEMPO';
# g_raceHeader['bestSpeed'] = 'MELHOR VELOC.';
# g_raceHeader['bestLap'] = 'NA VOLTA.';
g_raceHeader['POS'] = 'positionFinish';
g_raceHeader['NO.'] = 'kartNumber';
g_raceHeader['NOME'] = 'driverName';
g_raceHeader['CLASSE'] = 'driverClass';
g_raceHeader['VOLTAS'] = 'numberOfLaps';
g_raceHeader['TOTAL TEMPO'] = 'totalTime';
g_raceHeader['VELOCIDADE MEDIA'] = 'avgSpeed';
g_raceHeader['MELHOR TEMPO'] = 'bestLapTime';
g_raceHeader['MELHOR VELOC.'] = 'bestSpeed';
g_raceHeader['NA VOLTA.'] = 'bestLap';

################################################################################
################################################################################
def parseArgs():
	global g_inputPath
	global g_outputPath

	func_name = sys._getframe().f_code.co_name
	logger = logging.getLogger(func_name)

	try:
		opts, args = getopt.getopt(sys.argv[1:], "i:u:", ["inputPath=", "outputPath="])
	except getopt.GetoptError as err:
		logger.warning(str(err)) # will print something like "option -a not recognized", 
		sys.exit(2)

	for o, a in opts:
		if o in ("-i", "--inputPath"):
			g_inputPath = str(a)
		elif o in ("-o", "--outputPath"):
			g_outputPath = str(a)
		else:
			assert False, "unhandled option"

	logger.debug("inputPath = %s; outputPath = %s", g_inputPath, g_outputPath)

################################################################################
################################################################################
def parseResult_Laps(fileName): # tipo = 3
	pass

################################################################################
################################################################################
def parseResult_Race(fileName): # tipo = 1
	raceId, trackConfig, listHeader, listData = loadResultFile(fileName)
	if not raceId:
		return
	###########
	func_name = sys._getframe().f_code.co_name
	logger = logging.getLogger(func_name)
	logger.debug("Start | %s", fileName)
	timeStart = time.time()
	###########

	keyList = g_raceHeader.keys()
	keyList.sort()

	isValid = 0
	dictIdx = {}
	fieldList = ['raceId', 'trackConfig']
	for key in keyList:
		dictIdx[key] = listHeader.index(key) if key in listHeader else -1
		fieldList.append(g_raceHeader[key])
		isValid = (isValid or dictIdx[key] >= 0)

	if not isValid:
		logger.warning("Invalid File | %s", fileName)
		return 

	###########
	
	dbConnection = sqlite3.connect(PATH_GRANJA_DB)
	dbCursor = dbConnection.cursor()
		
	for row in listData:
		if not row:
			continue

		insertData = [raceId, trackConfig]
		for key in keyList:
			value = row[dictIdx[key]] if dictIdx[key] >= 0 else ''
			value = value.replace(',', '.') # pt_BR time format
			#value = value.replace('-', '') # no bestSpeed
			if value.find(':') > 0:
				valTime = value.split(':')
				value = float(valTime[1]) + 60 * float(valTime[0])
				value = float("{0:.3f}".format(value))
			insertData.append(value)

		logger.debug("INSERT OR REPLACE INTO races (%s) values (%s)" % (','.join(fieldList), ','.join(['?' for x in fieldList])), insertData)
		dbCursor.execute("INSERT OR REPLACE INTO races (%s) values (%s)" % (','.join(fieldList), ','.join(['?' for x in fieldList])), insertData)

	###########
	
	dbConnection.commit()
	dbConnection.close()

	elapsedTime = time.time() - timeStart
	logger.info("Finished | %s | Elapsed = %f", fileName, elapsedTime)

################################################################################
################################################################################
def loadResultFile(fileName):
	func_name = sys._getframe().f_code.co_name
	logger = logging.getLogger(func_name)
	###########
	logger.debug("Start | %s", fileName)
	timeStart = time.time()
	###########
	logger.debug("Open | %s", fileName)
	f = open(fileName, 'r')
	fileContent = f.read()
	f.close()
	###########
	raceId = int(basename(fileName).split('_')[0])
	###########
	logger.debug("BeautifulSoup")
	soup = BeautifulSoup(fileContent)
	###########
	headerbig = soup.find("div", { "class" : "headerbig" })
	if headerbig.text.find('KARTODROMO INTERNACIONAL GRANJA VIANA') < 0:
		logger.warning("Invalid file | %s", headerbig.text)
		return None,None,None,None
	trackConfig = ' '.join(headerbig.text.split(' ')[4:])
	trackConfig = trackConfig.strip()
	###########
	logger.debug("Find Header")
	table = soup.find('table')
	if not table:
		logger.warning("No Table in file | %s", fileName)
		return

	listHeader = [header.text.upper().encode('utf-8').strip() for header in table.findAll('th')]
	if not listHeader:
		logger.warning("No header in table | %s", fileName)
		return

	listData = []
	for row in table.findAll('tr'):
		cols = [data.text.strip() for data in row.findAll('td')]
		listData.append(cols)
	###########
	elapsedTime = time.time() - timeStart
	logger.info("Finished | %s | Elapsed = %f", fileName, elapsedTime)
	###########    
	return raceId, trackConfig, listHeader, listData

################################################################################
"""
Pos                 1
PIC                 1
No.                 019
Nome                DIEGO
Classe              INDOOR
Voltas              12
Total Tempo         18:29.327
Diff
Espaço
velocidade Media    39,371
Melhor Tempo        1:24.059
Melhor Veloc.       43,298
na volta.           9
Carro reg           cbf6d36c
Nat/State
Patrocinadores
Pontos              0
"""
################################################################################
def createDB():
	func_name = sys._getframe().f_code.co_name
	logger = logging.getLogger(func_name)
	logger.debug(PATH_GRANJA_DB)
	###########
	dbConnection = sqlite3.connect(PATH_GRANJA_DB)
	dbCursor = dbConnection.cursor()
	dbCursor.execute('''CREATE TABLE IF NOT EXISTS races (
		raceId INTEGER,
		trackConfig text,
		positionFinish INTEGER,
		numberOfLaps INTEGER,
		totalTime real,
		kartNumber INTEGER,
		driverName text,
		driverClass text,
		bestLapTime real,
		bestSpeed real,
		bestLap INTEGER,
		avgSpeed real
	)''')
	dbConnection.commit()
	dbConnection.close()
	logger.debug("DONE")

################################################################################
# MAIN
################################################################################
def main():
	appName = sys.argv[0]
	logging.basicConfig(
		filename = './log/' + appName + '_' + time.strftime("%Y%m%d_%H%M%S") + '.log',
		datefmt = '%Y-%m%d %H:%M:%S',
		format = '%(asctime)s | %(levelname)s | %(name)s  | %(message)s',
		level = logging.INFO
	)
	func_name = sys._getframe().f_code.co_name
	logger = logging.getLogger(func_name)
	logger.debug('Started')
	###
	parseArgs()
	###
	if not os.path.isfile(PATH_GRANJA_DB):
		createDB()
	###
	# 1) Init a Thread pool with the desired number of threads
	logger.debug('ThreadPool')
	pool = ThreadPool.ThreadPool(10)
	logger.debug('for file in glob.glob(%s)', g_inputPath)
	for file in glob.glob(g_inputPath):
		# 2) Add the task to the queue
		if re.search('_1.html$', file):
			pool.add_task(parseResult_Race, file)
		# TODO (?)
		# if re.search('_3.html$', file):
		# 	pool.add_task(parseResult_Laps, file)
	# 3) Wait for completion
	pool.wait_completion()
	###
	logger.debug('Finished')

################################################################################
################################################################################
### my_string = "blah, lots  ,  of ,  spaces, here "
### [x.strip() for x in my_string.split(',')]
if __name__ == '__main__':
	main()
