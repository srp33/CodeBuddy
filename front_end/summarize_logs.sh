#! /bin/bash

in_file_prefix="/logs/codebuddy.log"
touch ${in_file_prefix}
#num_rows_newest_file="$(wc -l ${in_file_prefix} | cut -d' ' -f1)"
out_dir=/logs/summarized
temp_file=$(mktemp)

python /app/summarize_logs.py ${in_file_prefix} ${out_dir} ${temp_file}
rm -f ${temp_file}

cat ${in_file_prefix}* | gzip > /logs/archive/$(date +"%y-%m-%d-%H").log.gz
rm -f ${in_file_prefix}*

python /app/delete_old_logs.py /logs/archive
