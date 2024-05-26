import telebot
from telebot import types
import logging
import data_base
import config
import anketas
import os

logging.basicConfig(filename=config.LOGS, level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

users = {}

bot = telebot.TeleBot(config.TELEBOT_TOKEN)

def create_buttons(*args):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in args:
            markup.add(types.KeyboardButton(i))
        return markup
    except Exception as e:
        logging.error(e)
        return

@bot.message_handler(commands=['start'])
def start(message):
    try:
        global users
        db = data_base.UsersDatabaseManager(config.DB_NAME)
        if db.is_in_table(message.from_user.id, 'users'):
            del db
            bot.send_message(message.chat.id, "Продолжай пользоваться ботом", reply_markup=create_buttons('/my_anketa', '/show', '/edit_anketa', '/credits'))
            return

        users[str(message.from_user.id)] = {}
        bot.send_message(message.chat.id, "Здравствуй, давай создадим тебе анкету. Как тебя зовут?")
        bot.register_next_step_handler(message, how_name)
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e, reply_markup=create_buttons("/start"))

def how_name(message):
    try:
        global users
        if message.content_type != 'text':
            bot.send_message(message.chat.id, "Введи своё имя")
            bot.register_next_step_handler(message, how_name)
            return
        
        users[str(message.from_user.id)]['name'] = message.text
        bot.send_message(message.chat.id, "Хорошо, сколько тебе лет?")
        bot.register_next_step_handler(message, how_age)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e, reply_markup=create_buttons("/start"))

def how_age(message):
    try:
        global users
        if message.content_type != 'text':
            bot.send_message(message.chat.id, "Введи свой возраст")
            bot.register_next_step_handler(message, how_age)
            return
        
        users[str(message.from_user.id)]['age'] = message.text
        bot.send_message(message.chat.id, "Хорошо, какой твой пол?", reply_markup=create_buttons('Парень', 'Девушка'))
        bot.register_next_step_handler(message, how_gender)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e, reply_markup=create_buttons("/start"))

def how_gender(message):
    try:
        global users
        if message.content_type != 'text':
            bot.send_message(message.chat.id, "Введи свой пол")
            bot.register_next_step_handler(message, how_gender)
            return
        
        elif message.text != 'Девушка' and message.text != 'Парень':
            bot.send_message(message.chat.id, "Нет такого варианта ответа")
            bot.register_next_step_handler(message, how_gender)
            return
        
        users[str(message.from_user.id)]['gender'] = message.text
        bot.send_message(message.chat.id, "Хорошо, кто тебя интересует?", reply_markup=create_buttons('Парни', 'Девушки', 'Всё равно'))
        bot.register_next_step_handler(message, how_gender_interesting)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e, reply_markup=create_buttons("/start"))

def how_gender_interesting(message):
    try:
        global users
        if message.content_type != 'text':
            bot.send_message(message.chat.id, "Введи пол, который тебя интересует")
            bot.register_next_step_handler(message, how_gender_interesting)
            return
        
        if message.text != 'Парни' and message.text != 'Девушки' and message.text != 'Всё равно':
            bot.send_message(message.chat.id, "Нет такого варианта ответа")
            bot.register_next_step_handler(message, how_gender_interesting)
            return
        
        users[str(message.from_user.id)]['gender_search'] = message.text
        bot.send_message(message.chat.id, "Хорошо, пришли одно фото для анкеты")
        bot.register_next_step_handler(message, how_picture)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e, reply_markup=create_buttons("/start"))

def how_picture(message):
    try:
        global users
        if message.content_type != 'photo':
            bot.send_message(message.chat.id, "Пришли фото")
            bot.register_next_step_handler(message, how_picture)
            return
        
        src = config.PICTURE + str(message.from_user.id) + os.path.splitext(bot.get_file(message.photo[-1].file_id).file_path)[1]
        
        with open(src, 'wb') as new_file:
            new_file.write(bot.download_file(bot.get_file(message.photo[-1].file_id).file_path))
        
        users[str(message.from_user.id)]['picture'] = src
        bot.send_message(message.chat.id, "Хорошо, напиши немного а себе, а нейросеть подукрасит анкету")
        bot.register_next_step_handler(message, create_text)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e, reply_markup=create_buttons("/start"))

