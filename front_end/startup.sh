#! /bin/bash

mode=$(grep "^mode: " /Settings.yaml | sed "1s/mode: //")

#bash /scheduled_scripts/run_hourly.sh &
#bash /scheduled_scripts/run_daily.sh &

#bash /scheduled_scripts/back_up_database.sh

if [[ "${mode}" == "production" ]]
then
  bash /app/scheduled_scripts/vacuum_database.sh
fi

#bash /scheduled_scripts/restore_database.sh

echo "Starting server..."
python /app/server/webserver.py
