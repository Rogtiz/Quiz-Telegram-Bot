import requests
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from handlers.user_handlers import setup as handlers_setup
from config import TOKEN

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    handlers_setup(dp)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
