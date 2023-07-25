# <copyright_statement>
#   CodeBuddy - A learning management system for computer programming
#   Copyright (C) 2023 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

import mariadb
import sys

HOST = "127.0.0.1"
PORT = 3305

with open("secrets/MARIADB_USER") as pfile:
    USERNAME = pfile.read().strip("\n")

with open("secrets/MARIADB_PASSWORD") as pfile:
    PASSWORD = pfile.read().strip("\n")

with open("secrets/MARIADB_DATABASE") as pfile:
    DATABASE = pfile.read().strip("\n")

# Connect to MariaDB Platform
def connectDB():
    try:
        conn = mariadb.connect(
            user=USERNAME,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            database=DATABASE
        )

        print('Sucessfully connected to MariaDB!\n')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        print(e)
        sys.exit(1)

    return conn

try:
    # Connect to database
    conn = connectDB()
    cur = conn.cursor()

    # Create table
    cur.execute('''CREATE TABLE IF NOT EXISTS users (user_id text, email_address text, name text)''')
    sql = '''INSERT INTO users (user_id, email_address, name)
             VALUES (?, ?, ?)'''

    # Insert values into table
    cur.execute(sql, ('person1', 'person1@gmail.com', 'FirstName1 LastName1'))
    cur.execute(sql, ('person2', 'person2@gmail.com', 'FirstName2 LastName2'))
    cur.execute(sql, ('person3', 'person3@gmail.com', 'FirstName3 LastName3'))

    conn.commit()

    # Print values from database
    cur.execute("SELECT * FROM users")
    for user in cur:
        print(f"ID: {user[0]}, email: {user[1]}, name: {user[2]}")

except mariadb.Error as e:
    print(e)
    print(f"Error: {e}")

conn.close()
