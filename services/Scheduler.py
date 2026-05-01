from datetime import datetime
from typing import Optional, List

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from logger_config import app_logger


class MessageScheduler:
    """
    Service for scheduling users' daily messages
    """

    _instance: Optional["MessageScheduler"] = None
    scheduler: AsyncIOScheduler

    def __new__(cls):
        """
        Singleton pattern
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
        return cls._instance

    @staticmethod
    def _get_job_id(telegram_id: int, notification_id: int = 0) -> str:
        """
        Gen unic id task for user
        :param telegram_id:
        :return: unic id
        """
        if notification_id:
            return f"daily_notification_{telegram_id}_{notification_id}"
        return f"daily_notification_{telegram_id}"

    async def _send_notification(
            self,
            bot: Bot,
            telegram_id: int,
            message: str
    ) -> None:
        """
        Send notification to user
        Inner method calling by Scheduler
        :param bot:
        :param telegram_id:
        :param message:
        :return: None
        """

        try:
            await bot.send_message(
                chat_id=telegram_id,
                text=message,
                disable_notification=False
            )
            app_logger.info(
                f"[{datetime.now()}] Отправлено уведомление пользователю {telegram_id}"
            )
        except Exception as e:
            app_logger.error(
                f"Ошибка отправки пользователю {telegram_id} {e}"
            )

    def scheduler_daily_notification(
            self,
            bot: Bot,
            telegram_id: int,
            hour: int,
            minute: int,
            notification_id: Optional[int] = None,
            message: str = "Пора тренировать речь!\nSpeechY соскучился...",
    ) -> bool:
        """
        Schedule daily notification for user
        :param bot:
        :param telegram_id:
        :param hour:
        :param minute:
        :param notification_id:
        :param message:
        :return: True if task succesfully added/updated
        """
        try:
            if not self.scheduler.running:
                app_logger.warning("Планировщик не запущен, запускаем...")
                self.scheduler.start()
            job_id = self._get_job_id(telegram_id, notification_id or 0)
            existing_job = self.scheduler.get_job(job_id)
            if existing_job:
                app_logger.debug(
                    f"Задача {job_id} уже существует, обновление"
                )
            self.scheduler.add_job(
                func=self._send_notification,
                trigger=CronTrigger(hour=hour, minute=minute),
                args=[bot, telegram_id, message],
                id=job_id,
                replace_existing=True,
                misfire_grace_time=300
            )

            notif_info = f'#{notification_id}' if notification_id else ""
            app_logger.info(
                f"Запланировано уведомление {notif_info} для {telegram_id} на {hour:02d}:{minute:02d}"
            )
            return True
        except Exception as e:
            app_logger.error(
                f"Ошибка планирования для {telegram_id}: {e}"
            )
            return False

    def remove_notification(
            self,
            telegram_id: int,
            notification_id: Optional[int] = None
    ) -> int:
        """
        Delete scheduler notification for user
        :param telegram_id:
        :param notification_id:
        :return: amount of deleted notifications
        """
        if notification_id is not None:
            job_id = self._get_job_id(telegram_id, notification_id)
            job = self.scheduler.get_job(job_id)
            if job:
                self.scheduler.remove_job(job_id)
                app_logger.info(f"Удалено уведомлений {notification_id} для {telegram_id}")
                return True
            return False
        else:

            removed_count = 0
            jobs = self.scheduler.get_jobs()
            prefix = f"daily_notification_{telegram_id}"
            for job in jobs:
                if job.id.startswith(prefix):
                    self.scheduler.remove_job(job.id)
                    removed_count += 1
            if removed_count:
                app_logger.info(
                    f"Удалено {removed_count} уведомлений для {telegram_id}"
                )
            return removed_count > 0

    def remove_all_user_notifications(
            self,
            telegram_id: int
    ) -> int:
        """
        Delete all user notifications
        :param telegram_id:
        :return: Amount of deleted notifications
        """
        removed_count = 0
        jobs = self.scheduler.get_jobs()
        prefix = f"daily_notification_{telegram_id}"

        for job in jobs:
            if job.id.startswith(prefix):
                self.scheduler.remove_job(job.id)
                removed_count += 1

        if removed_count:
            app_logger.info(
                f"Удалено {removed_count} уведомлений для {telegram_id}"
            )
        return removed_count

    def is_notification_scheduled(
            self,
            telegram_id: int
    ) -> bool:
        """
        Check if scheduled notification existing for user
        :param telegram_id:
        :return:  True if notification is scheduled
        """
        job_id = self._get_job_id(telegram_id)
        return self.scheduler.get_job(job_id) is not None

    def start(self) -> None:
        """
        Start scheduler
        :return: None
        """
        if not self.scheduler.running:
            self.scheduler.start()
            app_logger.info(
                "Планировщик уведомлений запущен"
            )

    def get_user_notifications(
            self,
            telegram_id: int
    ) -> List[dict]:
        notifications = []
        jobs = self.scheduler.get_jobs()
        prefix = f"daily_notification_{telegram_id}"

        for job in jobs:
            if job.id.startswith(prefix):
                trigger = job.trigger
                notifications.append({
                    "job_id": job.id,
                    'hour': trigger.hour,
                    'minute': trigger.minute,
                    'next_run_time': job.next_run_time
                })

        return notifications
    def stop(self) -> None:
        """
        Stop scheduler
        :return: None
        """
        if self.scheduler.running:
            self.scheduler.shutdown()
            app_logger.info(
                "Планировщик уведомлений остановлен"
            )

    def get_all_jobs(self) -> list:
        """
        Get a list of all scheduled tasks
        :return: list
        """
        return self.scheduler.get_jobs()


message_scheduler = MessageScheduler()
