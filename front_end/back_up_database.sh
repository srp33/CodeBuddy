#! /bin/bash

dump_file=database/CodeBuddy.dump.gz

echo "Backing up database to ${dump_file}..."

sqlite3 database/CodeBuddy.db .dump | gzip -c > ${dump_file}
