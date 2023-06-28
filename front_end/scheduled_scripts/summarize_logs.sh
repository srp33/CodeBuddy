#! /bin/bash

set -e

echo "Summarizing log files [$(date)]..."

in_file_prefix="/app/logs/codebuddy.log"
summary_file=/app/logs/summarized.json
archive_file=/app/logs/archive.log.gz

if [ ! -f ${in_file_prefix} ]
then
  touch ${in_file_prefix}
fi

python /app/scheduled_scripts/summarize_logs.py ${in_file_prefix} ${summary_file} ${archive_file}

#python /app/scheduled_scripts/delete_old_logs.py /logs/archive

echo "Done summarizing log files [$(date)]..."