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
    """
    This function create_buttons(*args) creates a custom keyboard markup with buttons based on the input arguments. 
    It uses the ReplyKeyboardMarkup class with resizing enabled to construct the markup. 
    For each argument provided, a new KeyboardButton is created and added to the markup. 
    If an exception occurs during the process, it logs the error and returns nothing.
    """
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
    """
    This function start(message) is a handler for the command "/start". 
    It first initializes a global variable users and a UsersDatabaseManager object using the config.DB_NAME. 
    It checks if the user's id is already in the 'users' table of the database. 
    If the user exists in the database, it sends a message to continue using the bot with custom buttons for different actions. 
    If the user is new, it initializes a new entry for the user in the users dictionary, asks for the user's name, and registers the next step handler how_name.
    In case of any exceptions during the process, it logs the error, sends the error message to the user with custom buttons to start again ("/start").
    """
    try:
        if bot.get_chat_member(message.from_user.id, message.from_user.id).user.username != None:
            global users
            db = data_base.UsersDatabaseManager(config.DB_NAME)
            if db.is_in_table(message.from_user.id, 'users'):
                del db
                bot.send_message(message.chat.id, "Продолжай пользоваться ботом", reply_markup=create_buttons('/my_anketa', '/show', '/show_any_anketa', '/edit_anketa', '/credits'))
                return

            users[str(message.from_user.id)] = {}
            bot.send_message(message.chat.id, "Здравствуй, давай создадим тебе анкету. Как тебя зовут?", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, how_name)
        else:
            bot.send_message(message.chat.id, "У тебя отсутствует имя пользователя телеграмм")
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e, reply_markup=create_buttons("/start"))

def how_name(message):
    """
    This how_name(message) function is a handler that processes the user's input after they have provided their name. 
    It first checks if the content type of the message is text. 
    If the content type is not text, it prompts the user to enter their name again by sending a message and registering the next step handler as how_name.
    If the content type is text, it updates the user's name in the users dictionary using the user's id as the key. 
    It then sends a message asking for the user's age and registers the next step handler as how_age to handle the user's age input.
    In case of any exceptions during the process, it logs the error, sends the error message to the user, and provides custom buttons to start the process again ("/start").
    """
    try:
        global users
        if message.content_type != 'text':
            bot.send_message(message.chat.id, "Введи своё имя")
            bot.register_next_step_handler(message, how_name, reply_markup=types.ReplyKeyboardRemove())
            return
        
        users[str(message.from_user.id)]['name'] = message.text
        bot.send_message(message.chat.id, "Хорошо, сколько тебе лет?", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, how_age)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e, reply_markup=create_buttons("/start"))

def how_age(message):
    """
    The how_age(message) function is a handler that processes the user's input after they have provided their age. 
    It first tries to execute the code within a try block. 
    If the content type of the message is not text, it prompts the user to enter their age again by sending a message and registering the next step handler as how_age.
    If the content type is text, it updates the user's age in the users dictionary using the user's id as the key. 
    It then sends a message asking for the user's gender with custom buttons for "Male" and "Female", and registers the next step handler as how_gender to handle the user's gender input.
    In case of any exceptions during the process, it logs the error, sends the error message to the user, and provides custom buttons to start the process again ("/start").
    """
    try:
        global users
        if message.content_type != 'text' or not(str(message.text).isdigit()):
            bot.send_message(message.chat.id, "Введи свой возраст", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, how_age)
            return
        
        users[str(message.from_user.id)]['age'] = message.text
        bot.send_message(message.chat.id, "Хорошо, какой твой пол?", reply_markup=create_buttons('Парень', 'Девушка'))
        bot.register_next_step_handler(message, how_gender)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e, reply_markup=create_buttons("/start"))

