#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import sqlite3
import cherrypy
import logging
import htmlmin

from prettytable import from_db_cursor

################################################################################
# STATIC DEF
################################################################################
PATH_GRANJA_DB = 'sqlite/granjaResult.sqlite'

################################################################################
# GLOBAL DEF
################################################################################


################################################################################
################################################################################
def tableData2Html(tableName):
	htmlcode = """<html><head><title>%s</title><link href="/static/style.css" rel="stylesheet"><head><body>""" % (tableName)

	try:
		con = sqlite3.connect(PATH_GRANJA_DB)
		con.row_factory = sqlite3.Row
		db_cur = con.cursor()
		db_cur.execute('SELECT * FROM %s;' % (tableName))
		pt = from_db_cursor(db_cur)
		pt.float_format = 1.3
		htmlcode += pt.get_html_string(attributes = {"id": "sort", "class": "sort"})
	except sqlite3.Error, e:
		if con:
			con.rollback()
		logging.error("Error %s:" % e.args[0])
	finally:
		if con:
			con.close()

	htmlcode += """<script src='/static/tablesort.min.js'></script><script src='/static/tablesort.number.js'></script><script>new Tablesort(document.getElementById('sort'));</script></body></html>"""
	htmlcodemin = htmlmin.minify(htmlcode, remove_empty_space = True)
	htmlcodemin = htmlcodemin.replace('<tr><th>', '<thead><tr><th>')
	htmlcodemin = htmlcodemin.replace('</th></tr>', '</th></tr></thead>')
	htmlcodemin = htmlcodemin.replace('<th>', '<th class="sort-header">')
	htmlcodemin = re.sub(r'\bNone\b', '0', htmlcodemin)

	return htmlcodemin

################################################################################
################################################################################
class granjaView(object):
	@cherrypy.expose
	def index(self):
		pass

	@cherrypy.expose
	def INDOOR_RANKING_LAPTIME(self):
		return tableData2Html('INDOOR_RANKING_LAPTIME_C01')

	@cherrypy.expose
	def PAROLIN_RANKING_LAPTIME(self):
		return tableData2Html('PAROLIN_RANKING_LAPTIME_C01')

	@cherrypy.expose
	def GERAL_RANKING_LAPTIME_C01(self):
		return tableData2Html('GERAL_RANKING_LAPTIME_C01')

	@cherrypy.expose
	def GERAL_RANKING_LAPTIME(self):
		return tableData2Html('GERAL_RANKING_LAPTIME')

	@cherrypy.expose
	def ALLTIME_RANKING_LAPTIME(self):
		return tableData2Html('ALLTIME_RANKING_LAPTIME')

	@cherrypy.expose
	def CKC_BI_INDOOR(self):
		return tableData2Html('CKC_BI_INDOOR')

	@cherrypy.expose
	def CKC_BI_PAROLIN(self):
		return tableData2Html('CKC_BI_PAROLIN')

################################################################################
################################################################################
if __name__ == '__main__':
	cherrypy.config.update({'server.socket_host': '0.0.0.0'})
	conf = {
		'/': {
			#'tools.sessions.on': True,
			'tools.staticdir.root': os.path.abspath(os.getcwd()),
			'tools.caching.on' : True,
			'tools.caching.delay' : 3600,
		},
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': './public',
			'tools.caching.on' : True,
			'tools.caching.delay' : 3600,
		}
	}
	cherrypy.quickstart(granjaView(), '/', conf)

#TODO:
#/index/ -> iframe com rankings (SEM BI)
#/ckc/indoor/podium
#/ckc/indoor/laptime
#/ckc/indoor/bi
#/ckc/parolim/podium
#/ckc/parolim/laptime
#/ckc/parolim/bi
