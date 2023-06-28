#! /bin/bash

this_dir="$(dirname $0)"
backup_hour="$1"

# This creates an infinite loop.
while :
do
  current_hour=$(date +%H)

  if [ "${current_hour}" -eq "${backup_hour}" ]
  then
    echo "Time to back up [$(date)]."

    bash ${this_dir}/summarize_logs.sh &
    bash ${this_dir}/back_up_database.sh &
    wait
  else
    echo "Not time to back up [$(date)]."
  fi

  sleep 1h
done