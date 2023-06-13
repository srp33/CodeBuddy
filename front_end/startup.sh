#! /bin/bash

mode=$(grep "^mode: " /Settings.yaml | sed "1s/mode: //")

#if [[ "${mode}" == "production" ]]
#then
#  nohup bash /app/scheduled_scripts/run_hourly.sh > /tmp/CodeBuddy_hourly.log &
#  nohup bash /app/scheduled_scripts/run_daily.sh > /tmp/CodeBuddy_daily.log &
#fi

#bash /app/scheduled_scripts/summarize_logs.sh

echo "Starting front-end server..."
python /app/server/webserver.py
