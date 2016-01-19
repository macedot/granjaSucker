#!/usr/bin/python

import requests
import getopt
import sys
import os
import logging
import time
from ThreadPool import ThreadPool

################################################################################
# STATIC DEF
################################################################################
LOGIN_URL = 'http://www.kartodromogranjaviana.com.br/resultados/resultados_cad.php'
LOGIN_PARAM = {
	'email' : 'granja@macedo.me',
	'opt' : 'L',
	'r' : '',
}
RESULT_URL = 'http://www.kartodromogranjaviana.com.br/resultados/resultados_folha.php'

################################################################################
# GLOBAL DEF
################################################################################
tipoResult = 1
idResult = 30000
quantResult = 1000
outputPath = (os.environ['HOME'] if 'HOME' in os.environ else '.') + '/granjaResult'

################################################################################
################################################################################
def parseArgs():
	global tipoResult
	global idResult
	global quantResult
	global outputPath

	try:

		func_name = sys._getframe().f_code.co_name
		logger = logging.getLogger(func_name)

		opts, args = getopt.getopt(sys.argv[1:], "t:i:q:", ["tipo=", "id=", "quant=", "outputPath="])
		for o, a in opts:
			if o in ("-t", "--tipo"):
				tipoResult = int(a)
			elif o in ("-i", "--id"):
				idResult = int(a)
			elif o in ("-q", "--quant"):
				quantResult = int(a)
			elif o in ("-o", "--outputPath"):
				outputPath = str(a)
			else:
				assert False, "unhandled option"

		logger.debug("tipoResult = %d; idResult = %d; quantResult = %d", tipoResult, idResult, quantResult)
	except getopt.GetoptError as err:
		print str(err) # will print something like "option -a not recognized"
		sys.exit(2)
	except:
		print "Unexpected error:", sys.exc_info()[0]
		sys.exit(9)

################################################################################
################################################################################
def downloadResult(session, idAtual):
	func_name = sys._getframe().f_code.co_name
	logger = logging.getLogger(func_name)

	fileName = "%s/%d_%d.html" % (outputPath, idAtual, tipoResult)
	if os.path.isfile(fileName):
#        if os.path.getsize(fileName) > 1014:
		logger.debug("tipoResult = %d; idResult = %d | File Exists | SKIP", tipoResult, idAtual)
		return

	logger.debug("tipoResult = %d; idResult = %d | Start", tipoResult, idAtual)
	timeStart = time.time()

	url = "%s?tipo=%d&id=%d" % (RESULT_URL, tipoResult, idAtual)
	logger.debug("tipoResult = %d; idResult = %d | %s", tipoResult, idAtual, url)
	r = session.get(url)

	contentSize = len(r.content)
	if contentSize < 1014:
		logger.debug("tipoResult = %d; idResult = %d | Response too short | SKIP | %d", tipoResult, idAtual, contentSize)
		return

	logger.debug("tipoResult = %d; idResult = %d | %s", tipoResult, idAtual, fileName)
	f = open(fileName, 'w+')
	f.write(r.content)
	f.close()

	# run your code
	elapsedTime = time.time() - timeStart

	logger.info("tipoResult = %d; idResult = %d; Elapsed = %f | Finished | %s", tipoResult, idAtual, elapsedTime, fileName)

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

	parseArgs()

	logger.debug('requests.session')
	session = requests.session()
	# `mount` a custom adapter that retries failed connections for HTTP and HTTPS requests.
	session.mount("http://", requests.adapters.HTTPAdapter(max_retries=10))

	logger.debug('session.post')
	r = session.post(LOGIN_URL, data = LOGIN_PARAM)

	idResultEnd = idResult
	idResultBegin = idResult - quantResult
	# 1) Init a Thread pool with the desired number of threads
	logger.debug('ThreadPool')
	pool = ThreadPool(10)
	logger.debug('for idAtual in xrange(%d, %d, -1)' % (idResultEnd, idResultBegin))
	for idAtual in xrange(idResultEnd, idResultBegin, -1):
		# 2) Add the task to the queue
		pool.add_task(downloadResult, session, idAtual)
	# 3) Wait for completion
	pool.wait_completion()
	###
	logger.info('Finished')

################################################################################
################################################################################
if __name__ == '__main__':
	main()
