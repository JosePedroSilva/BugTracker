#####################################################
            # Tests DB connection
#####################################################

import psycopg2

try:
    connection = psycopg2.connect(user="postgres",
                                  password='2427',
                                  host='127.0.0.1',
                                  port='5432',
                                  database='bugTracker')
    cursor = connection.cursor()
    print(connection.get_dsn_parameters(), "\n")

    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print(f'Version: {record}')

except (Exception, psycopg2.Error) as error:
    print(error)

finally:
    if(connection):
        cursor.close()
        connection.close()
        print('Connection closed')