def how_gender(message):
    """
    The how_gender(message) function is a handler that processes the user's input after they have provided their gender. 
    It first tries to execute the code within a try block. 
    If the content type of the message is not text, it prompts the user to enter their gender again by sending a message and registering the next step handler as how_gender.
    If the user's input is not "Девушка" (Girl) or "Парень" (Boy), it sends a message informing the user that the response is not valid and registers the next step handler as how_gender to re-prompt for the gender.
    If the user's input is valid, it updates the user's gender in the users dictionary using the user's id as the key. 
    It then sends a message asking who the user is interested in with custom buttons for "Парни" (Guys), "Девушки" (Girls), and "Всё равно" (Doesn't matter), 
    and registers the next step handler as how_gender_interesting to handle the user's interest input.
    In case of any exceptions during the process, it logs the error, sends the error message to the user, and provides custom buttons to start the process again ("/start").
    """
    try:
        global users
        if message.content_type != 'text':
            bot.send_message(message.chat.id, "Введи свой пол", reply_markup=create_buttons('Парень', 'Девушка'))
            bot.register_next_step_handler(message, how_gender)
            return
        
        elif message.text != 'Девушка' and message.text != 'Парень':
            bot.send_message(message.chat.id, "Нет такого варианта ответа", reply_markup=create_buttons('Парень', 'Девушка'))
            bot.register_next_step_handler(message, how_gender)
            return
        
        users[str(message.from_user.id)]['gender'] = message.text
        bot.send_message(message.chat.id, "Хорошо, кто тебя интересует?", reply_markup=create_buttons('Парни', 'Девушки', 'Всё равно'))
        bot.register_next_step_handler(message, how_gender_interesting)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e, reply_markup=create_buttons("/start"))

def how_gender_interesting(message):
    """
    The how_gender_interesting(message) function is a handler that processes the user's input after they have provided their gender preference. 
    It first tries to execute the code within a try block. 
    If the content type of the message is not text, it prompts the user to enter the gender they are interested in by sending a message and registering the next step handler as how_gender_interesting.
    If the user's input is not "Парни" (Guys), "Девушки" (Girls), or "Всё равно" (Doesn't matter), 
    it sends a message informing the user that the response is not valid and registers the next step handler as how_gender_interesting to re-prompt for the gender preference.
    If the user's input is valid, it updates the user's gender search preference in the users dictionary using the user's id as the key. 
    It then sends a message requesting the user to send one photo for their profile and registers the next step handler as how_picture to handle the photo upload.
    In case of any exceptions during the process, it logs the error, sends the error message to the user, and provides custom buttons to start the process again ("/start").
    """
    try:
        global users
        if message.content_type != 'text':
            bot.send_message(message.chat.id, "Введи пол, который тебя интересует", reply_markup=create_buttons('Парни', 'Девушки', 'Всё равно'))
            bot.register_next_step_handler(message, how_gender_interesting)
            return
        
        if message.text != 'Парни' and message.text != 'Девушки' and message.text != 'Всё равно':
            bot.send_message(message.chat.id, "Нет такого варианта ответа", reply_markup=create_buttons('Парни', 'Девушки', 'Всё равно'))
            bot.register_next_step_handler(message, how_gender_interesting)
            return
        
        users[str(message.from_user.id)]['gender_search'] = message.text
        bot.send_message(message.chat.id, "Хорошо, пришли одно фото для анкеты")
        bot.register_next_step_handler(message, how_picture)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e, reply_markup=create_buttons("/start"))

