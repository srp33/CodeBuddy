# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

#! /bin/bash

mode=$(grep "^mode: " /Settings.yaml | sed "1s/mode: //")
backup_hour=$(grep "^backup_hour: " /Settings.yaml | sed "1s/backup_hour: //")

bash /app/scheduled_scripts/summarize_logs.sh

if [[ "${mode}" == "production" ]]
then
  bash /app/scheduled_scripts/summarize_logs.sh &
  bash /app/scheduled_scripts/back_up_database.sh &
  wait

  bash /app/scheduled_scripts/vacuum_database.sh

  echo "Initializing hourly maintenance script..."
  nohup bash /app/scheduled_scripts/run_hourly.sh ${backup_hour} > /tmp/CodeBuddy_hourly.log &
fi

echo "Starting front-end server..."
python /app/server/webserver.py
