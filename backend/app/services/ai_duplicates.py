# app/services/ai_duplicates.py
from typing import List, Tuple
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.models.problem import Problem


class DuplicateDetector:
    """Детектор дубликатов проблем на основе TF-IDF и косинусного сходства"""

    def __init__(self, similarity_threshold: float = 0.7):
        """
        Args:
            similarity_threshold: Порог сходства (0-1). Выше = более строгое совпадение
        """
        self.similarity_threshold = similarity_threshold
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,  # Можно добавить русские стоп-слова
            ngram_range=(1, 2),  # Униграммы и биграммы
            min_df=1,
        )

    def _prepare_text(self, problem: Problem) -> str:
        """Подготовить текст проблемы для анализа"""
        parts = [
            problem.title,
            problem.description or "",
            problem.problem_type or "",
            problem.address or "",
        ]
        # Добавляем теги если есть
        if problem.tags:
            parts.extend(problem.tags)

        return " ".join(parts).lower()

    def find_duplicates(
        self,
        db: Session,
        problem: Problem,
        city: str = None,
        limit: int = 10,
    ) -> List[Tuple[Problem, float]]:
        """
        Найти похожие проблемы.

        Args:
            db: Сессия БД
            problem: Проблема для поиска дубликатов
            city: Фильтр по городу (опционально)
            limit: Максимальное количество результатов

        Returns:
            Список кортежей (проблема, сходство) отсортированный по убыванию сходства
        """
        # Получаем все актуальные проблемы (кроме текущей)
        query = db.query(Problem).filter(
            Problem.is_current == True,
            Problem.entity_id != problem.entity_id,
        )

        if city:
            query = query.filter(Problem.city == city)

        candidates = query.all()

        if not candidates:
            return []

        # Подготавливаем тексты
        target_text = self._prepare_text(problem)
        candidate_texts = [self._prepare_text(p) for p in candidates]

        # Вычисляем TF-IDF векторы
        all_texts = [target_text] + candidate_texts
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        except ValueError:
            # Если не удалось векторизовать (например, пустые тексты)
            return []

        # Вычисляем косинусное сходство
        target_vector = tfidf_matrix[0:1]
        candidate_vectors = tfidf_matrix[1:]
        similarities = cosine_similarity(target_vector, candidate_vectors)[0]

        # Фильтруем по порогу и сортируем
        results = []
        for candidate, similarity in zip(candidates, similarities):
            if similarity >= self.similarity_threshold:
                results.append((candidate, float(similarity)))

        # Сортируем по убыванию сходства
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]

    def find_similar_by_location(
        self,
        db: Session,
        problem: Problem,
        radius_meters: float = 100,
        limit: int = 10,
    ) -> List[Tuple[Problem, float]]:
        """
        Найти проблемы рядом (по геолокации).

        Args:
            db: Сессия БД
            problem: Проблема для поиска
            radius_meters: Радиус поиска в метрах
            limit: Максимальное количество результатов

        Returns:
            Список кортежей (проблема, расстояние в метрах)
        """
        from sqlalchemy import func
        from geoalchemy2.functions import ST_Distance, ST_DWithin

        if problem.location is None:
            return []

        # Поиск проблем в радиусе
        query = (
            db.query(
                Problem,
                func.ST_Distance(
                    Problem.location,
                    problem.location,
                    True  # use_spheroid=True для точности
                ).label("distance")
            )
            .filter(
                Problem.is_current == True,
                Problem.entity_id != problem.entity_id,
                ST_DWithin(Problem.location, problem.location, radius_meters, True)
            )
            .order_by("distance")
            .limit(limit)
        )

        results = []
        for prob, distance in query.all():
            results.append((prob, float(distance)))

        return results

    def find_combined_duplicates(
        self,
        db: Session,
        problem: Problem,
        text_weight: float = 0.7,
        location_weight: float = 0.3,
        limit: int = 10,
    ) -> List[Tuple[Problem, float]]:
        """
        Комбинированный поиск дубликатов (текст + геолокация).

        Args:
            db: Сессия БД
            problem: Проблема для поиска
            text_weight: Вес текстового сходства (0-1)
            location_weight: Вес геолокации (0-1)
            limit: Максимальное количество результатов

        Returns:
            Список кортежей (проблема, комбинированный score)
        """
        # Находим текстовые дубликаты
        text_duplicates = self.find_duplicates(
            db, problem, city=problem.city, limit=50
        )
        text_scores = {p.entity_id: score for p, score in text_duplicates}

        # Находим геолокационные дубликаты
        location_duplicates = self.find_similar_by_location(
            db, problem, radius_meters=500, limit=50
        )

        # Нормализуем расстояния в score (0-1)
        if location_duplicates:
            max_distance = max(dist for _, dist in location_duplicates)
            location_scores = {
                p.entity_id: 1 - (dist / max_distance if max_distance > 0 else 0)
                for p, dist in location_duplicates
            }
        else:
            location_scores = {}

        # Комбинируем scores
        all_entity_ids = set(text_scores.keys()) | set(location_scores.keys())
        combined_results = []

        for entity_id in all_entity_ids:
            text_score = text_scores.get(entity_id, 0)
            location_score = location_scores.get(entity_id, 0)

            combined_score = (
                text_score * text_weight +
                location_score * location_weight
            )

            # Получаем проблему
            prob = db.query(Problem).filter_by(
                entity_id=entity_id, is_current=True
            ).first()

            if prob:
                combined_results.append((prob, combined_score))

        # Сортируем и возвращаем топ
        combined_results.sort(key=lambda x: x[1], reverse=True)
        return combined_results[:limit]
