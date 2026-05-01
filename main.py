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


def run_migrations():
    """Запускает миграции Alembic перед стартом бота."""
    try:
        from alembic.config import Config
        from alembic import command

        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        app_logger.info("✅ Миграции успешно применены")
    except Exception as e:
        app_logger.error(f"❌ Ошибка выполнения миграций: {e}")
        raise


async def seed_initial_data():
    """Заполняет таблицы начальными данными (курсы, задания)."""
    async with await db.get_session() as session:
        from database.repositories.CourseRepository import CourseRepository
        course_repo = CourseRepository(session)

        # Проверяем, есть ли уже курсы
        courses = await course_repo.get_all_available_courses()
        if not courses:
            app_logger.info("Заполнение таблиц первоначальными данными...")
            data_seeder = DataSeeder(session)
            await data_seeder.seed_all()
            await session.commit()
            app_logger.info("✅ Начальные данные добавлены")
        else:
            app_logger.info("Начальные данные уже есть, пропускаем")


async def on_startup():
    """Запускается при старте бота."""
    app_logger.info("Бот запущен")


async def on_shutdown():
    """Запускается при остановке бота."""
    app_logger.info("Закрытие соединений с БД...")
    message_scheduler.stop()
    await db.close()
    app_logger.info("Бот остановлен")


async def main():
    app_logger.info("Инициализация бота...")

    # 1. Применяем миграции
    run_migrations()

    # 2. Заполняем начальными данными (если нужно)
    await seed_initial_data()

    # 3. Запускаем планировщик
    message_scheduler.start()

    # 4. Создаем бота
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

    dp["bot"] = bot

    dp.update.middleware(DbSessionMiddleware())
    dp.update.middleware(AnchorManagerMiddleware())
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.include_routers(*routers)

    try:
        # 5. Восстанавливаем уведомления
        async with await db.get_session() as session:
            from database.repositories.NotificationRepository import NotificationRepository
            notification_repo = NotificationRepository(session)
            await restore_all_notifications(bot, notification_repo)

        # 6. Запускаем поллинг
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