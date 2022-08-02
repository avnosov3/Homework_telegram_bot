import requests
import os
import time
import logging

import telegram
from dotenv import load_dotenv

from exceptions import StatusCodeNotOK, JSONWithError, HomeworksWithoutKeys

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
TOKENS = (
    'PRACTICUM_TOKEN',
    'TELEGRAM_TOKEN',
    'TELEGRAM_CHAT_ID',
)
NO_TOKEN = 'Отсутствуют переменные окружения: {tokens}'
TOKEN_ERROR = 'Проблема с токенами'
NO_KEY = 'Нет ключа {key} '
HOMEWORK_MESSAGE = (
    'Изменился статус проверки работы "{homework_name}". {homework_status}'
)
LIST_ERROR = 'Ответ API не в виде списка'
REQUEST_ERROR = (
    'Сбой сети. ENPOINT: {endpoint}. HEADERS: {headers}. PARAMS: {params}.'
    'STATUS: {status}.'
)
SERVER_ERROR = (
    'Отказ сервера. ENPOINT: {endpoint}. HEADERS: {headers}. PARAMS: {params}.'
    'STATUS: {status}.'
)
ERROR = 'Сбой в работе программы: {error}'
OLD_MESSAGE = 'Никаких новых сообщений не было'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(__name__ + '.log')
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(funcName)s %(message)s'
)
handler.setFormatter(formatter)


def send_message(bot, message):
    """Функция отправляет сообщение в телеграмм."""
    return bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    """Преобразование ответа  API."""
    params = {'from_date': current_timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != 200:
            raise StatusCodeNotOK(
                SERVER_ERROR.format(
                    endpoint=ENDPOINT,
                    headers=HEADERS,
                    params=params,
                    status=response.status_code
                )
            )
        elif 'error' in response.json():
            raise JSONWithError(
                SERVER_ERROR.format(
                    endpoint=ENDPOINT,
                    headers=HEADERS,
                    params=params,
                    status=response.status_code
                )
            )
        else:
            return response.json()
    except requests.RequestException:
        raise requests.RequestException(
            REQUEST_ERROR.format(
                endpoint=ENDPOINT,
                headers=HEADERS,
                params=params,
                status='нет ответа'
            )
        )


def check_response(response):
    """Проверка содержания ответа."""
    if isinstance(response, dict):
        try:
            homeworks = response['homeworks']
            if not isinstance(homeworks, list):
                raise TypeError(LIST_ERROR)
            else:
                return homeworks
        except KeyError:
            raise KeyError(
                NO_KEY.format(key='homeworks')
            )
    raise TypeError(JSONWithError.__doc__)


def parse_status(homework):
    """Парсинг ответа от API."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        if homework_status in HOMEWORK_VERDICTS:
            return HOMEWORK_MESSAGE.format(
                homework_name=homework_name,
                homework_status=HOMEWORK_VERDICTS.get(homework_status)
            )
        else:
            raise KeyError(
                HomeworksWithoutKeys.__doc__
            )
    except HomeworksWithoutKeys:
        raise HomeworksWithoutKeys(
            HomeworksWithoutKeys.__doc__
        )


def check_tokens():
    """Проверка переменных окружения."""
    no_tokens = [
        name for name in TOKENS
        if name not in globals() or not globals()[name]
    ]
    if no_tokens:
        logger.critical(NO_TOKEN.format(tokens=no_tokens))
        return False
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise KeyError(TOKEN_ERROR)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    current_last_homework = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                last_homework = parse_status(homeworks[0])
                if last_homework != current_last_homework:
                    send_message(
                        bot,
                        last_homework
                    )
                    current_last_homework = last_homework
                    current_timestamp = response.get(
                        'current_date', current_timestamp
                    )
            else:
                logger.debug(OLD_MESSAGE)

        except Exception as error:
            logger.error(ERROR.format(error=error))
            send_message(
                bot,
                ERROR.format(error=error)
            )
            time.sleep(RETRY_TIME)
        else:
            pass


if __name__ == '__main__':
    main()
    # from unittest import TestCase, mock, main as uni_main
    # ReqEx = requests.RequestException
    # JSON = {'error': 'testing'}
    # JSON = {'homeworks': [{'homework_name': 'test', 'status': 'test'}]}
    # JSON = {'homeworks': 1}

    # class TestReq(TestCase):
    #     @mock.patch('requests.get')
    #     def test_raised(self, rq_get):
    #         rq_get.side_effect = mock.Mock(
    #             side_effect=ReqEx('testing')
    #         )
    #         main()

    #     @mock.patch('requests.get')
    #     def test_error(self, rq_get):
    #         resp = mock.Mock()
    #         resp.json = mock.Mock(
    #             return_value=JSON)
    #         rq_get.return_value = resp
    #         main()

    #     @mock.patch('requests.get')
    #     def test_status_code(self, rq_get):
    #         resp = mock.Mock()
    #         resp.status_code = mock.Mock(
    #             return_value=333
    #         )
    #         rq_get.return_value = resp
    #         main()
    # uni_main()
