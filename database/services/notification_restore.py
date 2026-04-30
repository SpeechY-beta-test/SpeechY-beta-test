from typing import TYPE_CHECKING

from logger_config import app_logger
from services.Scheduler import message_scheduler

if TYPE_CHECKING:
    from aiogram import Bot
    from database.repositories.NotificationRepository import  NotificationRepository
    from database.models import Notification, User


async def restore_all_notifications(
        bot: "Bot",
        notification_repo: "NotificationRepository"
) -> int:
    """
    Restore all scheduled notifications on bot startup
    :param bot:
    :param notification_repo:
    :return: Amount of restored notifications
    """

    notifications_with_users = await notification_repo.get_all_notifications_with_users()
    restored_count = 0

    for notification, user in notifications_with_users:
        if not user.notifications:
            app_logger.debug(
                f"Пропуск уведомления для {user.telegram_id} - уведомления выключены"
            )
            continue


        success = message_scheduler.scheduler_daily_notification(
            bot=bot,
            telegram_id=user.telegram_id,
            hour=notification.notification_time.hour,
            minute=notification.notification_time.minute,
            notification_id=notification.id,
            message="Пора тренировать свою речь! Жду тебя\n Твой SpeechY"
        )

        if success:
            restored_count += 1
            app_logger.debug(
                f"Восстановлено уведомление #{notification.id} "
                f"для {user.telegram_id} "
                f"на {notification.notification_time.strftime('%H:%M')}"
            )
    app_logger.info(
        f"Восстановлено {restored_count} уведомлений"
    )
    return restored_count


async def restore_user_notifications(
        bot: "Bot",
        notification_repo: "NotificationRepository",
        user_id: int
) -> int:
    """
    Restore notifications for specific user
    Used for refresh after user settings
    :param bot:
    :param notification_repo:
    :param user_id:
    :return:
    """
    notifications = await notification_repo.get_all_raw(user_id)

    restored_count = 0

    for notification in notifications:
        success = message_scheduler.scheduler_daily_notification(
            bot=bot,
            telegram_id=user_id,
            hour=notification.hour,
            minute=notification.minute,
            notification_id=notification.id
        )
        if success:
            restored_count += 1
    if restored_count:
        app_logger.info(
            f"Восстановлено {restored_count} уведомлений для пользователя {user_id}"
        )
    return restored_count