def how_picture(message):
    """
    The how_picture(message) function is a handler that processes the user's photo upload. 
    It begins by trying to execute the code within a try block. 
    If the content type of the message is not a photo, it prompts the user to send a photo by sending a message and registering the next step handler as how_picture.
    If the message contains a photo, the function saves the photo to a designated location based on the user's id. It then updates the user's profile picture in the users dictionary. 
    A message is sent to the user asking them to write a brief description about themselves, indicating that a neural network will enhance their profile.
    The next step handler is then registered as create_text to process the user's text input.
    If an exception occurs during the process, the error is logged, and the user receives an error message along with custom buttons to restart the process ("/start").
    """
    try:
        global users
        if message.content_type != 'photo':
            bot.send_message(message.chat.id, "Пришли фото", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, how_picture)
            return

        src = config.PICTURE + str(message.from_user.id) + os.path.splitext(bot.get_file(message.photo[-1].file_id).file_path)[1]
        
        with open(src, 'wb') as new_file:
            new_file.write(bot.download_file(bot.get_file(message.photo[-1].file_id).file_path))
        
        users[str(message.from_user.id)]['picture'] = src
        bot.send_message(message.chat.id, "Хорошо, напиши немного а себе, а нейросеть подукрасит анкету", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, create_text)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e, reply_markup=create_buttons("/start"))

def create_text(message):
    """
    The create_text(message) function processes creating a user profile based on the text input provided by the user. 
    It attempts to execute the code within a try block. 
    The function calls anketas.create_anketa with various parameters including the user's ID, age, gender, picture, name, gender search preferences, user input text, chat ID, and a value of 0. 
    The user's data is then deleted from the users dictionary.
    If the creation of the profile is successful (status is True), a message saying "Profile successfully created" is sent to the chat. 
    Otherwise, the function notifies the user with the text_log message and provides buttons to restart the process using create_buttons("/start").
    The function interacts with a database (data_base.UsersDatabaseManager) to retrieve the user's profile picture and caption. 
    It then sends the profile picture to the chat along with the caption and custom buttons for further actions such as displaying, editing, or navigating the profile.
    In case of an exception, the error is logged using the logging module, and an error message is sent to the chat along with buttons to restart the process ("/start").
    """
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
            bot.send_photo(message.chat.id, ph, caption=db.get_data(message.from_user.id)[7], reply_markup=create_buttons('/my_anketa', '/show', '/show_any_anketa', '/edit_anketa', '/credits'))
        del db
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e, reply_markup=create_buttons("/start"))


@bot.message_handler(commands=['show'])
def show_anketas(message):
    """
    The show_anketas function is a message handler triggered by the /show command. 
    It retrieves user data, checks if the user has already created a profile, and prompts them to create one if not. 
    If the user has received likes from other users, it prompts them to see the list of likes and handle confirmations.
    It then calls anketas.show_anketa to fetch the user's profile data and displays it to the user. 
    If the profile data retrieval is unsuccessful, an error message is sent, and buttons for further actions are provided.
    If the user has no profile or no likes yet, appropriate messages are sent with corresponding buttons. 
    The function updates the user's search ID and displays the user's profile picture with a caption and additional action buttons. 
    In case of an exception during execution, the error is logged, and an error message is sent to the user.
    """
    try:
        if bot.get_chat_member(message.from_user.id, message.from_user.id).user.username != None:
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
                bot.send_message(message.chat.id, result, reply_markup=create_buttons('/my_anketa', '/show', '/show_any_anketa', '/edit_anketa', '/credits'))
                return
            
            if len(result) == 0:
                bot.send_message(message.chat.id, "Анкет нема", reply_markup=create_buttons('/my_anketa', '/show', '/show_any_anketa', '/edit_anketa', '/credits'))
                return

            db = data_base.UsersDatabaseManager(config.DB_NAME)
            db.execute_cursor(f"UPDATE `users` SET `user_id_search` = ? WHERE `id_tg` = ?", (result[2], message.from_user.id,))
            del db

            with open(result[0], 'rb') as ph:
                bot.send_photo(message.chat.id, ph, caption=result[1], reply_markup=create_buttons('\U0001F44D', '\U0001F44E', '\U0001F4AB'))
            bot.register_next_step_handler(message, estimation)
        else:
            bot.send_message(message.chat.id, "У тебя отсутствует имя пользователя телеграмм")
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

