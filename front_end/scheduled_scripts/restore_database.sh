#! /bin/bash

dump_file=/database/CodeBuddy.dump.gz

echo "Restoring database from ${dump_file}..."

zcat ${dump_file} | sqlite3 /database/CodeBuddy.db
