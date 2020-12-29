#! /bin/bash

echo "Vacuuming database [$(date)]..."

sqlite3 /database/CodeBuddy.db "VACUUM;"

echo "Done vacuuming database [$(date)]..."
