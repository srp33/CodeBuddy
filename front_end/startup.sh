#! /bin/bash

mode=$(grep "^mode: " /Settings.yaml | sed "1s/mode: //")
backup_hour=$(grep "^backup_hour: " /Settings.yaml | sed "1s/backup_hour: //")

bash /app/scheduled_scripts/summarize_logs.sh &
bash /app/scheduled_scripts/back_up_database.sh &
wait

if [[ "${mode}" == "production" ]]
then
   bash /app/scheduled_scripts/vacuum_database.sh

   echo "Initializing hourly maintenance script..."
   nohup bash /app/scheduled_scripts/run_hourly.sh ${backup_hour} > /tmp/CodeBuddy_hourly.log &
fi

echo "Starting front-end server..."
python /app/server/webserver.py
