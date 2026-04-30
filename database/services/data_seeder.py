from sqlalchemy.ext.asyncio import AsyncSession

from constants.Constants import Constants
from database.repositories.ConditionRepository import ConditionRepository
from database.repositories.CourseRepository import CourseRepository
from database.repositories.TaskRepository import TaskRepository


class DataSeeder:

    constants = Constants()
    available_courses = constants.get_const_courses()
    improvisation_tasks = constants.get_const_improvisation_tasks()

    def __init__(self, session: AsyncSession):
        self.session = session
        self.course_repo = CourseRepository(session)
        self.task_repo = TaskRepository(session)
        self.condition_repo = ConditionRepository(session)

    async def seed_all(self) -> None:
        for course in self.available_courses:
            print("Добавление курса", course)
            await self.course_repo.create(**course)

        for improvisation_task in self.improvisation_tasks:
            await self.task_repo.add_task("Импровизация", improvisation_task["name"], improvisation_task["rules"])
            for improvisation_task_conditions_difficulty_level in improvisation_task["conditions"]:
                for improvisation_task_conditions_difficulty_level_condition in improvisation_task_conditions_difficulty_level["conditions"]:
                    await self.condition_repo.add_condition(
                        improvisation_task["name"],
                        improvisation_task_conditions_difficulty_level_condition,
                        improvisation_task_conditions_difficulty_level["difficulty_level"]
                    )




