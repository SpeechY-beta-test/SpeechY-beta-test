import random
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Course, Task
from database.repositories.CompletedTaskRepository import CompletedTaskRepository
from database.repositories.CourseRepository import CourseRepository


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.course_repo = CourseRepository(session)

    async def add_task(
            self,
            course_name: str,
            task_name: str,
            rules: str
    ) -> Optional[Task]:
        """
        Add course task to db
        :param course_name:
        :param task_name:
        :param rules:
        :return:
        Task object
        """
        query = select(Course).where(Course.name == course_name)
        result = await self.session.execute(query)
        course = result.scalar_one_or_none()
        task = Task(
            course_id=course.id,
            name=task_name,
            rules=rules
        )
        self.session.add(task)
        await self.session.flush()
        return task

    async def get_random_task(self, course_name: str) -> Task:
        """
        Get random course task from db
        :param course_name:
        :return:
        Task object
        """
        course = await self.course_repo.get_by_name(course_name)
        result = await self.session.execute(
            select(Task).where(Task.course_id == course.id)
        )
        tasks = result.scalars().all()
        if tasks:
            random_task = random.choice(tasks)
            return random_task




