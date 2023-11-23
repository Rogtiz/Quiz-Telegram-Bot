import mysql.connector
from config import host, database, user, password

try:
    connection = mysql.connector.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )

    if connection.is_connected():
        print(f"Успешно подключено к базе данных '{database}'")


except mysql.connector.Error as e:
    print(f"Ошибка при подключении к базе данных: {e}")