def create_text(message):
    try:
        status, text_log = anketas.create_anketa(message.from_user.id, users[str(message.from_user.id)]['age'], users[str(message.from_user.id)]['gender'], users[str(message.from_user.id)]['picture'], users[str(message.from_user.id)]['name'], users[str(message.from_user.id)]['gender_search'], message.text, message.chat.id, 0)
        del users[str(message.from_user.id)]

        if status:
            bot.send_message(message.chat.id, "Анкета успешна создана")
        else:
            bot.send_message(message.chat.id, text_log, reply_markup=create_buttons("/start"))
            return
        db = data_base.UsersDatabaseManager(config.DB_NAME)
        with open(db.get_data(message.from_user.id)[4], 'rb') as ph:
            bot.send_photo(message.chat.id, ph, caption=db.get_data(message.from_user.id)[7], reply_markup=create_buttons('/my_anketa', '/show', '/edit_anketa', '/credits'))
        del db
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e, reply_markup=create_buttons("/start"))


@bot.message_handler(commands=['show'])
def show_anketas(message):
    try:
        db = data_base.UsersDatabaseManager(config.DB_NAME)
        if not(db.is_in_table(message.from_user.id, 'users')):
            bot.send_message(message.chat.id, "Создай анкету, пропиши /start", reply_markup=create_buttons('start'))
            del db
            return
        
        if len(db.execute_cursor(f"SELECT `id` FROM `likes` WHERE `id_search` = ?", (message.from_user.id,))) > 0:
            bot.send_message(message.chat.id, "Вас лайкнуло " + str(len(db.execute_cursor(f"SELECT `id` FROM `likes` WHERE `id_search` = ?", (message.from_user.id,)))) + " человек. Показать?", reply_markup=create_buttons('В обязательном порядке', 'Отбросить'))
            del db
            bot.register_next_step_handler(message, confirm_show)
            return

        status, result = anketas.show_anketa(message.from_user.id, db.get_data(message.from_user.id)[2], db.get_data(message.from_user.id)[3], db.get_data(message.from_user.id)[6])
        del db

        if not(status):
            bot.send_message(message.chat.id, result, reply_markup=create_buttons('/my_anketa', '/show', '/edit_anketa', '/credits'))
            return
        
        if len(result) == 0:
            bot.send_message(message.chat.id, "Анкет нема", reply_markup=create_buttons('/my_anketa', '/show', '/edit_anketa', '/credits'))
            return

        db = data_base.UsersDatabaseManager(config.DB_NAME)
        db.execute_cursor(f"UPDATE `users` SET `user_id_search` = ? WHERE `id_tg` = ?", (result[2], message.from_user.id,))
        del db

        with open(result[0], 'rb') as ph:
            bot.send_photo(message.chat.id, ph, caption=result[1], reply_markup=create_buttons('\U0001F44D', '\U0001F44E', '\U0001F4AB'))
        bot.register_next_step_handler(message, estimation)
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

def confirm_show(message):
    try:
        db = data_base.UsersDatabaseManager(config.DB_NAME)
        if message.text == 'В обязательном порядке':
            with open(db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])[4], 'rb') as ph:
                bot.send_photo(message.chat.id, ph, caption=db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])[7], reply_markup=create_buttons('\U0001F44D', '\U0001F44E'))
                bot

            bot.register_next_step_handler(message, answ_estimation)

        elif message.text == 'Отбросить':
            db.execute_cursor(f"DELETE FROM `likes` WHERE `id_search` = ?", (message.from_user.id,))
            del db

            show_anketas(message)

        else:
            bot.send_message(message.chat.id, "Неверная команда")
            bot.register_next_step_handler(message, answ_estimation)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

