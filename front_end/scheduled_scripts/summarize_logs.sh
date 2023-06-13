#! /bin/bash

echo "Summarizing log files [$(date)]..."

in_file_prefix="/logs/codebuddy.log"
out_dir=/logs/summarized
temp_file=~/temp_summarize_logs

if [ ! -f ${in_file_prefix} ]
then
  touch ${in_file_prefix}
fi

python /app/scheduled_scripts/summarize_logs.py ${in_file_prefix} ${out_dir} ${temp_file}
exit
rm -f ${temp_file}

cat ${in_file_prefix}* | gzip > /logs/archive/$(date +"%y-%m-%d-%H").log.gz
rm -f ${in_file_prefix}*

python /app/scheduled_scripts/delete_old_logs.py /logs/archive

echo "Done summarizing log files [$(date)]..."
