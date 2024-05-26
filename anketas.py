import yandex_gpt
import config
import data_base
import logging

logging.basicConfig(filename=config.LOGS, level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

def create_anketa(user_id, age, gender, picture, name, gender_search, text, chat_id, user_id_search):
  """
  The create_anketa function takes multiple parameters to create a user profile in a database. 
  It utilizes the yandex_gpt.gpt function to generate a result based on the provided inputs and system prompts. 
  If the generated result indicates a mismatch, it returns 'False' with an error message. 
  Otherwise, it adds the user data to the database using UsersDatabaseManager, logs the success, and returns 'True' with a success message. 
  In case of any exceptions during the process, it logs the error and returns 'False' with the encountered exception.
  """
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
  """
  The show_anketa function retrieves a profile for a specified user based on their age, gender, and gender preferences for potential matches. 
  It connects to a database using UsersDatabaseManager and executes a SQL query to fetch a single profile that matches the criteria. 
  The function then logs a success message, cleans up resources, and returns a tuple containing a boolean value (indicating success or failure) and the fetched profile information. 
  If an exception occurs during the process, it logs the error and returns a tuple with a boolean value of False and the encountered exception.
  """
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
  """
  This like function attempts to insert a like action between two users into a database table named "likes". 
  It takes two parameters, user_id and user_id_search, representing the IDs of the user who initiated the like and the user who received the like. 
  Inside a try block, it creates a database connection using UsersDatabaseManager from the data_base module and executes an SQL INSERT query to add a new like entry with the provided user IDs. 
  After completing the database operation, it deletes the database connection object to release system resources. 
  If any exceptions occur during the database operation, it logs the error message using the logging.error function and returns a tuple with a boolean value of False and the caught exception for error handling.
  """
    try:
        db = data_base.UsersDatabaseManager(config.DB_NAME)
        db.execute_cursor(f"INSERT INTO `likes` (`id_tg`, `id_search`) VALUES (?, ?)", (user_id, user_id_search,))
        del db
    except Exception as e:
        logging.error(e)
        return False, e
    
def themes(anketa_one, anketa_two):
  """
  This themes function takes two input strings, anketa_one and anketa_two, and concatenates them with a newline character in between. 
  It then utilizes the yandex_gpt.gpt function to generate text based on the concatenated input using a specific system prompt from the config module. 
  Finally, the generated text is returned as the result of the function.
  """
    result = yandex_gpt.gpt(anketa_one + "\n\n" + anketa_two, config.system_prompts[1])
    return result
