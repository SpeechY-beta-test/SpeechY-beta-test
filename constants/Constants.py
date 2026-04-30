from typing import List

from schemas.schemas import DifficultyLevel


class Constants:

    def get_const_courses(self) -> List[dict]:
        return self.AVAILABLE_COURSES

    def get_const_improvisation_tasks(self) -> List[dict]:
        return self.IMPROVISATION_TASKS
    AVAILABLE_COURSES: List[dict] = \
        [
        {
            "name": "Дикция",
            "description": "Поможет говорить увереннее, а также подготовиться к публичным выступлениям",
            "is_active": True
        },
        {
            "name": "Импровизация",
            "description": "Поможет подбирать нужные слова в нужный момент",
            "is_active": True
        }
    ]

    IMPROVISATION_TASKS: List[dict] = \
        [
        {
            "name": "Описание предмета",
            "rules": "Ваша задача: говорить о слове 1-2 минуты.\n"
                     "Избегайте слов-паразитов и говорите четко",
            "conditions": [
                {
                    "difficulty_level": DifficultyLevel.EASY.value,
                    "conditions": [
                        "Зонт", "Будильник", "Лампочка", "Карандаш", "Очки", "Чайник", "Рюкзак", "Зеркало", "Свеча",
                        "Вешалка", "Шарик", "Ложка", "Книга", "Дверная ручка", "Калькулятор",
                    ]

                },
                {
                    "difficulty_level": DifficultyLevel.MEDIUM.value,
                    "conditions": [
                        "Скотч", "Термос", "Песочные часы", "Степлер", "Фонарик", "Лупа", "USB-флешка", "Компас",
                        "Микрофон", "Штопор", "Секундомер", "Швейная игла", "Строительная рулетка",
                        "Пульт от телевизора", "Клей-карандаш",
                    ]
                },
                {
                    "difficulty_level": DifficultyLevel.HARD.value,
                    "conditions": [
                        "Гравитация", "Тень", "Пароль", "Интернет", "Эхо", "Скука", "Wi-Fi", "Время",
                        "Тишина", "Алгоритм", "Дежавю", "Репутация", "Граница",
                        "Пауза", "Случайность",
                    ]
                }
            ]
        },
        {
            "name": "Пересказ",
            "rules": "Правила пересказа",
            "conditions": [
                {
                    "difficulty_level": DifficultyLevel.EASY.value,
                    "conditions": [
                        "Текст 1", "Текст 2", "Текст 3"
                    ]

                }
            ]
        }
    ]
