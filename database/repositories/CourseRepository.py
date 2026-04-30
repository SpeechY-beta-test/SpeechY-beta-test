from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Course


class CourseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, course_id: int) -> Course | None:
        """
        get course by id from db
        :param course_id:
        :return:
        Course object from db
        """
        result = await self.session.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> Optional[Course]:
        """
        Create and add Course object in db
        :param kwargs:
        :return:
        Created Course object
        """
        course = Course(**kwargs)
        self.session.add(course)
        await self.session.flush()
        return course

    async def get_all_available_courses(self):
        """
        get all Course objects from db
        :return:
        List of all Course objects
        """
        result = await self.session.execute(
            select(Course)
        )
        return result.scalars().all()

    async def get_course_by_id(self, course_id) -> Optional[Course]:
        """
        get Course object from db by id
        :param course_id:
        :return:
        Course object
        """
        result = await self.session.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, course_name: str) -> Optional[Course]:
        """
        Get course object from db by name
        :param course_name:
        :return:
        Course object
        """
        result = await self.session.execute(
            select(Course).where(Course.name == course_name)
        )
        course = result.scalar_one_or_none()
        return course