@bot.message_handler(commands=['show_any_anketa'])
def show_any_anketa(message):
    """This function handles the Telegram command /show_any_anketa.

    - It checks if the user has a username; if not, it sends a message indicating the absence of a username.
    - If the user is not in the database, it prompts them to create an anketa by sending a message with the /start command.
    - It checks if the user has received any likes. If likes are present, it notifies the user and prompts them to confirm whether they want to view them.
    - If no likes are present, it fetches all anketa data for the user.
    - If there are no anketa results, it informs the user that there are no entries available.
    - If an anketa is found, it updates the user's search ID and sends the corresponding photo with a caption.
    - Finally, it registers the next step handler for user interaction, such as providing an estimation or feedback.

Error handling is implemented to log any exceptions that occur during execution.
    """
    try:
        if bot.get_chat_member(message.from_user.id, message.from_user.id).user.username != None:
            db = data_base.UsersDatabaseManager(config.DB_NAME)
            if not(db.is_in_table(message.from_user.id, 'users')):
                bot.send_message(message.chat.id, "Создай анкету, пропиши /start", reply_markup=create_buttons('start'))
                del db
                return
            
            if len(db.execute_cursor(f"SELECT `id` FROM `likes` WHERE `id_search` = ?", (message.from_user.id,))) > 0:
                bot.send_message(message.chat.id, "Вас лайкнуло " + str(len(db.execute_cursor(f"SELECT `id` FROM `likes` WHERE `id_search` = ?", (message.from_user.id,)))) + " человек. Показать?", reply_markup=create_buttons('В обязательном порядке', 'Отбросить'))
                del db
                bot.register_next_step_handler(message, confirm_show_sec)
                return

            status, result = anketas.show_anketa_all_category(message.from_user.id)
            del db

            if not(status):
                bot.send_message(message.chat.id, result, reply_markup=create_buttons('/my_anketa', '/show', '/show_any_anketa', '/edit_anketa', '/credits'))
                return
            
            if len(result) == 0:
                bot.send_message(message.chat.id, "Анкет нема", reply_markup=create_buttons('/my_anketa', '/show', '/show_any_anketa', '/edit_anketa', '/credits'))
                return

            db = data_base.UsersDatabaseManager(config.DB_NAME)
            db.execute_cursor(f"UPDATE `users` SET `user_id_search` = ? WHERE `id_tg` = ?", (result[2], message.from_user.id,))
            del db

            with open(result[0], 'rb') as ph:
                bot.send_photo(message.chat.id, ph, caption=result[1], reply_markup=create_buttons('\U0001F44D', '\U0001F44E', '\U0001F4AB'))
            bot.register_next_step_handler(message, estimation_sec)
        else:
            bot.send_message(message.chat.id, "У тебя отсутствует имя пользователя телеграмм")
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

def confirm_show(message):
    """
    The confirm_show function is a message handler that processes user input to confirm or reject an action related to liking profiles. 
  - If the user confirms by selecting "В обязательном порядке" (meaning "In priority"), the function retrieves and displays the profile picture and caption of the liked profile. It also creates buttons for further actions, such as confirmation or rejection of the like. The user is prompted to provide an estimation after confirming.
  - If the user chooses to reject the like by selecting "Отбросить" (meaning "Discard"), the like entry is deleted from the database. The function then proceeds to show other profiles for the user to review.
  - In case of an invalid command input, an error message is sent to the user, and they are prompted to retry the action.
  - Any exceptions raised during the execution of the function are logged, and an error message is sent to the user.
    """
    try:
        if bot.get_chat_member(message.from_user.id, message.from_user.id).user.username != None:
            db = data_base.UsersDatabaseManager(config.DB_NAME)
            if message.text == 'В обязательном порядке':
                with open(db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])[4], 'rb') as ph:
                    bot.send_photo(message.chat.id, ph, caption=db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])[7], reply_markup=create_buttons('\U0001F44D', '\U0001F44E'))
                    

                bot.register_next_step_handler(message, answ_estimation)

            elif message.text == 'Отбросить':
                db.execute_cursor(f"DELETE FROM `likes` WHERE `id_search` = ?", (message.from_user.id,))
                del db

                show_anketas(message)

            else:
                bot.send_message(message.chat.id, "Неверная команда")
                bot.register_next_step_handler(message, confirm_show)
        else:
            bot.send_message(message.chat.id, "У тебя отсутствует имя пользователя телеграмм")

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

