#!/bin/bash

export PATH=".:$HOME:$PATH"

# Get ready to work
GRANJA_WORK_PATH="${HOME}/granjaSucker"
GRANJA_RESULT_PATH="${HOME}/granjaResult"
GRANJA_HISTORY_PATH="${HOME}/granjaHistory"
GRANJA_CFG_LAST="${GRANJA_WORK_PATH}/last.granja"
GRANJA_DB="${GRANJA_WORK_PATH}/sqlite/granjaResult.sqlite"

if [ ! -d "${GRANJA_WORK_PATH}" ]; then
	echo "Invalid GRANJA_WORK_PATH : ${GRANJA_WORK_PATH}" 1>&2
fi

if [ ! -d "${GRANJA_RESULT_PATH}" ]; then
	echo "Invalid GRANJA_WORK_PATH : ${GRANJA_RESULT_PATH}" 1>&2
fi

if [ ! -d "${GRANJA_HISTORY_PATH}" ]; then
	echo "Invalid GRANJA_WORK_PATH : ${GRANJA_HISTORY_PATH}" 1>&2
fi

if [ ! -f "${GRANJA_CFG_LAST}" ]; then
	echo "Invalid GRANJA_CFG_LAST : ${GRANJA_CFG_LAST}" 1>&2
fi

if [ ! -f "${GRANJA_DB}" ]; then
	echo "Invalid GRANJA_DB : ${GRANJA_DB}" 1>&2
fi

# Get last fetch parameters
lastID=$(head -1 ${GRANJA_CFG_LAST} | awk -F, '{print $1}')
howManyToFetch=$(head -1 ${GRANJA_CFG_LAST} | awk -F, '{print $2}')
baseName=$(basename $0)
currentTime=$(date +%Y%m%d_%H%M%S)
logFilePath="${GRANJA_WORK_PATH}/log/${baseName}-${currentTime}.log"
findResultPattern="${GRANJA_RESULT_PATH}/*_1.html"

# Should we go? 
currentPath=$(pwd -P)
cd ${GRANJA_WORK_PATH}
# fetch data from web
echo "================================================================================" >> ${logFilePath}
echo "python granjaMultiSucker.py --quant=${howManyToFetch} --id=${lastID} --outputPath=${GRANJA_RESULT_PATH}" >> ${logFilePath}
echo "================================================================================" >> ${logFilePath}
python granjaMultiSucker.py --quant=${howManyToFetch} --id=${lastID} --outputPath=${GRANJA_RESULT_PATH} &>> ${logFilePath}

numFetchResult=$(ls ${GRANJA_RESULT_PATH}/*_1.html 2>/dev/null | wc -l)

if [ $numFetchResult -le 0 ]; then
	echo ">> NO RESULT FETCH!" &>> ${logFilePath}
	exit 0
fi

# database
#backup ${GRANJA_DB} 1>/dev/null

# parse html into sqlite
echo "================================================================================" >> ${logFilePath}
echo "python granjaHtmlParse.py --inputPath=${findResultPattern}" >> ${logFilePath}
echo "================================================================================" >> ${logFilePath}
python granjaHtmlParse.py --inputPath=${findResultPattern} &>> ${logFilePath}
cd ${currentPath}

# Update status with last data
#lastID=$((lastID + numFetchResult))
lastFile=$(ls ${findResultPattern}  | sort | tail -1)
lastID=$(basename ${lastFile} | awk -F_ '{print $1}')
echo "${lastID},${howManyToFetch}" > ${GRANJA_CFG_LAST}
mv ${GRANJA_RESULT_PATH}/*.* ${GRANJA_HISTORY_PATH}/ 2>/dev/null

# Job is done!
exit 0
