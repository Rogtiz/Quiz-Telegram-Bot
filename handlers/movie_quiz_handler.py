import asyncio
from aiogram import types
from aiogram.types import FSInputFile
from handlers.check_movie_answer import is_close_enough
from config import API_KEY, API_URL
import requests
import handlers.user_handlers as uh
from database import db_queries as db
import handlers.file_handlers as fh

# Словарь для хранения данных о викторине
all_data = {}
used_hints = 0
all_hints = ['📅 Год выпуска', '🍿 Жанры', '🎥 Имя режиссера']


async def get_movie_description():
    global all_data
    headers = {'accept': 'application/json', 'X-API-KEY': API_KEY}
    response = requests.get(API_URL, headers=headers)
    if response.status_code == 200:
        data = response.json()
        all_data = data
        return data['description'], data['name']
    else:
        return None, None


current_question = 0
user_answers = []
answers = ['nope']
optional_info = []


async def start_movie_quiz(message: types.Message):
    global answers, optional_info, all_data
    description, movie_name = await get_movie_description()
    answers.append(movie_name)

    if len(optional_info) == 0:
        optional_info = [1]
        optional_info[0] = all_data
    else:
        optional_info.append(all_data)

    if description:
        await message.answer(description)
        await answers_keyboard(message)
    else:
        await message.answer("Ошибка при получении данных о фильме.")


async def answers_keyboard(message: types.Message):
    kb = [
        [types.KeyboardButton(text="🤷‍♂️ Я не знаю ответа")],
        [types.KeyboardButton(text="💡 Подсказка")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    return await message.answer(f"Напишите название фильма", reply_markup=keyboard)


def get_hints():
    global all_data
    yearOfRelease = all_data['year']
    genres = all_data['genres']
    for person in all_data['persons']:
        if person['enProfession'] == 'director':
            director = person['name']
            break
    return yearOfRelease, genres, director


async def get_hints_keyboard(message: types.Message):
    kb = [
        [types.KeyboardButton(text="📅 Год выпуска")],
        [types.KeyboardButton(text="🍿 Жанры")],
        [types.KeyboardButton(text="🎥 Имя режиссера")],
        [types.KeyboardButton(text="✏️ Ответить")]
    ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

    await message.answer(f"Выберите подсказку", reply_markup=keyboard)


async def give_hints(message: types.Message):
    global used_hints, current_question
    yearOfRelease, genres, director = get_hints()
    if message.text == '📅 Год выпуска':
        await message.answer(f"Год выпуска: {yearOfRelease}")
        if not (used_hints >= ((current_question + 1) * 3)):
            used_hints += 1
    if message.text == '🍿 Жанры':
        done_genres = ''
        for genre in genres:
            done_genres += genre['name'] + ', '
        await message.answer(f"Жанры: {done_genres}")
        if not (used_hints >= ((current_question + 1) * 3)):
            used_hints += 1
    if message.text == '🎥 Имя режиссера':
        await message.answer(f"Имя режиссера: {director}")
        if not (used_hints >= ((current_question + 1) * 3)):
            used_hints += 1


async def movie_quiz_answer(message: types.Message):
    global used_hints, all_data, current_question, user_answers

    if current_question < 5:
        user_answer = message.text

        if is_close_enough(user_answer, all_data['name']):
            user_answers.append(True)
        else:
            user_answers.append(False)

        current_question += 1

        if current_question < 5:
            await start_movie_quiz(message)
        else:
            await show_results(message)


async def get_movies_file(message: types.Message):
    global optional_info
    info = "Информация о фильмах из вопросов:\n\n"

    for movie in optional_info:
        for person in movie['persons']:
            if person['enProfession'] == 'director':
                director = person['name']
                break
        info += (f"Название фильма: {movie['name']}\nОписание: {movie['description']}\nРежиссер: {director}\nГод "
                 f"выпуска: {movie['year']}\nСтрана производства: {movie['countries'][0]['name']}\nРейтинг на "
                 f"Кинопоиске: {movie['rating']['kp']}\nРейтинг на IMDB: {movie['rating']['imdb']}\nСтраница фильма "
                 f"на Кинопоиске: https://www.kinopoisk.ru/film/{movie['id']}/\n\n\n")

    user_id = message.from_user.id
    filename = fh.save_info_to_file(user_id, info, 'movie_info')

    file = FSInputFile(filename)

    await message.answer_document(file)
    optional_info.clear()

    await asyncio.sleep(1)
    fh.delete_file(filename)


async def not_know_answer(message: types.Message):
    global user_answers, current_question
    user_answers.append(False)
    current_question += 1

    if current_question < 5:
        await start_movie_quiz(message)
    else:
        await show_results(message)


async def show_results(message: types.Message):
    global user_answers, current_question, used_hints, answers, optional_info
    correct_answers = user_answers.count(True)

    message_text = f"🎬 Результаты киновикторины:\nПравильных ответов: {correct_answers}/5\n\nОтветы на вопросы:\n"
    for i in range(5):
        message_text += f"{i + 1}. {answers[i + 1]}\n"
    await message.answer(message_text)

    # Сбросим переменные для возможности начать новую викторину
    current_question = 0
    user_answers = []
    current_level = int(db.get_user_info(message.from_user.id, 'level')[0])
    possible_level = current_level
    db.update_user_info(message.from_user.id, 'movie_answers', 5)
    db.update_user_info(message.from_user.id, 'movie_correct', correct_answers)
    db.update_user_info(message.from_user.id, 'movie_incorrect', 5 - correct_answers)
    if correct_answers > 0:
        if used_hints == 0:
            possible_level = db.auto_update_user_level(message.from_user.id, correct_answers * 5)
        elif 0 < used_hints < 3:
            possible_level = db.auto_update_user_level(message.from_user.id, correct_answers * 3)
        else:
            possible_level = db.auto_update_user_level(message.from_user.id, correct_answers * 1)

    print(possible_level)
    if possible_level > current_level:
        await message.answer(f"🎉 Поздравляем, вы перешли на {possible_level} уровень!")
    used_hints = 0
    answers = ['nope']
    kb = [
        [types.KeyboardButton(text="🔍 Получить информацию")],
        [types.KeyboardButton(text="🏠 Главное меню")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    return await message.answer(f"Хотите ли вы получить дополнительную информацию об этих фильмах?",
                                reply_markup=keyboard)
