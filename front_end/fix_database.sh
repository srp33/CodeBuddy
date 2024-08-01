# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

#! /bin/bash

set -o errexit

cp -v database/CodeBuddy.db /tmp/CodeBuddy.db

echo "Dumping the database to a temp file..."
sqlite3 /tmp/CodeBuddy.db .dump > /tmp/database_dump.sql

echo "Restoring the database to a temp file..."
sqlite3 /tmp/CodeBuddy2.db < /tmp/database_dump.sql

mv -v /tmp/CodeBuddy2.db database/CodeBuddy.db
