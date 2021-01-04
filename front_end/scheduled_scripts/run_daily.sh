#! /bin/bash

this_dir="$(dirname $0)"

# This creates an infinite loop.
while :
do
  # We sleep a little while to avoid conflicting with hourly tasks.
  sleep 5m

  bash ${this_dir}/summarize_logs.sh
  bash ${this_dir}/vacuum_database.sh

  sleep 24h
done
