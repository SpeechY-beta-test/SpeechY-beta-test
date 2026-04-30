import re


class UserUtils:
    @staticmethod
    def validate_user_name(name: str):
        name = name.strip()

        if len(name) < 2 or len(name) > 50:
            raise ValueError("Имя должно содержать от 2 до 50 символов")
        if not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', name):
            raise ValueError("Имя может содержать только буквы, пробел или дефис")

        if '  ' in name:
            raise ValueError("Имя не может содержать двойные пробелы")

        if name.startswith('-') or name.endswith('-'):
            raise ValueError("Дефис не может быть в начале или конце имени")

        if '--' in name:
            raise ValueError("Имя не может содержать двойные дефисы")

        return True

    @staticmethod
    def validate_user_notifications(data: str) -> list[str]:
        if not data or not data.strip():
            raise ValueError("Строка не может быть пустой")

        data = re.sub(r'[;,]\s*', ' ', data)
        data = data.replace(',', ' ')

        times = [t.strip() for t in data.split() if t.strip()]

        if not times:
            raise ValueError("Не найдено ни одного времени")

        time_pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'

        for t in times:
            if not re.match(time_pattern, t):
                raise ValueError(
                    f"'{t}' - неверный формат.\n"
                    "Вводи времена через пробел или запятую.\n"
                    "Пример: 9:30, 10:30, 11:30"
                )
        return times
