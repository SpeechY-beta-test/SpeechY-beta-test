# main.py
import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from database import db
from database.services.data_seeder import DataSeeder
from database.services.notification_restore import restore_all_notifications
from middlewares.anchor import AnchorManagerMiddleware
from middlewares.db import DbSessionMiddleware
from routers import routers
from logger_config import app_logger
from services.Scheduler import message_scheduler


async def on_startup():
    """Запускается при старте бота."""
    app_logger.info("Проверка структуры БД (миграции должны быть применены отдельно)")

    from sqlalchemy import text
    from database.base import Base

    async with db.engine.begin() as conn:
        result = await conn.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
        ))
        tables_exist = result.scalar()

        if not tables_exist:
            app_logger.info("Таблиц нет, создаем через create_all (первый запуск)")
            await conn.run_sync(Base.metadata.create_all)

            app_logger.info("Заполнение таблиц первоначальными данными")
            async with await db.get_session() as session:
                data_seeder = DataSeeder(session)
                await data_seeder.seed_all()
                await session.commit()
        else:
            app_logger.info("Таблицы существуют, пропускаем создание")

    # Запускаем планировщик
    message_scheduler.start()

    # Восстанавливаем уведомления
    async with await db.get_session() as session:
        from database.repositories.NotificationRepository import NotificationRepository
        from database.repositories.UserRepository import UserRepository

        notification_repo = NotificationRepository(session)
        user_repo = UserRepository(session)

        # Нужно получить экземпляр бота - он будет передан через контекст
        # Для этого лучше передать bot позже, либо сохранить в глобальную переменную
        app_logger.info("База данных готова")
        app_logger.info("Бот запущен")


async def on_shutdown():
    """Запускается при остановке бота."""
    app_logger.info("Закрытие соединений с БД...")
    message_scheduler.stop()
    await db.close()
    app_logger.info("Бот остановлен")


async def main():
    app_logger.info("Инициализация бота...")
    BOT_TOKEN = settings.get_bot_token()
    bot = Bot(
        BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True
        )
    )

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Добавляем бота в данные для возможности восстановления уведомлений
    dp["bot"] = bot

    dp.update.middleware(DbSessionMiddleware())
    dp.update.middleware(AnchorManagerMiddleware())
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.include_routers(*routers)

    try:
        async with await db.get_session() as session:
            from database.repositories.NotificationRepository import NotificationRepository

            notification_repo = NotificationRepository(session)

            await restore_all_notifications(bot, notification_repo)

        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        app_logger.info("Бот остановлен принудительно")
        sys.exit(0)