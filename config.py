TELEBOT_TOKEN = '' # Token for connecting to a Telegram bot
API_KEY = ''  # API key is needed to use the Yandex Cloud API
FOLDER_ID = ''  # The directory ID is also required to use the Yandex Cloud API
PATH = '/home/имя_пользователя/Bot_for_Znakomstv/'  # The path from the root directory of Linux to the project folder
LOGS = f'{PATH}logs.txt'  # logs file
DB_NAME = f'{PATH}database.db'  # database file
PICTURE = f'{PATH}pictures/'  # folder with pictures


"""System prompts for the GPT operation 1) - For generation; 2) - For proposing topics"""

system_prompts = ['Ты - профессиональный анкетёр, ты работаешь в крупной компании по написанию анкет для людей, которые хотят знакомиться, напиши анкету по информации от пользователя. '
                  'Пиши анкету от имени пользователя, также пиши текстом, пиши только о пользователе, своего ничего не придумывай, не задавай никаких вопросов.'
                  'Текст прошу не форматируй.', 'Тебе предстоит задача читать две анкеты от двух людей и предложить исходя из этих анкет тему начала общения между ними.'
                  'Ты можешь предлагать несколько тем на выбор исходя из общих интересов.' 
                  'Тебе нужно предложить пять тем для начала общения. Говори от своего имени. Не путайся в интересах. Текст прошу не форматируй']
