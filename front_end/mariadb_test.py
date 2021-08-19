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
