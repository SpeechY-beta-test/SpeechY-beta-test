import time
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import time
from database.models import Notification, User


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_users_with_notifications(self):
        """
        Get all users with turned on notifications
        :return: List of User objects
        """
        result = await self.session.execute(
            select(User)
            .where(User.notifications == True)
        )
        return result.scalars().all()

    async def get_all_notifications_with_users(self) -> List[tuple[Notification, User]]:
        """
        Get all notifications with users
        Used to restore the scheduler at startup
        :return: a list of tuples(Notification, User)
        """

        result = await self.session.execute(
            select(Notification, User)
            .join(User, Notification.user_id == User.id)
            .order_by(Notification.user_id, Notification.notification_time)
        )
        return result.all()


    async def get_all_by_user_id(self, user_id) -> List[str]:
        """
        Get all users notifications time in HH:MM format
        :param user_id:
        :return:
        Notifications time in HH:MM format
        """
        result = await self.session.execute(
            select(Notification.notification_time)
            .where(Notification.user_id == user_id)
            .order_by(Notification.notification_time)
        )

        times = result.scalars().all()

        return [t.strftime("%H:%M") for t in times]

    async def get_all_raw(self, user_id: int):
        """
        Get all Notification objects by user_id
        :param user_id:
        :return:
        List of Notification objects
        """
        result = await self.session.execute(
            select(Notification.notification_time)
            .where(Notification.user_id == user_id)
            .order_by(Notification.notification_time)
        )
        return result.scalars().all()

    async def add_notification(
            self,
            telegram_id: int,
            notification_time: time
    ) -> Optional[Notification]:
        """
        Create and add Notification object in db
        :param telegram_id:
        :param notification_time:
        :return:
        Added Notification object
        """
        result = await self.session.execute(
            select(User.id).where(User.telegram_id == telegram_id)
        )
        user_id = result.scalar_one_or_none()
        notification = Notification(
            user_id=user_id,
            notification_time=notification_time
        )
        self.session.add(notification)
        await self.session.flush()
        await self.session.refresh(notification)
        return notification

    async def add_notification_from_string(
            self, user_id: int,
            time_str: str
    ) -> Optional[Notification]:
        """
        Add Notification object in db from string with HH:MM format
        :param user_id:
        :param time_str:
        :return:
        Added Notification object
        """
        try:
            hour, minute = map(int, time_str.split(':'))
            notification_time = time(hour, minute)

            return await self.add_notification(user_id, notification_time)
        except (ValueError, AttributeError):
            return None

    async def clear_all_user_notifications(self, user_id: int) -> int:
        """
        Delete all Notification objects from db by user_id
        :param user_id:
        :return:
        amount of deleted objects
        """
        result = await self.session.execute(
            select(Notification).where(Notification.user_id == user_id)
        )
        notifications = result.scalars().all()

        for notification in notifications:
            await self.session.delete(notification)

        await self.session.flush()
        return len(notifications)

