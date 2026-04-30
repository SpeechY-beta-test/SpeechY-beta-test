from abc import ABC, abstractmethod

from database.models import Task, Condition
from schemas.schemas import CourseName


class MessageFormatter(ABC):

    """
    Abstract base class for message formatting
    """

    @abstractmethod
    def format_task_message(
            self,
            task: Task,
            condition: Condition
    ) -> str:
        pass


class ImprovizationFormatter(MessageFormatter):
    """
    Formatter for improvization course
    """

    def format_task_message(
            self,
            task: Task,
            condition: Condition
    ) -> str:
        return (
            f"🎭 Задание: <b><i>{task.name}</i></b>\n\n"
            f"📋 <i>{task.rules}</i>\n\n"
            f"🎲 Твое слово: <b>{condition.condition}</b>\n\n"
            f"💡 Говори без остановки 60 секунд!"
        )


class MessageFormatterFactory:
    """
    Factory for creating formatters based on course name
    """

    _formatters = {
        CourseName.IMPROVISATION: ImprovizationFormatter(),

    }

    @classmethod
    def get_formatter(cls, course_name: CourseName) -> MessageFormatter:
        """
        Get formatter for specific course
        :param course_name:
        :return: formatter
        """

        formatter = cls._formatters.get(course_name)
        if not formatter:
            raise ValueError(
                f"No formatter found for course {course_name}"
            )
        return formatter