def confirm_show_sec(message):
    """
    The confirm_show function is a message handler that processes user input to confirm or reject an action related to liking profiles. 
  - If the user confirms by selecting "В обязательном порядке" (meaning "In priority"), the function retrieves and displays the profile picture and caption of the liked profil>
  - If the user chooses to reject the like by selecting "Отбросить" (meaning "Discard"), the like entry is deleted from the database. The function then proceeds to show other >
  - In case of an invalid command input, an error message is sent to the user, and they are prompted to retry the action.
  - Any exceptions raised during the execution of the function are logged, and an error message is sent to the user.
    """
    try:
        if bot.get_chat_member(message.from_user.id, message.from_user.id).user.username != None:
            db = data_base.UsersDatabaseManager(config.DB_NAME)
            if message.text == 'В обязательном порядке':
                with open(db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])[4], 'rb') as ph:
                    bot.send_photo(message.chat.id, ph, caption=db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])[7], reply_markup=create_buttons('\U0001F44D', '\U0001F44E'))
                    

                bot.register_next_step_handler(message, answ_estimation_sec)

            elif message.text == 'Отбросить':
                db.execute_cursor(f"DELETE FROM `likes` WHERE `id_search` = ?", (message.from_user.id,))
                del db

                show_any_anketa(message)

            else:
                bot.send_message(message.chat.id, "Неверная команда")
                bot.register_next_step_handler(message, confirm_show_sec)
        else:
            bot.send_message(message.chat.id, "У тебя отсутствует имя пользователя телеграмм")

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

def answ_estimation(message):
    """
    The answ_estimation function is an event handler that processes user input related to confirming or rejecting a like action on profiles. Here's an overview of its functionality:
  - The function attempts to interact with the database using UsersDatabaseManager from data_base module and the specified database name from the config module.
  - If the user input is a thumbs-up emoji \U0001F44D, the function performs a series of actions:
      - It sends messages containing the profile link, specific themes, and mutual interest information with the liked user.
      - It sends the profile photo with a caption and the link to the user.
      - It deletes the like entry related to the user.
      - The database connection is then closed.
  - If the user input is a thumbs-down emoji \U0001F44E, the function simply deletes the like entry without further actions.
  - If an invalid command is provided, an error message is sent to the user, and the function registers the next step handler for further interaction.
  - Finally, the function calls show_anketas(message) which presumably displays additional profiles for the user to review.
  - Any exceptions that occur during the execution are logged, and an error message is sent to the user indicating the issue.
    """
    try:
        if bot.get_chat_member(message.from_user.id, message.from_user.id).user.username != None:
            db = data_base.UsersDatabaseManager(config.DB_NAME)
            if message.text == '\U0001F44D':
                themes = anketas.themes(db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])[7], db.get_data(message.from_user.id)[7])

                bot.send_message(message.chat.id, "Ссылка на этого пользователя: t.me/" + bot.get_chat_member(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0], db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0]).user.username)

                bot.send_message(message.chat.id, themes, reply_markup=create_buttons('/my_anketa', '/show', '/show_any_anketa', '/edit_anketa', '/credits'))

                with open(db.get_data(message.from_user.id)[4], 'rb') as ph:
                    bot.send_photo(db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])[8], ph, caption=db.get_data(message.from_user.id)[7] + "\n\nВзаимная симпатия с этим пользователем. Ссылка на него: t.me/" + bot.get_chat_member(message.from_user.id, message.from_user.id).user.username, reply_markup=create_buttons('\U0001F44D', '\U0001F44E', '\U0001F4AB'))

                bot.send_message(db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])[8], themes)

                db.execute_cursor(f"DELETE FROM `likes` WHERE `id_search` = ? AND `id_tg` = ?", (message.from_user.id, str(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])))
                del db
                
            elif message.text == '\U0001F44E':
                db.execute_cursor(f"DELETE FROM `likes` WHERE `id_search` = ? AND `id_tg` = ?", (message.from_user.id, str(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])))
                del db

            else:
                del db
                bot.send_message(message.chat.id, "Неверная команда")
                bot.register_next_step_handler(message, answ_estimation)
                return
        else:
            bot.send_message(message.chat.id, "У тебя отсутствует имя пользователя телеграмм")

        show_anketas(message)
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

