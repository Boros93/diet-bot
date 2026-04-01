import asyncio
from aiogram import Bot, Dispatcher

from app.config import BOT_TOKEN
from app.handlers import router


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN mancante nel file .env")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())