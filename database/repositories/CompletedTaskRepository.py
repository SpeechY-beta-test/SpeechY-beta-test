from typing import Optional, List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import CompletedTask
from database.repositories.UserRepository import UserRepository


class CompletedTaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def exists_completed_task_condition(
            self,
            user_id: int,
            task_id: int,
            condition_id: int
    ) -> bool:
        """
        Check if completed task condition exists
        :param user_id:
        :param task_id:
        :param condition_id:
        :return: bool flag
        """
        res = await self.session.execute(
            select(CompletedTask)
            .where(CompletedTask.user_id == user_id)
            .where(CompletedTask.task_id == task_id)
            .where(CompletedTask.condition_id == condition_id)
            .with_only_columns(CompletedTask.id)
            .limit(1)
        )
        return res.scalar_one_or_none() is not None

    async def add_completed_task_condition(
            self,
            telegram_id: int,
            task_id: int,
            condition_id: int
    ) -> CompletedTask:
        """
        Add completed task condition.
        :param telegram_id:
        :param task_id:
        :param condition_id:
        :return: CompletedTask object
        """
        user = await self.user_repo.get_by_telegram_id(telegram_id)

        if await self.exists_completed_task_condition(user.id, task_id, condition_id):
            raise ValueError(
                f"Task {task_id} with condition {condition_id} "
                f"already completed by user {telegram_id}"
            )

        completed_task = CompletedTask(
            user_id=user.id,
            task_id=task_id,
            condition_id=condition_id
        )
        self.session.add(completed_task)
        await self.session.flush()
        return completed_task

    async def clear_all_completed_task_conditions(
            self,
            telegram_id: int,
            task_id: int
    ) -> int:
        """
        Delete all completed task conditions for a specific task and user.
        :param telegram_id: User's Telegram ID
        :param task_id: Task ID
        :return: Number of deleted records
        :raises ValueError: If user not found
        """
        user = await self.user_repo.get_by_telegram_id(telegram_id)

        result = await self.session.execute(
            delete(CompletedTask).where(
                CompletedTask.user_id == user.id,
                CompletedTask.task_id == task_id
            )
        )

        await self.session.flush()
        return result.rowcount

    async def get_all_completed_task_condition_ids(
            self,
            telegram_id: int,
            task_id: int
    ) -> List[int]:
        """
        Get all ids of conditions completed task
        :param telegram_id:
        :param task_id:
        :return:
        list of ids
        """
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        ids = []
        res = await self.session.execute(
            select(CompletedTask)
            .where(CompletedTask.user_id == user.id)
            .where(CompletedTask.task_id == task_id)
        )

        completed_task_conditions = res.scalars().all()
        for condition in completed_task_conditions:
            ids.append(condition.condition_id)
        print(ids)
        return ids
