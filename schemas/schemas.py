from enum import Enum


class DifficultyLevel(str, Enum):
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'


class CourseName(str, Enum):
    IMPROVISATION = "Импровизация"
    DICTION = "Дикция"


class StreakStatus(str, Enum):
    INCREASED = "increased"
    RESET = "reset"
    FIRST_TASK = "first_task"
    ALREADY_COMPLETED = "already_completed"
    STREAK_BROKEN = "streak_broken"


