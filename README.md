# granjaSucker

Quick-n-dirty implementation of web crawler for go-kart results from KGV (Kartodromo Granja Viana)

---

## 3rd Party Components

| Package | Description |
| --- | --- |
| CherryPy | [http://www.cherrypy.org/] (http://www.cherrypy.org/) |
| SQLite | [https://www.sqlite.org/] (https://www.sqlite.org/) |


## Lib
| File | Description |
| --- | --- |
| ThreadPool.py | Thread pool processing. Based on code from [Emilio Monti and Riccardo Govoni.] (http://code.activestate.com/recipes/577187-python-thread-pool/) |

## Main Files
| File | Description |
| --- | --- |
| granjaMultiSucker.py | Multi-thread web crawler. Saves a HTML file for each race result.  |
| granjaHtmlParse.py | Multi-thread HTML parser. Saves into SQLite database.  |
| granjaUpdateStatistics.py | Rebuild summary tables on SQLite database. |
| granjaView.py | HTTP to serve summary information.  |


## Shell Wrappers
| File | Description |
| --- | --- |
| granjaBackup.sh | Daily backup routines.  |
| granjaSeqRun.sh | Daily run script. |
| granjaViewServer.sh | Wrapper to restart HTTP server. |

## Aux File
| File | Description |
| --- | --- |
| last.granja | Stores next last ID and fetch size. |