def answ_estimation(message):
    try:
        db = data_base.UsersDatabaseManager(config.DB_NAME)
        if message.text == '\U0001F44D':
            bot.send_message(message.chat.id, "Ссылка на этого пользователя: t.me/" + bot.get_chat_member(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0], db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0]).user.username)

            bot.send_message(message.chat.id, anketas.themes(db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])[7], db.get_data(message.from_user.id)[7]))

            with open(db.get_data(message.from_user.id)[4], 'rb') as ph:
                bot.send_photo(db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])[8], ph, caption=db.get_data(message.from_user.id)[7] + "\n\nВзаимная симпатия с этим пользователем. Ссылка на него: t.me/" + bot.get_chat_member(message.from_user.id, message.from_user.id).user.username)

            bot.send_message(db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])[8], anketas.themes(db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = '{message.from_user.id}' LIMIT 1")[0])[7], db.get_data(message.from_user.id)[7]))

            db.execute_cursor(f"DELETE FROM `likes` WHERE `id_search` = ? AND `id_tg` = ?", (message.from_user.id, str(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id))[0])))
            del db
            
        elif message.text == '\U0001F44E':
            db.execute_cursor(f"DELETE FROM `likes` WHERE `id_search` = ? AND `id_tg` = ?", (message.from_user.id, str(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id))[0])))
            del db

        else:
            del db
            bot.send_message(message.chat.id, "Неверная команда")
            bot.register_next_step_handler(message, answ_estimation)
            return

        show_anketas(message)
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

def estimation(message):
    try:
        if message.text == '\U0001F44D':
            db = data_base.UsersDatabaseManager(config.DB_NAME)
            anketas.like(message.from_user.id, db.get_data(message.from_user.id)[9])
            del db

            show_anketas(message)
            
        elif message.text == '\U0001F44E':
            show_anketas(message)

        elif message.text == '\U0001F4AB':
            bot.send_message(message.chat.id, "Вышел из режима поиска людей", reply_markup=create_buttons("/my_anketa", '/show', '/edit_anketa', '/credits'))
        
        else:
            bot.send_message(message.chat.id, "Неверная команда")
            bot.register_next_step_handler(message, estimation)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

@bot.message_handler(commands=['my_anketa'])
def show_anketa(message):
    try:
        db = data_base.UsersDatabaseManager(config.DB_NAME)
        if not(db.is_in_table(message.from_user.id, 'users')):
            bot.send_message(message.chat.id, "Создай анкету, пропиши /start", reply_markup=create_buttons('start'))
            del db
            return
        
        with open(db.get_data(message.from_user.id)[4], 'rb') as ph:
            bot.send_photo(message.chat.id, ph, caption=db.get_data(message.from_user.id)[7], reply_markup=create_buttons("/my_anketa", '/show', '/edit_anketa', '/credits'))
        del db
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

@bot.message_handler(commands=['edit_anketa'])
def edit(message):
    try:
        db = data_base.UsersDatabaseManager(config.DB_NAME)
        if db.is_in_table(message.from_user.id, 'users'):
            db.delete_data(message.from_user.id)
        del db
        users[str(message.from_user.id)] = {}
        bot.send_message(message.chat.id, "Как тебя зовут?")
        bot.register_next_step_handler(message, how_name)
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

@bot.message_handler(commands=['credits'])
def credits(message):
    try:
        bot.send_message(message.chat.id, "2024 © Бот знакомств Da_Tot\n\nБот был сделан для хакатона на курсе Python ИИ от Яндекса\nпрограммы «Код будущего».\n\nУчастие в создании бота принимали:\n\n  — Егор Бекренев (KocoyBot)\n\n  — Алексей Смирнов (kzttynxvxrdzxs)\n\n — Матвей Дорошкевич (fatpigmat)\n\nТрекер команды:\n\n  — Илья Заворотный (vompie)", reply_markup=create_buttons("/my_anketa", '/show', '/edit_anketa', '/credits'))
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

bot.infinity_polling()
