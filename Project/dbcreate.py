import mysql.connector
from mysql.connector import errorcode

DB_NAME = 'Tutor2'
USER = 'root'
PASSWORD = 'Kalparatna@2023'
HOST = 'localhost' 

try:
    conn = mysql.connector.connect(user=USER, password=PASSWORD, host=HOST)

    cursor = conn.cursor()

    create_database_query = f"CREATE DATABASE {DB_NAME}"

    cursor.execute(create_database_query)

    print(f"Database '{DB_NAME}' created successfully!")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
finally:
    cursor.close()
    conn.close()