def answ_estimation_sec(message):
    """
    The answ_estimation function is an event handler that processes user input related to confirming or rejecting a like action on profiles. Here's an overview of its function>
  - The function attempts to interact with the database using UsersDatabaseManager from data_base module and the specified database name from the config module.
  - If the user input is a thumbs-up emoji \U0001F44D, the function performs a series of actions:
      - It sends messages containing the profile link, specific themes, and mutual interest information with the liked user.
      - It sends the profile photo with a caption and the link to the user.
      - It deletes the like entry related to the user.
      - The database connection is then closed.
  - If the user input is a thumbs-down emoji \U0001F44E, the function simply deletes the like entry without further actions.
  - If an invalid command is provided, an error message is sent to the user, and the function registers the next step handler for further interaction.
  - Finally, the function calls show_anketas(message) which presumably displays additional profiles for the user to review.
  - Any exceptions that occur during the execution are logged, and an error message is sent to the user indicating the issue.
    """
    try:
        if bot.get_chat_member(message.from_user.id, message.from_user.id).user.username != None:
            db = data_base.UsersDatabaseManager(config.DB_NAME)
            if message.text == '\U0001F44D':
                themes = anketas.themes(db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])[7], db.get_data(message.from_user.id)[7])

                bot.send_message(message.chat.id, "Ссылка на этого пользователя: t.me/" + bot.get_chat_member(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0], db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0]).user.username)

                bot.send_message(message.chat.id, themes, reply_markup=create_buttons('/my_anketa', '/show', '/show_any_anketa', '/edit_anketa', '/credits'))

                with open(db.get_data(message.from_user.id)[4], 'rb') as ph:
                    bot.send_photo(db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])[8], ph, caption=db.get_data(message.from_user.id)[7] + "\n\nВзаимная симпатия с этим пользователем. Ссылка на него: t.me/" + bot.get_chat_member(message.from_user.id, message.from_user.id).user.username, reply_markup=create_buttons('\U0001F44D', '\U0001F44E', '\U0001F4AB'))

                bot.send_message(db.get_data(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])[8], themes)

                db.execute_cursor(f"DELETE FROM `likes` WHERE `id_search` = ? AND `id_tg` = ?", (message.from_user.id, str(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])))
                del db
            elif message.text == '\U0001F44E':
                db.execute_cursor(f"DELETE FROM `likes` WHERE `id_search` = ? AND `id_tg` = ?", (message.from_user.id, str(db.execute_cursor(f"SELECT `id_tg` FROM `likes` WHERE `id_search` = ? LIMIT 1", (message.from_user.id,))[0])))
                del db
            else:
                del db
                bot.send_message(message.chat.id, "Неверная команда")
                bot.register_next_step_handler(message, answ_estimation_sec)
                return
        else:
            bot.send_message(message.chat.id, "У тебя отсутствует имя пользователя телеграмм")

        show_any_anketa(message)
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

