#! /bin/bash

#bash /scheduled_scripts/run_hourly.sh &
#bash /scheduled_scripts/run_daily.sh &

#bash /scheduled_scripts/back_up_database.sh
bash /scheduled_scripts/vacuum_database.sh
#bash /scheduled_scripts/restore_database.sh

echo "Starting server..."
python /app/webserver.py
