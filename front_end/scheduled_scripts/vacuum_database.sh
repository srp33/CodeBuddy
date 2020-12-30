#! /bin/bash

echo "Vacuuming database [$(date)]..."

cd /database
sqlite3 CodeBuddy.db "VACUUM;"

echo "Done vacuuming database [$(date)]..."