def estimation(message):
    """
    The estimation function processes user input related to liking or rejecting profiles in a chatbot application. Here's a summary of its functionality:
  - The function first attempts to handle different scenarios based on the user input:
      - If the user sends a thumbs-up emoji (\U0001F44D), it interacts with the database to perform a like action on the profile associated with the user ID. It then shows additional profiles for the user to review.
      - If the user sends a thumbs-down emoji (\U0001F44E), it simply shows the next profile for review.
      - If the user sends a different command (like a "stop" emoji), it sends a message indicating that the mode has been exited.
      - For any other input, it sends a message indicating an incorrect command and registers the estimation function for further input processing.
  - If an exception occurs during the execution of the function, it logs the error and sends a message to the user indicating the issue.
  Overall, the estimation function effectively manages user input related to profile liking and navigation within the chatbot application.
    """
    try:
        if bot.get_chat_member(message.from_user.id, message.from_user.id).user.username != None:
            if message.text == '\U0001F44D':
                db = data_base.UsersDatabaseManager(config.DB_NAME)
                anketas.like(message.from_user.id, db.get_data(message.from_user.id)[9])
                del db

                show_anketas(message)
                
            elif message.text == '\U0001F44E':
                show_anketas(message)

            elif message.text == '\U0001F4AB':
                bot.send_message(message.chat.id, "Вышел из режима поиска людей", reply_markup=create_buttons('/my_anketa', '/show', '/show_any_anketa', '/edit_anketa', '/credits'))
            
            else:
                bot.send_message(message.chat.id, "Неверная команда")
                bot.register_next_step_handler(message, estimation)
        else:
            bot.send_message(message.chat.id, "У тебя отсутствует имя пользователя телеграмм")

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

def estimation_sec(message):
    """
    The estimation function processes user input related to liking or rejecting profiles in a chatbot application. Here's a summary of its functionality:
  - The function first attempts to handle different scenarios based on the user input:
      - If the user sends a thumbs-up emoji (\U0001F44D), it interacts with the database to perform a like action on the profile associated with the user ID. It then shows add>      - If the user sends a thumbs-down emoji (\U0001F44E), it simply shows the next profile for review.
      - If the user sends a different command (like a "stop" emoji), it sends a message indicating that the mode has been exited.
      - For any other input, it sends a message indicating an incorrect command and registers the estimation function for further input processing.
  - If an exception occurs during the execution of the function, it logs the error and sends a message to the user indicating the issue.
  Overall, the estimation function effectively manages user input related to profile liking and navigation within the chatbot application.
    """
    try:
        if bot.get_chat_member(message.from_user.id, message.from_user.id).user.username != None:
            if message.text == '\U0001F44D':
                db = data_base.UsersDatabaseManager(config.DB_NAME)
                anketas.like(message.from_user.id, db.get_data(message.from_user.id)[9])
                del db

                show_any_anketa(message)

            elif message.text == '\U0001F44E':
                show_any_anketa(message)

            elif message.text == '\U0001F4AB':
                bot.send_message(message.chat.id, "Вышел из режима поиска людей", reply_markup=create_buttons('/my_anketa', '/show', '/show_any_anketa', '/edit_anketa', '/credits'))
            else:
                bot.send_message(message.chat.id, "Неверная команда")
                bot.register_next_step_handler(message, estimation_sec)
        else:
            bot.send_message(message.chat.id, "У тебя отсутствует имя пользователя телеграмм")

    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

