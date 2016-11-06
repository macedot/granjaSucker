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

# database
backup ${GRANJA_DB}

# history
backup ${GRANJA_HISTORY_PATH}
if [ $? -eq 0 ]; then
	rm -fr ${GRANJA_HISTORY_PATH}/*.*
fi

# Job is done!
exit 0
