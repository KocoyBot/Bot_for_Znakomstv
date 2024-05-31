import requests
import logging
import config

logging.basicConfig(filename=config.LOGS, level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")
    
def gpt(text, system):
    """
    This function gpt(text, system) sends a POST request to the Yandex API to utilize the Yandex GPT model for text generation. 
    It constructs the necessary JSON payload, including the system message and user input, and sets parameters like temperature and maxTokens for the completion. 
    It then attempts to make the request and handle the response. If a successful response (status code 200) is returned, it extracts and returns the generated text. 
    Any errors during the process are logged, and appropriate error messages or exceptions are returned.
    """
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'

    headers = {
        'Authorization': f'Api-Key {config.API_KEY}',
        'Content-Type': 'application/json'
    }

    json = {
            "modelUri": f"gpt://{config.FOLDER_ID}/yandexgpt/latest",
            "completionOptions": {
            "stream": False,
            "temperature": 0,
            "maxTokens": "500"
        },
            "messages": [
                {"role": "system", "text": system},
                {"role": "user", "text": text}
            ]
        }

    try:
        resp = requests.post(url, headers=headers, json=json)

        if resp.status_code == 200:
            logging.info("YANDEX GPT: 200 OK")
            result = resp.json()["result"]["alternatives"][0]["message"]["text"]
            return result
        
        error_message = 'Invalid response received: code: {}, message: {}'.format(resp.status_code, resp.text)
        logging.error(f"YANDEX GPT: {error_message}")
        return error_message
    
    except Exception as e:
        logging.error(e)
        return e
