from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database.models import Progress
from database.repositories.UserRepository import UserRepository


class ProgressRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def add_progress_to_user(
            self,
            telegram_id: int,
            course_id: int,
            progress: int = 0
    ) -> Progress:
        """
        Add Progress object to db
        :param telegram_id:
        :param course_id:
        :param progress:
        :return:
        Added Progress object
        """
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        progress = Progress(
            user_id=user.id,
            course_id=course_id,
            progress=progress
        )
        self.session.add(progress)
        await self.session.flush()
        return progress

    async def get_user_progress(self, user_id):
        """
        Get all user Progress objects
        :param user_id:
        :return:
        List of Progress objects
        """
        query = select(Progress).where(Progress.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user_course_progress(
            self,
            course_id: int,
            user_id: int
    ) -> Optional[Progress]:
        """
        Get Progress object for choosing course and user
        :param course_id:
        :param user_id:
        :return:
        Progress object
        """
        query = select(Progress)\
            .where(Progress.course_id == course_id)\
            .where(Progress.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def add_course_progress_to_user(
            self,
            user_id: int,
            course_id: int
    ) -> int:

        """
        Add XP (Progress.progress) to user by course_id
        :param user_id:
        :param course_id:
        :return:
        Added XP
        """
        print("user_id: ", user_id)
        print("course_id", course_id)
        result = await self.session.execute(
            select(Progress).where(Progress.user_id == user_id)
            .where(Progress.course_id == course_id)
        )
        exp = settings.get_EXP_FOR_IMPROVIZATION_TASKS()
        course_progress = result.scalar_one_or_none()
        course_progress.progress += exp
        await self.session.commit()
        print("Прошли add_curse to user")
        return exp