@bot.message_handler(commands=['my_anketa'])
def show_anketa(message):
    """
    The show_anketa function is a message handler that responds to the /my_anketa command. Here's a summary of its functionality:
  - The function first attempts to create an instance of the UsersDatabaseManager class and checks if the user's ID is in the 'users' table. If the user is not in the table, it sends a message prompting the user to create a profile by typing /start.
  - If the user is in the database, the function opens the user's photo file (indexed at position 4 in the user's data) and sends it as a photo message along with a caption (retrieved from position 7 in the user's data) to the chat. Additional buttons for actions like viewing the profile, editing the profile, or accessing credits are also included in the message.
  - In case of any exceptions during the execution of the function, it logs the error and sends a message with the error description to the chat.
  Overall, the show_anketa function handles the display of user profiles based on the /my_anketa command, interacting with the database and sending relevant information to the user in a structured format.
    """
    try:
        if bot.get_chat_member(message.from_user.id, message.from_user.id).user.username != None:
            db = data_base.UsersDatabaseManager(config.DB_NAME)
            if not(db.is_in_table(message.from_user.id, 'users')):
                bot.send_message(message.chat.id, "Создай анкету, пропиши /start", reply_markup=create_buttons('start'))
                del db
                return
            
            with open(db.get_data(message.from_user.id)[4], 'rb') as ph:
                bot.send_photo(message.chat.id, ph, caption=db.get_data(message.from_user.id)[7], reply_markup=create_buttons('/my_anketa', '/show', '/show_any_anketa', '/edit_anketa', '/credits'))
            del db
        else:
            bot.send_message(message.chat.id, "У тебя отсутствует имя пользователя телеграмм")
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

@bot.message_handler(commands=['edit_anketa'])
def edit(message):
    """
    The edit function is a message handler triggered by the /edit_anketa command. Here's a brief description of its functionality:
  - The function starts by creating an instance of the UsersDatabaseManager class and checks if the user's ID is in the 'users' table. If the user is found in the database, their data is deleted from the database.
  - The function then clears the user's data in the users dictionary linked to their user ID.
  - Subsequently, a message "Как тебя зовут?" (translated as "What is your name?") is sent to the user's chat to prompt them for input.
  - Finally, the function registers the next step handler how_name to handle the user's response to the name inquiry. If any exceptions occur during execution, the function logs the error and sends an error message to the chat.
  Overall, the edit function handles the editing of user profiles by deleting existing data and prompting the user to provide a new name, initiating a conversation flow to update the user information when the /edit_anketa command is invoked.
    """
    try:
        if bot.get_chat_member(message.from_user.id, message.from_user.id).user.username != None:
            db = data_base.UsersDatabaseManager(config.DB_NAME)
            if db.is_in_table(message.from_user.id, 'users'):
                db.delete_data(message.from_user.id)
            del db
            users[str(message.from_user.id)] = {}
            bot.send_message(message.chat.id, "Как тебя зовут?")
            bot.register_next_step_handler(message, how_name)
        else:
            bot.send_message(message.chat.id, "У тебя отсутствует имя пользователя телеграмм")
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

@bot.message_handler(commands=['credits'])
def credits(message):
    """
    This function is a message handler triggered by the /credits command.
    It sends a message containing credits and acknowledgments about the bot creation and its contributors.
    The message includes information about the bot's origins, participation in a Yandex Python AI course hackathon, and the names of the team members involved in the bot's development.
    It also lists the team tracker who contributed to the bot creation.
    The function includes a reply markup with buttons for /my_anketa, /show, /edit_anketa, and /credits commands.
    If an exception occurs during message sending, the function logs the error and sends the error message to the chat.
    """
    try:
        if bot.get_chat_member(message.from_user.id, message.from_user.id).user.username != None:
            bot.send_message(message.chat.id, "2024 © Бот знакомств Da_Tot\n\nБот был сделан для хакатона на курсе Python ИИ от Яндекса\nпрограммы «Код будущего».\n\nУчастие в создании бота принимали:\n\n  — Егор Бекренев (KocoyBot)\n\n  — Алексей Смирнов (kzttynxvxrdzxs)\n\n — Матвей Дорошкевич (fatpigmat)\n\nТрекер команды:\n\n  — Илья Заворотный (vompie)", reply_markup=create_buttons('/my_anketa', '/show', '/show_any_anketa', '/edit_anketa', '/credits'))
        else:
            bot.send_message(message.chat.id, "У тебя отсутствует имя пользователя телеграмм")
    except Exception as e:
        logging.error(e)
        bot.send_message(message.chat.id, e)

bot.infinity_polling()
