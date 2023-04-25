# HOMEWORK TELEGRAM BOT
Telegram-бота обращается к API сервиса Практикум.Домашка и узнаваёт статус вашей домашней работы: взята ли ваша домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку. Написаны тесты для проверки кода, который занимается обработкой ошибок.

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
5. Из папки yatube провести миграции
```
python3 manage.py migrate
python manage.py migrate (Windows)
```
6. Запустить файл ```homework.py```

## Автор
[Артём Носов](https://github.com/avnosov3)
