class SpeechAnalyzer:
    @staticmethod
    def analyze_speech_rate(text: str, duration_seconds: float) -> dict[str]:
        words_count = len(text.split())

        chars_count = len(text)
        wpm = (words_count / duration_seconds) * 60
        cps = chars_count / duration_seconds

        if wpm < 100:
            speed_status = "Медленно (спокойная речь)"
        elif wpm < 150:
            speed_status = "Нормально (разговорный темп)"
        elif wpm < 180:
            speed_status = "Быстро (оживленная беседа)"
        else:
            speed_status = "Очень быстро (тараторка)"

        return {
            "wpm": round(wpm, 1),
            "cps": round(cps, 2),
            "words": words_count,
            "chars": chars_count,
            "status": speed_status
        }

    @staticmethod
    def analyze_speech_density(text: str, duration_seconds: float) -> dict[str]:
        words = text.split()
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0

        estimated_speech_time = len(text) / 15
        coef = (estimated_speech_time / duration_seconds) * 100
        speech_density = min(100, coef)

        if speech_density > 80:
            pause_style = "<Без пауз (монолог / тараторка)"
        elif speech_density > 60:
            pause_style = "Нормальные паузы"
        elif speech_density > 40:
            pause_style = "Много пауз"
        else:
            pause_style = "Очень медленно с длинными паузами"

        return {
            "avg_word_length": round(avg_word_length, 1),
            "speech_density": round(speech_density, 1),
            "pause_style": pause_style
        }

    @staticmethod
    def analyze_emotional_indicators(text: str, wpm: float):
        # Длина предложений (энергичность)
        sentences = text.split('.') + text.split('!') + text.split('?')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

        # Восклицательные/вопросительные знаки
        excitement = text.count('!')
        questions = text.count('?')

        # Капс (громкость)
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0

        # Оценка эмоционального состояния
        if wpm > 170 and excitement > 2:
            emotion = "😄 Возбуждён/воодушевлён"
        elif wpm < 90 and avg_sentence_length < 8:
            emotion = "😔 Грусть/усталость"
        elif questions > 3:
            emotion = "🤔 Задумчив/неуверен"
        elif caps_ratio > 0.3:
            emotion = "😠 Раздражён/кричит"
        elif 110 < wpm < 140:
            emotion = "😌 Спокоен/уверен"
        else:
            emotion = "😐 Нейтрально"

        return {
            "avg_sentence_length": round(avg_sentence_length, 1),
            "excitement_marks": excitement,
            "questions": questions,
            "caps_ratio": round(caps_ratio * 100, 1),
            "inferred_emotion": emotion
        }

    @staticmethod
    def analyze_complexity(text: str, wpm: float):
        words = text.lower().split()

        # Уникальные слова (богатство словаря)
        unique_words = set(words)
        lexical_diversity = len(unique_words) / len(words) if words else 0

        # Длинные слова (>6 символов) - показатель сложности
        long_words = [w for w in words if len(w) > 6]
        long_words_ratio = len(long_words) / len(words) if words else 0

        # Средняя длина слова (уже есть)
        avg_len = sum(len(w) for w in words) / len(words) if words else 0

        # Оценка
        if lexical_diversity > 0.7:
            vocabulary = "📚 Богатый словарный запас"
        elif lexical_diversity > 0.5:
            vocabulary = "📖 Нормальный словарь"
        else:
            vocabulary = "📝 Простая речь (повторы)"

        if long_words_ratio > 0.3:
            complexity = "🎓 Сложная лексика (термины/научный стиль)"
        elif long_words_ratio > 0.15:
            complexity = "📘 Средняя сложность"
        else:
            complexity = "💬 Простой язык (разговорный)"

        return {
            "unique_words": len(unique_words),
            "lexical_diversity": round(lexical_diversity, 2),
            "long_words_ratio": round(long_words_ratio * 100, 1),
            "vocabulary_level": vocabulary,
            "complexity": complexity
        }

    @staticmethod
    def predict_accent_hints(text: str):
        # Характерные маркеры для русского языка
        accent_markers = {
            "оканье": text.count("о") / len(text) if text else 0,
            "аканье": text.count("а") / len(text) if text else 0,
            "ерь": text.count("ь") + text.count("ъ"),
            "повторы_звуков": len([w for w in text.split() if len(set(w)) < len(w) * 0.7])
        }

        # Простая эвристика
        hints = []
        if accent_markers["оканье"] > 0.12:
            hints.append("Возможно северный говор (оканье)")
        if accent_markers["повторы_звуков"] > 5:
            hints.append("Возможно заикание/запинки")

        return hints

