# HOMEWORK TELEGRAM BOT
Telegram-бот обращается к API сервиса Практикум.Домашка и узнаёт статус вашей домашней работы: взята ли ваша домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку. Написаны тесты для проверки кода, который занимается обработкой ошибок.

## Техно-стек
* python 3.7.9
* python-telegram-bot 13.7

## Запуск проекта
1. Клонировать репозиторий
```
git@github.com:avnosov3/homework_bot.git
```
2. Перейти в папку с проектом и создать виртуальное окружение
```
cd homework_bot
```
```
python3 -m venv env
python -m venv venv (Windows)
```
3. Активировать виртуальное окружение
```
source env/bin/activate
source venv/Scripts/activate (Windows)
```
4. Установить зависимости из файла requirements.txt
```
pip3 install -r requirements.txt
pip install -r requirements.txt (Windows)
```
5. [Получить](https://passport.yandex.ru/auth?retpath=https%3A%2F%2Foauth.yandex.ru%2Fauthorize%3Fresponse_type%3Dtoken%26client_id%3D1d0b9dd4d652455a9eb710d450ff456a&noreturn=1&origin=oauth) токен API сервиса Яндекс.Домашка
6. Создать и заполнить файл .env
```
PRACTICUM_TOKEN = <Указать токен>
TELEGRAM_TOKEN = <Указать токен телеграмм бота>
TELEGRAM_CHAT_ID = <Указать chat_id вашего аккаунта>
```
7. Запустить файл ```homework.py```

## Автор
[Артём Носов](https://github.com/avnosov3)
