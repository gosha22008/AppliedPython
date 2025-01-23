import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config import TOKEN
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router_prof, router_log


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=TOKEN)
# Диспетчер
dp = Dispatcher()


# Запуск процесса поллинга новых апдейтов
async def main():
    dp.include_router(router=router_prof)
    dp.include_router(router=router_log)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.info(f"Бот запущен!")
    asyncio.run(main())
    