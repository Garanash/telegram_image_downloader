import os
import logging
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
API_ID = 'ваш_api_id'  # Получить на my.telegram.org
API_HASH = 'ваш_api_hash'  # Полуить на my.telegram.org
BOT_TOKEN = 'ваш_bot_token'  # Полуить у @BotFather
CHANNEL_ID = 'username_or_id_канала'  # Например, '@channelname' или -1001234567890
DOWNLOAD_PATH = 'downloaded_images'  # Основная папка для загрузки

# Создаем клиент
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


async def download_media(message, folder_name):
    """Скачиваем медиа из сообщения"""
    if not message.media:
        return

    media = message.media
    file_path = None

    try:
        if isinstance(media, MessageMediaPhoto):
            file_path = await client.download_media(
                message,
                file=os.path.join(folder_name, f'photo_{message.id}.jpg')
            )
        elif isinstance(media, MessageMediaDocument):
            # Проверяем, что документ - это изображение
            if message.document.mime_type.startswith('image/'):
                file_path = await client.download_media(
                    message,
                    file=os.path.join(folder_name, f'document_{message.id}')
                )

        if file_path:
            logger.info(f'Downloaded: {file_path}')
    except Exception as e:
        logger.error(f'Error downloading media: {e}')


@client.on(events.NewMessage(chats=CHANNEL_ID))
async def handle_new_message(event):
    """Обработка новых сообщений в канале"""
    message = event.message
    post_id = message.id

    # Создаем папку для поста
    post_folder = os.path.join(DOWNLOAD_PATH, f'post_{post_id}')
    os.makedirs(post_folder, exist_ok=True)

    # Скачиваем медиа из самого поста
    await download_media(message, post_folder)

    # Получаем комментарии к посту (если есть)
    comments_folder = os.path.join(post_folder, 'comments')
    os.makedirs(comments_folder, exist_ok=True)

    try:
        async for comment in client.iter_messages(CHANNEL_ID, reply_to=post_id):
            await download_media(comment, comments_folder)
    except Exception as e:
        logger.error(f'Error fetching comments: {e}')


async def main():
    """Основная функция"""
    # Проверяем, что основная папка существует
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)

    logger.info('Bot started. Press Ctrl+C to stop.')
    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info('Bot stopped by user')
    except Exception as e:
        logger.error(f'Error: {e}')