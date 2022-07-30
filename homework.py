import requests
import os
import time
import telegram
import logging
from dotenv import load_dotenv

from exceptions import StatusCodeNotOK, JSONDecodeError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

TOKENS = (
    'PRACTICUM_TOKEN',
    'TELEGRAM_TOKEN',
    'TELEGRAM_CHAT_ID',
)

NO_TOKEN = 'Отсутствует обязательная переменная окружения {token}'
STATUS_CODE = 'Status code: {status} '
API_FAILURE = 'Сбой: Эндпоинт {endpoint}. Код ответа API: {status}'
NO_KEY = 'Нет ключа {key} '
HOMEWORK_MESSAGE = (
    'Изменился статус проверки работы "{homework_name}". {homework_status}'
)
JSON_ERROR = 'ошибка преобразования к типам данных Python '
LIST_ERROR = 'Ответ API не в виде списка'
EMPTY = 'Пустой словарь'
NO_DICT = 'Получен НЕ словарь'
GOOD = 'try выполнился'


def send_message(bot, message):
    """Функция отправляет сообщение в телеграмм."""
    return bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    """Преобразование ответа  API."""
    timestamp = current_timestamp or int(time.time())
    try:
        homeworks = requests.get(ENDPOINT, headers=HEADERS, params={
            'from_date': timestamp})
        if homeworks.status_code != 200:
            logging.error(
                API_FAILURE.format(
                    endpoint=ENDPOINT,
                    status=homeworks.status_code
                )
            )
            raise StatusCodeNotOK(
                STATUS_CODE.FORMAT(status=homeworks.status_code)
            )
        else:
            try:
                return homeworks.json()
            except JSONDecodeError:
                logging.error(JSON_ERROR)
    except StatusCodeNotOK:
        logging.error(
            API_FAILURE.format(endpoint=ENDPOINT, status=homeworks.status_code)
        )


def check_response(response):
    """Проверка содержания ответа."""
    if type(response) == dict:
        if type(response['homeworks']) is not list:
            logging.error(LIST_ERROR)
            raise KeyError
        return response['homeworks']
        # return response.get('homeworks')[0]
    else:
        logging.error(NO_KEY.format(key='homeworks'))
        raise TypeError


def parse_status(homework):
    """Парсинг ответа от API."""
    if homework:
        homework_name = homework.get('homework_name')
        if not homework_name:
            logging.error(NO_KEY.format(key='homework_name'))
            raise KeyError
        homework_status = homework.get('status')
        if homework_status in HOMEWORK_STATUSES.keys():
            return HOMEWORK_MESSAGE.format(
                homework_name=homework_name,
                homework_status=HOMEWORK_STATUSES.get(homework_status)
            )
        else:
            logging.error(NO_DICT)
            raise KeyError
    else:
        logging.error(EMPTY)


def check_tokens():
    """Проверка переменных окружения."""
    no_tokens = []
    for name in TOKENS:
        if name not in globals() or not globals()[name]:
            no_tokens.append(False)
    if no_tokens:
        logging.critical(NO_TOKEN.format(token=name))
        return False
    return True


def main():
    """Основная логика работы бота."""
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(funcName)s %(message)s',
        level=logging.DEBUG,
        filename='main.log',
        filemode='w'
    )
    if not check_tokens():
        exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = check_response(get_api_answer(current_timestamp))
            send_message(
                bot,
                parse_status(response)
            )
            time.sleep(RETRY_TIME)
        except Exception as error:
            logging.error(f'Сбой в работе программы: {error}')
            time.sleep(RETRY_TIME)
        else:
            logging.info(GOOD)


if __name__ == '__main__':
    main()
