import logging
import os
import time

from dotenv import load_dotenv
import requests
import telegram

from exceptions import (
    JSONWithError, MessageError,
    SendMessageError, StatusCodeNotOK
)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
URL = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
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
VALUE_ERROR = 'Неожиданное значение статуса: {status} '
HOMEWORK_MESSAGE = (
    'Изменился статус проверки работы "{homework_name}". {homework_status}'
)
FORMAT_ERROR = 'Ожидаем list, а получили {format}.'
REQUEST_ERROR = (
    'Сбой сети. ENPOINT: {url}. HEADERS: {headers}. PARAMS: {params}.'
    'ERROR: {error}.'
)
SERVER_ERROR = (
    'Отказ сервера. ENPOINT: {url}. HEADERS: {headers}. PARAMS: {params}.'
)
JSON_ERROR = (
    'Отказ сервера. ENPOINT: {url}. HEADERS: {headers}. PARAMS: {params}.'
    'KEY: {key}. VALUE: {value}'
)
NO_KEY = 'Нет ключа: {key}'
ERROR = 'Сбой в работе программы: {error}'
OLD_MESSAGE = 'Никаких новых сообщений не было'
MESSAGE_ERROR = 'Не удалось отправить сообщение: {message}. {error}.'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(__file__ + '.log')
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(funcName)s %(message)s'
)
handler.setFormatter(formatter)


def send_message(bot, message):
    """Функция отправляет сообщение в телеграмм."""
    try:
        return bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        raise MessageError(
            MESSAGE_ERROR.format(
                message=message,
                error=error
            )
        )


def get_api_answer(current_timestamp):
    """Преобразование ответа  API."""
    params = {'from_date': current_timestamp}
    request_params = dict(
        url=URL,
        headers=HEADERS,
        params=params
    )
    try:
        response = requests.get(**request_params)
    except requests.RequestException as error:
        raise REQUEST_ERROR(**request_params,
                            error=error)
    status = response.status_code
    if status != 200:
        raise StatusCodeNotOK(
            SERVER_ERROR.format(**request_params)
        )
    json = response.json()
    for error in ('error', 'code'):
        if error in json:
            raise JSONWithError(
                JSON_ERROR.format(
                    **request_params,
                    key=error,
                    value=json[error],
                )
            )
    return json


def check_response(response):
    """Проверка содержания ответа."""
    if not isinstance(response, dict):
        raise TypeError(FORMAT_ERROR.format(
            format=type(response)))
    if 'homeworks' not in response:
        raise KeyError(
            NO_KEY.format(key='homeworks')
        )
    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        raise TypeError(FORMAT_ERROR.format(
            format=type(homeworks)))
    return homeworks


def parse_status(homework):
    """Парсинг ответа от API."""
    name = homework['homework_name']
    status = homework['status']
    if status in HOMEWORK_VERDICTS:
        return HOMEWORK_MESSAGE.format(
            homework_name=name,
            homework_status=HOMEWORK_VERDICTS.get(status)
        )
    raise ValueError(
        VALUE_ERROR.format(status=status)
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
    current_id = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            last_homework = parse_status(homeworks[0])
            last_id = last_homework['id']
            if last_id != current_id:
                send_message(
                    bot,
                    last_homework
                )
                current_id = last_id
                current_timestamp = response.get(
                    'current_date', current_timestamp
                )
                time.sleep(RETRY_TIME)
            else:
                logger.debug(OLD_MESSAGE)
                time.sleep(RETRY_TIME)
        except Exception as error:
            main_error = ERROR.format(error=error)
            logger.error(main_error)
            try:
                send_message(
                    bot,
                    main_error
                )
            except SendMessageError as error:
                logger.error(
                    MESSAGE_ERROR.format(
                        message=main_error,
                        error=error
                    )
                )
                time.sleep(RETRY_TIME)


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
