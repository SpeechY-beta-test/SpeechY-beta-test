import os
import random
from typing import List

from aiogram.types import Message
from faster_whisper import WhisperModel

from database.repositories.CourseRepository import CourseRepository
from utils.SpeechAnalyzer import SpeechAnalyzer


class TaskUtils:
    @staticmethod
    async def get_all_available_tasks_message(
            course_repo: CourseRepository
    ) -> str:
        courses = await course_repo.get_all_available_courses()
        msg = ""
        i = 0
        for course in courses:

            msg += f"{i + 1}. <b>{course.name}</b>\n" \
                   f"<i>{course.description}</i>\n"
            i += 1
        return msg

    @staticmethod
    async def gen_random_index_of_list(array: List) -> int:
        random_index = random.randint(0, len(array) - 1)
        return random_index
    
    @staticmethod   # just for example, don't use in  main ver
    async def analyze_voice_message(message: Message) -> str:
        file = await message.bot.get_file(message.voice.file_id)
        downloaded_file = await message.bot.download_file(file.file_path)
        temp_path = f"temp_voice_{message.from_user.id}"

        with open(temp_path, 'wb') as f:
            f.write(downloaded_file.getvalue())

        model = WhisperModel("large", device="cpu", compute_type="int8")
        segments, info = model.transcribe(temp_path, language="ru")

        text = " ".join([segment.text for segment in segments])

        duration = message.voice.duration

        speed = SpeechAnalyzer.analyze_speech_rate(text, duration)
        density = SpeechAnalyzer.analyze_speech_density(text, duration)
        emotion = SpeechAnalyzer.analyze_emotional_indicators(text, speed["wpm"])
        complexity = SpeechAnalyzer.analyze_complexity(text, speed["wpm"])

        report = f"""
        Распознанный текст:\n
        {text}\n\n
    <b>📊 Анализ голосового сообщения</b>

    ⏱️ <b>Длительность:</b> {duration} сек
    📝 <b>Длина текста:</b> {speed['chars']} символов, {speed['words']} слов

    <b>🗣️ Скорость речи:</b>
    • {speed['status']}
    • {speed['wpm']} слов в минуту

    <b>🎤 Плотность речи:</b>
    • {density['pause_style']}
    • Плотность: {density['speech_density']}%
    • Средняя длина слова: {density['avg_word_length']} симв.

    <b>😊 Эмоциональная окраска:</b>
    • {emotion['inferred_emotion']}
    • Восклицаний: {emotion['excitement_marks']}, вопросов: {emotion['questions']}

    <b>📚 Лексический анализ:</b>
    • {complexity['vocabulary_level']}
    • {complexity['complexity']}
    • Уникальных слов: {complexity['unique_words']} из {speed['words']}
    • Длинных слов (&gt;6 букв): {complexity['long_words_ratio']}%
        """

        os.remove(temp_path)
        return report
