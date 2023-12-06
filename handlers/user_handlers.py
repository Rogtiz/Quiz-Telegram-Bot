import requests
import logging
from aiogram import types
from aiogram.filters import Command
# from aiogram.filters import Command
import handlers.movie_quiz_handler as mq
from database import db_queries as db


in_quiz = False
questions = [{"answers": [False]}, {"answers": [False]}, {"answers": [False]}, {"answers": [False]}, {"answers": [False]}]

async def main_menu(message: types.Message):
    kb = [
        [types.KeyboardButton(text="🧠 Викторина"), types.KeyboardButton(text="🎬 Киновикторина")],
        [types.KeyboardButton(text="📊 Статистика"), types.KeyboardButton(text="🏆 Топ")],
        [types.KeyboardButton(text="❓ О викторине"), types.KeyboardButton(text="❓ О киновикторине")]
    ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

    await message.answer("Главное меню:", reply_markup=keyboard)


async def cmd_start(message: types.Message):
    if not db.is_user_exists(message.from_user.id):
        db.save_user(message.from_user.id, message.from_user.username, message.from_user.first_name,
                     message.from_user.last_name)

    await message.answer(
        '👋 Привет, я бот, который дает вам возможность поиграть вам в викторину и выяснить, кто тут самый умный!')
    await main_menu(message)


async def cmd_help(message: types.Message):
    await message.answer('✍️ Список доступный команд:\n/victory - Начать викторину\n/help - Помощь\n/stop - '
                         'Остановить викторину')
    await message.delete()


async def cmd_stats(message: types.Message):
    if not db.is_user_exists(message.from_user.id):
        await message.reply('❌ Вы не можете использовать данную команду. Для регистрации введите /start')
    else:
        result = db.get_user_info(message.from_user.id, '*')
        print(result)
        username = message.from_user.username
        stats_level = result[6]
        stats_experience = result[5]
        experience_threshold = 4 * (2 ** (stats_level - 1))
        stats_questions_qty = result[7]
        stats_correct_answers = result[8]
        stats_incorrect_answers = result[9]
        stats_movie_questions_qty = result[10]
        stats_movie_correct = result[11]
        stats_movie_incorrect = result[12]

        await message.answer(f"📊 <b>Статистика пользователя {username}</b>:\n\n💎 <b>Уровень:</b> {stats_level}\n"
                             f"⏳ <b>Опыт:</b> {stats_experience}/{experience_threshold}\n\n"
                             f"📌 <b>Количество вопросов:</b> {stats_questions_qty}\n🟩 <"
                             f"b>Правильных ответов:</b> {stats_correct_answers}\n"
                             f"🟥 <b>Неправильных ответов:</b> {stats_incorrect_answers}\n\n🎬 <b>Киновикторина:</b>\n"
                             f"\n<b>Количество вопросов:</b> {stats_movie_questions_qty}\n🟩 <b>Правильных "
                             f"ответов:</b> {stats_movie_correct}\n🟥 <b>Неправильных ответов:</b> "
                             f"{stats_movie_incorrect}\n", parse_mode='HTML')


async def cmd_top(message: types.Message):
    if not db.is_user_exists(message.from_user.id):
        await message.reply('❌ Вы не можете использовать данную команду. Для регистрации введите /start')
    else:
        kb = [
            [types.KeyboardButton(text="🏆 Топ по уровню")],
            [types.KeyboardButton(text="🏆 Топ по количеству вопросов")],
            [types.KeyboardButton(text="🔙 Назад")]
        ]

        keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

        # Отправка сообщения с кнопками
        await message.answer("Выберите признак для составления топа:", reply_markup=keyboard)


async def cmd_top_level(message: types.Message):
    result = db.get_top_users('level')
    message_text = "<b>🏆 Топ по уровню:</b>\n"
    for i in range(len(result)):
        message_text += f"{i + 1}. {result[i][2]} - {result[i][6]} уровень\n"
    await message.answer(message_text, parse_mode='HTML')


async def cmd_top_questions_qty(message: types.Message):
    result = db.get_top_users('questions_qty')
    # Начинаем формировать сообщение
    message_text = "<b>🏆 Топ по количеству вопросов:</b>\n"

    # Добавляем каждый элемент топа в сообщение
    for i in range(len(result)):
        message_text += f"{i + 1}. {result[i][2]} - {result[i][7]} вопросов\n"

    # Отправляем сформированное сообщение
    await message.answer(message_text, parse_mode='HTML')


async def about_simple_quiz(message: types.Message):
    photo_url = 'https://i.imgur.com/8pjhcEW.png'  # Или используйте локальный путь к файлу
    caption = ('🧠 <b>Simple Quiz</b> - это викторина наподобие <b><i>"Кто хочет стать миллионером"</i></b>\n\n<b>Суть '
               'игры: </b>После начала викторины, у вас будет возможность выбрать сложность вопросов. Это важно, '
               'ведь за правильный ответ выдается опыт, а его количество зависит от выбранной вами '
               'сложности.\n\n🟢 Легкая - 1 ед. опыта\n🟡 Средняя - 2 ед. опыта\n🔴 Сложная - 4. ед опыта\n\nПосле выбора '
               'сложности вам будет'
               'задано 5 вопросов по порядку, к каждому вопросу будет предложено по 4 варианта ответа.')  # Текст
    # подписи к изображению

    await message.reply_photo(photo=photo_url, caption=caption, parse_mode='HTML')


async def about_movie_quiz(message: types.Message):
    photo_url = 'https://i.imgur.com/FX57gYZ.png'  # Или используйте локальный путь к файлу
    caption = ('🎬 <b>Movie Quiz</b> - это викторина, где вам предстоит угадать название фильма\n\n<b>Суть '
               'игры: </b>После начала викторины вы получите описание фильма из Кинопоиска. По этому описание вы '
               'должны угадать фильм и написать его название. \n\n🔔 <b>Важно: </b> Фильмы, которые будут загаданы, '
               'состоят в списке <b><i>Топ-250 фильмов Кинопоиска</i></b>.\n\n<b>Источник: '
               '</b>https://www.kinopoisk.ru/lists/movies/top250')  # Текст
    # подписи к изображению

    await message.reply_photo(photo=photo_url, caption=caption, parse_mode='HTML')


async def start_quiz(message: types.Message):
    kb = [
        [types.KeyboardButton(text="🟢 Легкий")],
        [types.KeyboardButton(text="🟡 Средний")],
        [types.KeyboardButton(text="🔴 Сложный")],
        [types.KeyboardButton(text="🔙 Назад")]
    ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

    await message.answer("Выбери уровень сложности:", reply_markup=keyboard)


def get_questions(difficulty):
    url = 'https://engine.lifeis.porn/api/millionaire.php'
    params = {'qType': difficulty_mapping[difficulty], 'count': 5}

    response = requests.get(url, params=params)
    data = response.json()

    if data['ok']:
        return data['data']
    else:
        logging.error(f"Ошибка при запросе вопросов: {data['info']}")
        return None


difficulty_mapping = {"🟢 легкий": 1, "🟡 средний": 2, "🔴 сложный": 3}

difficulty = 0

async def choose_difficulty(message: types.Message):
    global difficulty, in_quiz
    difficulty = message.text.lower()
    global questions
    questions = get_questions(difficulty)
    if questions:
        in_quiz = True
        await ask_question(message)
    else:
        await message.answer("Произошла ошибка при получении вопросов. Попробуйте еще раз.")


current_question_index = 0
user_answers = []


async def answer_question(message: types.Message):
    global current_question_index, user_answers

    if current_question_index < len(questions):
        user_answer = message.text
        # correct_answer = questions[current_question_index]['answers'][0]  # Правильный ответ всегда первый в списке

        # answer_mapping = {"a": 0, "b": 1, "c": 2, "d": 3}

        if user_answer == correct_answer:
            user_answers.append(True)
        else:
            user_answers.append(False)

        current_question_index += 1

        if current_question_index < len(questions):
            await ask_question(message)
        else:
            await show_results(message)
    else:
        logging.error("Попытка ответить на больше вопросов, чем есть в викторине.")


async def ask_question(message: types.Message):
    current_question = questions[current_question_index]
    question_text = current_question['question']
    answers = current_question['answers']
    global correct_answer
    correct_answer = answers[0]
    answers = current_question['answers'].sort()

    kb = [
        [types.KeyboardButton(text=current_question['answers'][0]),
         types.KeyboardButton(text=current_question['answers'][1])],
        [types.KeyboardButton(text=current_question['answers'][2]),
         types.KeyboardButton(text=current_question['answers'][3])]
    ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)

    await message.answer(question_text, reply_markup=keyboard)


async def show_results(message: types.Message):
    global user_answers, current_question_index, in_quiz
    correct_answers = user_answers.count(True)
    total_questions = len(questions)

    await message.answer(f"Результаты викторины:\nПравильных ответов: {correct_answers}/{total_questions}")

    # Сбросим переменные для возможности начать новую викторину
    current_question_index = 0
    user_answers = []
    current_level = int(db.get_user_info(message.from_user.id, 'level')[0])
    possible_level = current_level
    db.update_user_info(message.from_user.id, 'questions_qty', total_questions)
    db.update_user_info(message.from_user.id, 'correct_answers', correct_answers)
    db.update_user_info(message.from_user.id, 'incorrect_answers', total_questions - correct_answers)
    if correct_answers > 0:
        if difficulty_mapping[difficulty] == 1:
            possible_level = db.auto_update_user_level(message.from_user.id, correct_answers * 1)
        elif difficulty_mapping[difficulty] == 2:
            possible_level = db.auto_update_user_level(message.from_user.id, correct_answers * 2)
        else:
            possible_level = db.auto_update_user_level(message.from_user.id, correct_answers * 4)

    print(possible_level)
    if possible_level > current_level:
        await message.answer(f"🎉 Поздравляем, вы перешли на {possible_level} уровень!")
    in_quiz = False
    await main_menu(message)


def setup(dp):
    global questions
    dp.message.register(mq.get_hints_keyboard, lambda message: message.text == "💡 Подсказка")
    dp.message.register(mq.give_hints, lambda message: message.text in mq.all_hints)
    dp.message.register(mq.answers_keyboard, lambda message: message.text == "✏️ Ответить")
    dp.message.register(mq.not_know_answer, lambda message: message.text == "🤷‍♂️ Я не знаю ответа")
    dp.message.register(cmd_start, Command('start'))
    dp.message.register(cmd_help, Command('help'))
    dp.message.register(cmd_stats, Command('stats'))
    dp.message.register(start_quiz, Command('victory'))
    dp.message.register(mq.get_movies_file, lambda message: message.text == "🔍 Получить информацию")
    dp.message.register(start_quiz, lambda message: message.text == "🧠 Викторина")
    dp.message.register(choose_difficulty, lambda message: message.text.lower() in difficulty_mapping.keys())
    dp.message.register(mq.start_movie_quiz, lambda message: message.text == "🎬 Киновикторина")
    dp.message.register(cmd_stats, lambda message: message.text == "📊 Статистика")
    dp.message.register(cmd_top, lambda message: message.text == "🏆 Топ")
    dp.message.register(about_simple_quiz, lambda message: message.text == "❓ О викторине")
    dp.message.register(about_movie_quiz, lambda message: message.text == "❓ О киновикторине")
    dp.message.register(cmd_top_level, lambda message: message.text == "🏆 Топ по уровню")
    dp.message.register(cmd_top_questions_qty, lambda message: message.text == "🏆 Топ по количеству вопросов")
    dp.message.register(main_menu, lambda message: message.text == "🔙 Назад")
    dp.message.register(main_menu, lambda message: message.text == "🏠 Главное меню")
    # dp.callback_query.register(start_quiz, F.data == "victory")
    dp.message.register(answer_question, lambda message: message.text in questions[current_question_index]['answers'])
    dp.message.register(mq.movie_quiz_answer, lambda message: message.text)
