import mysql.connector
from config import host, database, user, password

try:
    cnx = mysql.connector.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )

    if cnx.is_connected():
        print(f"Успешно подключено к базе данных '{database}'")

    cursor = cnx.cursor()

except mysql.connector.Error as e:
    print(f"Ошибка при подключении к базе данных: {e}")


# Ваш код для выполнения операций с базой данных здесь
def save_user(user_id, username, first_name, last_name):
    sql = "INSERT INTO users (user_id, username, first_name, last_name) VALUES (%s, %s, %s, %s)"
    val = (user_id, username, first_name, last_name)

    cursor.execute(sql, val)
    cnx.commit()


def is_user_exists(user_id):
    sql = "SELECT COUNT(*) FROM users WHERE user_id = %s"
    val = (user_id,)

    cursor.execute(sql, val)

    result = cursor.fetchone()[0]  # Получаем значение COUNT(*)
    print(result)

    return result > 0


def get_user_info(user_id, field):
    try:
        cursor.execute(f"SELECT {field} FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        return result
    except mysql.connector.Error as e:
        print(f"Ошибка при получении информации о пользователе из базы данных: {e}")
        return None


# create function to update user info in database with choice what to update
def update_user_info(user_id, field, value):
    try:
        if (field == 'questions_qty' or field == 'correct_answers' or field == 'incorrect_answers'
                or field == 'experience' or field == 'movie_answers' or field == 'movie_correct' or field == 'movie_incorrect'):
            result = get_user_info(user_id, field)[0]
            value += result
            cursor.execute(f"UPDATE users SET {field} = %s WHERE user_id = %s", (value, user_id))
            cnx.commit()
    except mysql.connector.Error as e:
        print(f"Ошибка при обновлении информации о пользователе в базе данных: {e}")
        return None
    return True


def get_top_users(field):
    try:
        cursor.execute(f"SELECT * FROM users ORDER BY {field} DESC LIMIT 10")
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as e:
        print(f"Ошибка при получении топа пользователей из базы данных: {e}")
        return None


def auto_update_user_level(user_id, experience):
    get_level_query = "SELECT level FROM users WHERE user_id = %s"
    cursor.execute(get_level_query, (user_id,))
    current_level = cursor.fetchone()[0]
    current_experience = get_user_info(user_id, 'experience')[0]

    print(f"level {current_level}")

    # Определяем пороговые значения опыта для каждого уровня
    done_experience = experience + current_experience
    experience_threshold = 4 * (2 ** (current_level - 1))

    # Если пользователь достиг порогового значения опыта, повышаем уровень
    if done_experience >= experience_threshold:
        new_level = current_level + 1

        # Обновляем уровень пользователя в базе данных
        update_level_query = "UPDATE users SET level = %s WHERE user_id = %s"
        cursor.execute(update_level_query, (new_level, user_id))

        update_experience_query = "UPDATE users SET experience = %s WHERE user_id = %s"
        cursor.execute(update_experience_query, (done_experience - experience_threshold, user_id))

        # Подтверждаем изменения
        cnx.commit()

        return new_level
    result = get_user_info(user_id, 'experience')[0]
    update_experience_query = "UPDATE users SET experience = %s WHERE user_id = %s"
    cursor.execute(update_experience_query, (done_experience + result, user_id))

    cnx.commit()
    return current_level
