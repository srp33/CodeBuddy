#! /bin/bash

db_file=/database/CodeBuddy.db
dump_file=/database/CodeBuddy.dump.gz

if [ -f ${db_file} ]
then
  echo Moving database from ${db_file} to ${db_file}.2
  mv ${db_file} ${db_file}.2
fi

echo "Restoring database from ${dump_file} to ${db_file}..."

zcat ${dump_file} | sqlite3 /database/CodeBuddy.db