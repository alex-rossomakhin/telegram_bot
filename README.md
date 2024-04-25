# Telegram_bot
Простой бот для telegram на python для отслеживания статуса при помощи API. 
Автоматически проверяет статуc и в случае изменения, отправляет оповещение в телеграмм.
Так же умеет оповещать о сбоях в работе.
## Технологии 
* Python 3.9
* python-dotenv
* python-telegram-bot

## Запуск проекта 
Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone git@github.com:alex-rossomakhin/telegram_bot.git
```
```bash
cd telegram_bot.py
```
Cоздать и активировать виртуальное окружение:
```bash
python -m venv env
```
```bash
source env/bin/activate
```
Установить зависимости из файла requirements.txt:
```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```
Записать в переменные окружения (файл .env) необходимые ключи:

токен профиля на ресурсе
токен телеграм-бота
свой ID в телеграме
Запустить проект:

python telegram_bot.py

## Автор
[Alexey Rossomakhin](https://github.com/alex-rossomakhin)
