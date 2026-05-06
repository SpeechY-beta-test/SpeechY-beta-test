from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from constants.Constants import Constants
from database.models import Course, Task, Condition
from database.repositories.ConditionRepository import ConditionRepository
from database.repositories.CourseRepository import CourseRepository
from database.repositories.TaskRepository import TaskRepository
from schemas.schemas import CourseName


class DataSeeder:

    constants = Constants()
    available_courses = constants.get_const_courses()
    improvisation_tasks = constants.get_const_improvisation_tasks()

    def __init__(self, session: AsyncSession):
        self.session = session
        self.course_repo = CourseRepository(session)
        self.task_repo = TaskRepository(session)
        self.condition_repo = ConditionRepository(session)
    async def update_seed_data(self) -> None:
        """
        Обновляет существующие данные, не удаляя их
        :return: None
        """

        for course_data in self.available_courses:
            result = await self.session.execute(
                select(Course).where(Course.name == course_data["name"])
            )
            course = result.scalar_one_or_none()

            if course:
                course.description = course_data.get("description", course.description)
                course.is_active = course_data.get("is_active", course.is_active)
            else:
                self.session.add(Course(**course_data))

        await self.session.flush()
        result = await self.session.execute(
            select(Course.id).where(Course.name == CourseName.IMPROVISATION.value)
        )
        improv_course_id = result.scalar_one_or_none()
        if not improv_course_id:
            raise ValueError("Курс Импровизация не найден")

        for task_data in self.improvisation_tasks:
            result = await self.session.execute(
                select(Task).where(
                    Task.name == task_data["name"],
                    Task.course_id == improv_course_id
                )
            )
            task = result.scalar_one_or_none()
            if task:
                task.rules = task_data.get("rules", task.rules)
            else:
                task = Task(
                    course_id=improv_course_id,
                    name=task_data["name"],
                    rules=task_data["rules"]
                )
                self.session.add(task)
                await self.session.flush()
            for condition_group in task_data.get("conditions", []):
                difficulty = condition_group["difficulty_level"]
                for condition_text in condition_group["conditions"]:
                    result = await self.session.execute(
                        select(Condition).where(
                            Condition.task_id == task.id,
                            Condition.condition == condition_text,
                            Condition.difficulty_level == difficulty
                        )
                    )
                    existing = result.scalar_one_or_none()

                    if not existing:
                        self.session.add(
                            Condition(
                                task_id=task.id,
                                condition=condition_text,
                                difficulty_level=difficulty
                            )
                        )
        await self.session.commit()
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




