"""Смотреть в main."""
from telethon import TelegramClient
from telethon.tl.types import InputMessagesFilterDocument as Doc
import dateutil.parser as datp
from json import load


CONFIG = load(open('config.json'))
# две эти переменные необходимо получить отсюда https://my.telegram.org
# при первом запуске скрипта он захочет чтобы ты залогинился
api_id = CONFIG['api_id']
api_hash = CONFIG['api_hash']

client = TelegramClient('session_name', api_id, api_hash)
client.start()


async def main(chat,
               search_string='pdf',
               max_size: int = None,
               max_date: str = '',
               min_date: str = '',
               limit: int = None,
               filepath: str = None,
               **kwargs):
    """
    Для того чтобы вытаскивать файлы из ТГ чатов.

    :param chat: имя чата или канала вида @имя_чата или ID
    :param search_string: что ищем, строкой
    :param max_size: максимальный размер файла
    :param max_date: дата после которой начнется спуск в прошлое
    :param min_date: дата на которой закончится спуск в прошлое
    :param limit: Максимальное количество загруженных сообщений
    :param filepath: Путь для сохранения фалов
    :return:
    """
    min_date = datp.parse(min_date) if min_date else None

    async for message in client.iter_messages(chat,
                                              search=search_string,
                                              offset_date=None if not max_date
                                              else datp.parse(max_date),
                                              filter=Doc,
                                              limit=limit):
        if (
            hasattr(message, 'media')
            and hasattr(message.media, 'document')
            and (max_size is None or message.media.document.size < max_size)
        ):
            if min_date and message.date < min_date:
                break
            print('\n', message.media.document.attributes[0].file_name, '\n')
            # print(message.stringify())
            await message.download_media(file=filepath, progress_callback=callback)


def callback(current, total):
    print('Downloaded', current, 'out of', total,
          'bytes: {:.2%}'.format(current / total))


def run(**kwargs):
    """
    Это можно импортить себе в программу, чтобы запускать.

    :param kwargs: Такие же как в main.
    """
    with client:
        client.loop.run_until_complete(main(**kwargs))


if __name__ == '__main__':
    import sys
    import time
    s = time.perf_counter()
    if 'chat' not in CONFIG:
        if len(sys.argv) > 1:
            CONFIG['chat'] = sys.argv[1]
        else:
            sys.exit('Not enough args provided.\n'
                     'Must be:\n'
                     'python3 ./main.py <chat @name or id>')
    run(**CONFIG)
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")
