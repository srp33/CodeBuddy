#! /bin/bash

#bash /scheduled_scripts/run_hourly.sh &
#bash /scheduled_scripts/run_daily.sh &

echo "Starting server..."
python /app/webserver.py 9799
