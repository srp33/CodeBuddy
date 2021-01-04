#! /bin/bash

this_dir="$(dirname $0)"

# This creates an infinite loop.
while :
do
  sleep 1m
  bash ${this_dir}/back_up_database.sh
  sleep 1h
done
