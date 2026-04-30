import random
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import DifficultyLevel, Condition, Task
from database.repositories.CompletedTaskRepository import CompletedTaskRepository
from database.repositories.TaskRepository import TaskRepository


class ConditionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.task_repo = TaskRepository(session)
        self.completed_task_repository = CompletedTaskRepository(session)

    async def add_condition(
            self,
            task_name: str,
            condition: str,
            difficulty_level: DifficultyLevel
    ) -> Optional[Condition]:
        """
        Add task condition in db
        :param task_name:
        :param condition:
        :param difficulty_level:
        :return:
        Added condition
        """

        query = select(Task).where(task_name == Task.name)
        result = await self.session.execute(query)
        task = result.scalar_one_or_none()
        condition = Condition(
            task_id=task.id,
            condition=condition,
            difficulty_level=difficulty_level
        )
        self.session.add(condition)
        await self.session.flush()
        return condition

    async def get_random_condition_by_level(
            self,
            telegram_id: int,
            task_id: int,
            level: DifficultyLevel
    ) -> Condition:
        """
        get random task condition based on user course progress level
        :param telegram_id
        :param task_id:
        :param level:
        :return:
        Random condition
        """
        query = select(Condition).where(Condition.task_id == task_id).where(Condition.difficulty_level == level)
        result = await self.session.execute(query)
        conditions = result.scalars().all()
        completed_task_conditions = await self.completed_task_repository.get_all_completed_task_condition_ids(
            telegram_id, task_id
        )
        available_conditions = [
            condition for condition in conditions
            if condition.id not in completed_task_conditions
        ]
        print("Completed_task_conditions: ", completed_task_conditions)
        print("Available ids: ", [condition.id for condition in available_conditions])
        if available_conditions:
            random_condition = random.choice(available_conditions)
            return random_condition



