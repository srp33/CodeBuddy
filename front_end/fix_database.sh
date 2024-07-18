#! /bin/bash

set -o errexit

cp -v database/CodeBuddy.db /tmp/CodeBuddy.db

echo "Dumping the database to a temp file..."
sqlite3 /tmp/CodeBuddy.db .dump > /tmp/database_dump.sql

echo "Restoring the database to a temp file..."
sqlite3 /tmp/CodeBuddy2.db < /tmp/database_dump.sql

mv -v /tmp/CodeBuddy2.db database/CodeBuddy.db
