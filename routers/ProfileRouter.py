import asyncio

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from Managers.AnchorMessageManager import AnchorMessageManager
from database.repositories.CourseRepository import CourseRepository
from database.repositories.NotificationRepository import NotificationRepository
from database.repositories.ProgressRepository import ProgressRepository
from database.repositories.UserRepository import UserRepository
from keyboards.ProfileKeyboards import profile_back_keyboard, change_notifications_keyboard, profile_keyboard
from keyboards.RegisterKeyboards import get_skip_notifications_keyboard
from logger_config import app_logger
from services.Scheduler import message_scheduler
from states.UserStates import UserStates
from utils.ProfileUtils import ProfileUtils
from utils.UserUtils import UserUtils

profile_router = Router()


@profile_router.callback_query(F.data == "get_profile")
async def get_profile_handler(
        callback: CallbackQuery,
        user_repo: UserRepository,
        notification_repo: NotificationRepository,
        progress_repo: ProgressRepository,
        course_repo: CourseRepository,
        state: FSMContext,
        session: AsyncSession
):
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    anchor_msg_manager = AnchorMessageManager(
        user_id=user.id,
        chat_id=callback.message.chat.id,
        session=session,
        bot=callback.message.bot,
        state=state
    )
    profile_text = await ProfileUtils.get_profile_text(
        callback,
        user_repo,
        notification_repo,
        progress_repo,
        course_repo
    )
    await anchor_msg_manager.edit_anchor(profile_text, reply_markup=profile_keyboard().as_markup())
    await state.set_state(None)


@profile_router.callback_query(F.data == "configure_notifications")
async def configure_notifications_handler(
        callback: CallbackQuery,
        state: FSMContext,
        user_repo: UserRepository,
        notification_repo: NotificationRepository,
        anchor_manager: AnchorMessageManager
):
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    notifications = await notification_repo.get_all_raw(user.id)
    target_keyboard = change_notifications_keyboard(bool(user.notifications)) if notifications else profile_back_keyboard()
    await anchor_manager.edit_anchor(
        "Теперь напиши мне, когда тебе <i>напоминать</i> о тренировках\nНапример, 9:30 10:30 11:30",
        reply_markup=target_keyboard.as_markup()
    )
    await state.set_state(UserStates.change_notifications)


@profile_router.callback_query(F.data == "off_notifications")
async def off_notifications_handler(
        callback: CallbackQuery,
        user_repo: UserRepository,
        notification_repo: NotificationRepository,
        progress_repo: ProgressRepository,
        course_repo: CourseRepository,
        state: FSMContext,
        anchor_manager: AnchorMessageManager,
        session: AsyncSession
):
    await state.set_state(None)
    await user_repo.toggle_user_notifications(callback.from_user.id)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)

    if not user.notifications:
        message_scheduler.remove_notification(callback.from_user.id )

    await get_profile_handler(
        callback,
        user_repo,
        notification_repo,
        progress_repo,
        course_repo,
        state,
        session
    )


@profile_router.message(UserStates.change_notifications)
async def change_notifications_handler(
        message: Message,
        state: FSMContext,
        notification_repo: NotificationRepository,
        user_repo: UserRepository,
        progress_repo: ProgressRepository,
        course_repo: CourseRepository,
        anchor_manager: AnchorMessageManager
):
    try:
        notifications_times = UserUtils.validate_user_notifications(message.text)
        if notifications_times:
            user = await user_repo.get_by_telegram_id(message.from_user.id)
            await notification_repo.clear_all_user_notifications(user.id)
            message_scheduler.remove_all_user_notifications(message.from_user.id)

            for time in notifications_times:
                notification = await notification_repo.add_notification_from_string(message.from_user.id, time)
                app_logger.info(f"Уведомление в БД: id={notification.id if notification else None}")
                hour, minute = map(int, time.split(':'))
                app_logger.info(f"Планируем уведомление для {message.from_user.id} на {hour}:{minute}")
                message_scheduler.scheduler_daily_notification(
                    bot=message.bot,
                    telegram_id=message.from_user.id,
                    hour=hour,
                    minute=minute,
                    notification_id=notification.id
                )
        profile_msg_text = await ProfileUtils.get_profile_text(
            message,
            user_repo,
            notification_repo,
            progress_repo,
            course_repo
        )
        await anchor_manager.delete_user_message(message)
        await anchor_manager.edit_anchor(profile_msg_text, reply_markup=profile_keyboard().as_markup())
        await state.set_state(None)
    except ValueError as e:
        await anchor_manager.delete_user_message(message)
        await anchor_manager.edit_anchor(str(e), reply_markup=get_skip_notifications_keyboard().as_markup())
        await state.set_state(UserStates.change_notifications)


@profile_router.callback_query(F.data == "change_name")
async def change_name_handler(
        callback: CallbackQuery,
        state: FSMContext,
        anchor_manager: AnchorMessageManager
):
    await anchor_manager.edit_anchor(
        f"Введи новое имя, чтобы я тебя точно ни с кем не перепутал :)",
        reply_markup=profile_back_keyboard().as_markup())
    await state.set_state(UserStates.change_name)


@profile_router.message(UserStates.change_name)
async def set_new_user_name_handler(
        message: Message,
        user_repo: UserRepository,
        state: FSMContext,
        notification_repo: NotificationRepository,
        progress_repo: ProgressRepository,
        course_repo: CourseRepository,
        anchor_manager: AnchorMessageManager
):
    try:
        is_validated = UserUtils.validate_user_name(message.text)
        if is_validated:
            await user_repo.change_name_by_telegram_id(message.from_user.id, message.text)
            profile_message_text = await ProfileUtils.get_profile_text(
                message,
                user_repo,
                notification_repo,
                progress_repo,
                course_repo
            )
            await anchor_manager.delete_user_message(message)
            await anchor_manager.edit_anchor(profile_message_text, reply_markup=profile_keyboard().as_markup())
            await state.clear()
    except ValueError:
        await anchor_manager.delete_user_message(message)
        await anchor_manager.edit_anchor(
            "Введенное тобой имя некорректно, давай еще раз",
            reply_markup=profile_back_keyboard().as_markup()
        )
        await state.set_state(UserStates.change_name)

