#! /bin/bash

in_file_pattern="/logs/codebuddy.log*"
out_file=/logs/summarized/access.log.gz

# This approach is not guaranteed to summarize every entry.
# It might miss a few that are logged while the temp file is being created.
cat ${in_file_pattern} | gzip > /logs/temp.log.gz
rm -fv ${in_file_pattern}

python /app/summarize_logs.py /logs/temp.log.gz ${out_file}
