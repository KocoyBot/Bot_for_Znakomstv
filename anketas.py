import yandex_gpt
import config
import data_base
import logging

logging.basicConfig(filename=config.LOGS, level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

def create_anketa(user_id, age, gender, picture, name, gender_search, text, chat_id, user_id_search):
    try:
        result = yandex_gpt.gpt(f'{name}, {age}. {text}', config.system_prompts[0])
        if result == 'К сожалению, я не могу ничего сказать об этом. Давайте сменим тему?':
            return False, 'Анкета не соответствует норме'
        db = data_base.UsersDatabaseManager(config.DB_NAME)
        db.add_data(user_id, age, gender, picture, name, gender_search, result, chat_id, user_id_search)
        del db
        logging.info("Успех")
        return True, "Успех"
    except Exception as e:
        logging.error(e)
        return False, e
    
def show_anketa(user_id, age, gender, gender_search):
    try:
        db = data_base.UsersDatabaseManager(config.DB_NAME)
        if gender == 'Парень':
            if gender_search == 'Парни':
                result = db.execute_cursor(f"SELECT `picture`, `text`, `id_tg` FROM `users` WHERE (`age` = ? OR `age` = ? OR `age` = ?) AND `gender` = 'Парень' AND `gender_search` = 'Парни' AND `id_tg` <> ? ORDER BY RANDOMOM() LIMIT 1", (age, age+1, age-1, user_id,))
            elif gender_search == 'Девушки':
                result = db.execute_cursor(f"SELECT `picture`, `text`, `id_tg` FROM `users` WHERE (`age` = ? OR `age` = ? OR `age` = ?) AND `gender` = 'Девушка' AND `gender_search` = 'Парни' AND `id_tg` <> ? ORDER BY RANDOM() LIMIT 1", (age, age+1, age-1, user_id,))
            elif gender_search == 'Всё равно':
                result = db.execute_cursor(f"SELECT `picture`, `text`, `id_tg` FROM `users` WHERE (`age` = ? OR `age` = ? OR `age` = ?) AND `gender_search` = 'Всё равно' AND `id_tg` <> ? ORDER BY RANDOM() LIMIT 1", (age, age+1, age-1, user_id,))
        elif gender == 'Девушка':
            if gender_search == 'Парни':
                result = db.execute_cursor(f"SELECT `picture`, `text`, `id_tg` FROM `users` WHERE (`age` = ? OR `age` = '? OR `age` = ?) AND `gender` = 'Парень' AND `gender_search` = 'Девушки' AND `id_tg` <> ? ORDER BY RANDOM() LIMIT 1", (age, age+1, age-1, user_id,))
            elif gender_search == 'Девушки':
                result = db.execute_cursor(f"SELECT `picture`, `text`, `id_tg` FROM `users` WHERE (`age` = ? OR `age` = ? OR `age` = ?) AND `gender` = 'Девушка' AND `gender_search` = 'Девушки' AND `id_tg` <> ? ORDER BY RANDOM() LIMIT 1", (age, age+1, age-1, user_id,))
            elif gender_search == 'Всё равно':
                result = db.execute_cursor(f"SELECT `picture`, `text`, `id_tg` FROM `users` WHERE (`age` = ? OR `age` = ? OR `age` = ?) AND `gender_search` = 'Всё равно' AND `id_tg` <> ? ORDER BY RANDOM() LIMIT 1", (age, age+1, age-1, user_id,))
        logging.info("Успех")
        del db
        return True, result
    except Exception as e:
        logging.error(e)
        return False, e
    
def like(user_id, user_id_search):
    try:
        db = data_base.UsersDatabaseManager(config.DB_NAME)
        db.execute_cursor(f"INSERT INTO `likes` (`id_tg`, `id_search`) VALUES (?, ?)", (user_id, user_id_search,))
        del db
    except Exception as e:
        logging.error(e)
        return False, e
    
def themes(anketa_one, anketa_two):
    result = yandex_gpt.gpt(anketa_one + "\n\n" + anketa_two, config.system_prompts[1])
    return result