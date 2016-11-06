#!/bin/bash


declare baseName=$(basename $0)

function echoInfo {
	local msg=$1
	local DATETIME=$(date '+%Y-%m-%d %H:%M:%S')
	local logMsg="${DATETIME} INFO [${baseName}] ${msg}"
	echo $logMsg
  [ -f ${logFilePath} ] && echo $logMsg >> ${logFilePath}
	return 0
}

function echoError {
	local msg=$1
	DATETIME=$(date '+%Y-%m-%d %H:%M:%S')
	logMsg="${DATETIME} ERROR [${baseName}] ${msg}"
	echo $logMsg 1>&2
  [ -f ${logFilePath} ] && echo $logMsg >> ${logFilePath}
	return 0
}

export PATH=".:$HOME:$PATH"

# Get ready to work
GRANJA_WORK_PATH="${HOME}/granjaSucker"
GRANJA_RESULT_PATH="${HOME}/granjaResult"
GRANJA_HISTORY_PATH="${HOME}/granjaHistory"
GRANJA_CFG_LAST="${GRANJA_WORK_PATH}/last.granja"
GRANJA_DB="${GRANJA_WORK_PATH}/sqlite/granjaResult.sqlite"

if [ ! -d "${GRANJA_WORK_PATH}" ]; then
	echoError "Invalid GRANJA_WORK_PATH : ${GRANJA_WORK_PATH}"
fi

if [ ! -d "${GRANJA_RESULT_PATH}" ]; then
	echoError "Invalid GRANJA_WORK_PATH : ${GRANJA_RESULT_PATH}"
fi

if [ ! -d "${GRANJA_HISTORY_PATH}" ]; then
	echoError "Invalid GRANJA_WORK_PATH : ${GRANJA_HISTORY_PATH}"
fi

if [ ! -f "${GRANJA_CFG_LAST}" ]; then
	echoError "Invalid GRANJA_CFG_LAST : ${GRANJA_CFG_LAST}"
fi

if [ ! -f "${GRANJA_DB}" ]; then
	echoError "Invalid GRANJA_DB : ${GRANJA_DB}"
fi

# Get last fetch parameters

if [ ! -z "$1" ]; then
	lastReadID=$1
else
	lastReadID=$(head -1 ${GRANJA_CFG_LAST} | awk -F, '{print $1}')
fi

if [ ! -z "$2" ]; then
	howManyToFetch=$2
else
	howManyToFetch=$(head -1 ${GRANJA_CFG_LAST} | awk -F, '{print $2}')
fi

currentTime=$(date +%Y%m%d_%H%M%S)
logFilePath="${GRANJA_WORK_PATH}/log/${baseName}-${currentTime}.log"
findResultPattern="${GRANJA_RESULT_PATH}/*_1.html"

echoInfo "LOG: ${logFilePath}"
# Should we go?
previusPath=$(pwd -P)
cd ${GRANJA_WORK_PATH}
# fetch data from web
echoInfo "================================================================================"
echoInfo "python granjaMultiSucker.py --quant=${howManyToFetch} --id=${lastReadID} --outputPath=${GRANJA_RESULT_PATH}"
#echoInfo "================================================================================"
python granjaMultiSucker.py --quant=${howManyToFetch} --id=${lastReadID} --outputPath=${GRANJA_RESULT_PATH} &>> ${logFilePath}

numFetchResult=$(ls ${findResultPattern} 2>/dev/null | wc -l)
if [ $numFetchResult -le 0 ]; then
	echoError ">> NO RESULT FETCH!"
	exit 0
fi

# parse html into sqlite
echoInfo "================================================================================"
echoInfo "python granjaHtmlParse.py --inputPath=${findResultPattern}"
#echoInfo "================================================================================"
python granjaHtmlParse.py --inputPath="${findResultPattern}" &>> ${logFilePath}

# update statistics tables
echoInfo "================================================================================"
echoInfo "python granjaUpdateStatistics.py"
#echoInfo "================================================================================"
python granjaUpdateStatistics.py &>> ${logFilePath}

cd ${previusPath}
# Update status with last data
lastFile=$(ls ${findResultPattern}  | sort | tail -1)
echoInfo "lastFile = $lastFile"
lastID=$(basename ${lastFile} | awk -F_ '{print $1}')
echoInfo "lastID = $lastID"
lastID=$((lastID + numFetchResult))
echoInfo "lastID = $lastID"
echoInfo "$lastReadID -lt $lastID"
if [ "$lastReadID" -lt "$lastID" ]; then
	echoInfo "${lastID},${howManyToFetch} > ${GRANJA_CFG_LAST}"
	echo "${lastID},${howManyToFetch}" > ${GRANJA_CFG_LAST}
fi
mv ${GRANJA_RESULT_PATH}/* ${GRANJA_HISTORY_PATH}/ 2>/dev/null

# Job is done!
echoInfo "================================================================================"
echoInfo "# Job is done!"
exit 0
