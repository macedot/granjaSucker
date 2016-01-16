#!/bin/bash

export PATH=".:$HOME:$PATH"

# Get ready to work
GRANJA_WORK_PATH="${HOME}/granjaSucker"
GRANJA_DB="${GRANJA_WORK_PATH}/sqlite/granjaResult.sqlite"

if [ ! -d "${GRANJA_WORK_PATH}" ]; then
	echo "Invalid GRANJA_WORK_PATH : ${GRANJA_WORK_PATH}" 1>&2
fi

if [ ! -f "${GRANJA_DB}" ]; then
	echo "Invalid GRANJA_DB : ${GRANJA_DB}" 1>&2
fi

# database
backup ${GRANJA_DB} 1>/dev/null

# Job is done!
exit 0
