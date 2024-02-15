import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import APIAnswerError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
payload = {'from_date': 1677628800}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверка токенов."""
    global_dict = globals()
    global_dict = {'PRACTICUM_TOKEN': global_dict['PRACTICUM_TOKEN'],
                   'TELEGRAM_TOKEN': global_dict['TELEGRAM_TOKEN'],
                   'TELEGRAM_CHAT_ID': global_dict['TELEGRAM_CHAT_ID']
                   }
    global_dict_none = [name
                        for name, token in global_dict.items()
                        if token is None]
    if global_dict_none:
        logging.critical(f'Отсутствует токен {", ".join(global_dict_none)}')
        raise FileNotFoundError(f'Отсутствуетt токен'
                                f'{", ".join(global_dict_none)}')
    return True


def send_message(bot, message):
    """Проверка отправки сообщения в телеграм."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

    except telegram.TelegramError:
        logging.error('Сбой при отправке сообщения в Telegram', exc_info=True)
    else:
        logging.debug('Сообщение отправлено')


def get_api_answer(timestamp):
    """Проверка получения ответа от API."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        if response.status_code == HTTPStatus.OK:
            return response.json()
        else:
            logging.error(f'Ответ от {ENDPOINT}:{response.status_code}')
            raise APIAnswerError(f'Ответ от {ENDPOINT} не 200',
                                 f'Ответ : {response.status_code}')
    except requests.exceptions.RequestException:
        logging.error(f'Ошибка при запросе к {ENDPOINT}')
        raise APIAnswerError(f'Ошибка при запросе к {ENDPOINT},'
                             f'Параметры : {payload},'
                             f'Ответ : {response.status_code}')


def check_response(response):
    """Проверка ответа."""
    response_error = response
    response_error_type = type(response)
    if not isinstance(response, dict):
        logging.error('Неккоректный тип данных: {}'.format(response_error))
        raise TypeError('Неккоректный тип данных:'
                        '{}'.format(response_error_type))
    if 'homeworks' not in response:
        logging.error('Отсутствует ключ homeworks в ответе API:'
                      '{}'.format(response_error))
        raise TypeError(
            'Отсутствует ключ homeworks в ответе API:'
            '{}'.format(response_error)
        )
    if not isinstance(response['homeworks'], list):
        raise TypeError('Неккоректный тип данных homeworks')
    homeworks = response['homeworks']
    return homeworks


def parse_status(homework):
    """Получение статуса домашней работы."""
    if ('homework_name' or 'status') not in homework:
        logging.error('Некорректные данные в homework')
        raise TypeError('Некорректные данные в homework')
    homework_name = homework['homework_name']
    status = homework['status']
    if status not in HOMEWORK_VERDICTS:
        logging.error('Неизвестный статус домашней работы')
        raise KeyError('Неизвестный статус домашней работы')
    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        sys.exit('Проверьте, заданы ли все токены')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    message = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            new_message = parse_status(homework[0])
            timestamp = response.get('current_date')
            if new_message != message:
                message = new_message
                send_message(bot, message)
            else:
                logging.debug('Новых статусов нет')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    handler = logging.FileHandler("botlog")
    handler1 = logging.StreamHandler()
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
        handlers=([handler, handler1]),
    )
    main()
