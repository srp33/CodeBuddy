#! /bin/bash

in_file=/app/database/CodeBuddy.db
out_file=/app/database/CodeBuddy_backup.db

rm -f ${out_file}

echo "Backing up ${in_file} to ${out_file} [$(date)]..."

python3 /app/scheduled_scripts/back_up_database.py ${in_file} ${out_file}

echo "Done backing up ${in_file} to ${out_file} [$(date)]."