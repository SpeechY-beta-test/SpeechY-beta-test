from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, Update
from sqlalchemy.ext.asyncio import AsyncSession

from Managers.AnchorMessageManager import AnchorMessageManager
from database.repositories.UserRepository import UserRepository
from logger_config import app_logger


class AnchorManagerMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        """
        Middleware для внедрения AnchorMessageManager в хендлеры
        """
        session: AsyncSession = data.get("session")
        state: FSMContext = data.get("state")
        if not session:
            app_logger.warning("AnchorManagerMiddleware: session not found in data")
            return await handler(event, data)

        user_telegram_id = None
        chat_id = None
        bot = None

        if event.message and isinstance(event.message, Message):
            user_telegram_id = event.message.from_user.id
            chat_id = event.message.chat.id
            bot = event.message.bot
            app_logger.debug(f"AnchorManagerMiddleware: Message from user {user_telegram_id}")

        elif event.callback_query and isinstance(event.callback_query, CallbackQuery):
            user_telegram_id = event.callback_query.from_user.id
            if event.callback_query.message:
                chat_id = event.callback_query.message.chat.id
            bot = event.callback_query.bot
            app_logger.debug(f"AnchorManagerMiddleware: CallbackQuery from user {user_telegram_id}")
        if user_telegram_id and chat_id and bot:
            try:
                # Получаем пользователя из БД
                user_repo = UserRepository(session)
                db_user = await user_repo.get_by_telegram_id(user_telegram_id)
                print(db_user)
                if db_user:
                    # Создаем AnchorMessageManager
                    anchor_manager = AnchorMessageManager(
                        user_id=db_user.id,
                        chat_id=chat_id,
                        bot=bot,
                        session=session,
                        state=state
                    )
                    data["anchor_manager"] = anchor_manager
                    app_logger.debug(f"AnchorManagerMiddleware: Created AnchorMessageManager for user {db_user.id}")
                else:
                    app_logger.warning(f"AnchorManagerMiddleware: User with telegram_id {user_telegram_id} not found")
            except Exception as e:
                app_logger.error(f"AnchorManagerMiddleware: Error creating AnchorMessageManager: {e}")
        else:
            app_logger.debug(
                f"AnchorManagerMiddleware: Missing data - user_id={user_telegram_id}, chat_id={chat_id}, bot={bool(bot)}")

        return await handler(event, data)
