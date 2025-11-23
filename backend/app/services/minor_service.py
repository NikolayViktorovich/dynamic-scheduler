"""Сервис для работы с майнерами и рекомендациями"""

from collections import defaultdict
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import (
    Course,
    CourseTag,
    Minor,
    MinorCourse,
    MinorSkill,
    Skill,
    StudentCourse,
    User,
    UserMinor,
)
from app.models.student_course import CourseStatus
from app.schemas.minor import (
    CourseTagSimple,
    CourseWithTags,
    MinorDetailed,
    MinorRecommendation,
    MinorRecommendationsResponse,
    MinorSkillDetailed,
)


class MinorRecommendationService:
    """Сервис рекомендаций майнеров по дифференцированным тегам"""

    @staticmethod
    def calculate_student_tag_profile(db: Session, user: User) -> Dict[str, float]:
        """
        Строит профиль студента по тегам на основе:
        - основной специальности
        - уже пройденных курсов

        Возвращает словарь {tag_name: суммарный_вес}
        """
        tag_profile = defaultdict(float)

        # Получаем все пройденные курсы студента
        completed_courses = (
            db.query(StudentCourse)
            .filter(
                StudentCourse.student_id == user.id,
                StudentCourse.status == CourseStatus.COMPLETED,
            )
            .all()
        )

        completed_course_ids = [sc.course_id for sc in completed_courses]

        if completed_course_ids:
            # Собираем теги из всех пройденных курсов
            course_tags = (
                db.query(CourseTag)
                .filter(CourseTag.course_id.in_(completed_course_ids))
                .all()
            )

            for ct in course_tags:
                tag_profile[ct.tag_name] += ct.weight

        # Можно добавить теги из основной специальности, если нужно
        # (для MVP пока просто используем пройденные курсы)

        return dict(tag_profile)

    @staticmethod
    def calculate_minor_tag_profile(db: Session, minor: Minor) -> Dict[str, float]:
        """
        Строит профиль майнера по тегам его курсов.

        Возвращает словарь {tag_name: суммарный_вес}
        """
        tag_profile = defaultdict(float)

        # Получаем курсы майнера
        minor_courses = (
            db.query(MinorCourse).filter(MinorCourse.minor_id == minor.id).all()
        )

        minor_course_ids = [mc.course_id for mc in minor_courses]

        if minor_course_ids:
            # Собираем теги из всех курсов майнера
            course_tags = (
                db.query(CourseTag)
                .filter(CourseTag.course_id.in_(minor_course_ids))
                .all()
            )

            for ct in course_tags:
                tag_profile[ct.tag_name] += ct.weight

        return dict(tag_profile)

    @staticmethod
    def calculate_similarity_score(
        student_profile: Dict[str, float], minor_profile: Dict[str, float]
    ) -> tuple[float, List[str]]:
        """
        Вычисляет similarity score между студентом и майнером.

        Формула: для каждого тега берём min(student_weight, minor_weight),
        суммируем по всем общим тегам.

        Возвращает: (score, список_совпадающих_тегов)
        """
        score = 0.0
        matching_tags = []

        # Находим общие теги
        common_tags = set(student_profile.keys()) & set(minor_profile.keys())

        for tag in common_tags:
            # Берём минимальный вес (насколько тег представлен у обоих)
            contribution = min(student_profile[tag], minor_profile[tag])
            score += contribution
            matching_tags.append(tag)

        # Можно добавить небольшой бонус за теги майнера, которых нет у студента
        # (это "новые знания", что тоже может быть интересно)
        new_tags = set(minor_profile.keys()) - set(student_profile.keys())
        for tag in new_tags:
            # Небольшой бонус (например, 0.3 от веса тега в майнере)
            score += 0.3 * minor_profile[tag]

        return score, matching_tags

    @staticmethod
    def get_recommendations(
        db: Session, user: User, limit: int = 5
    ) -> MinorRecommendationsResponse:
        """
        Получить рекомендации майнеров для студента.

        Логика:
        1. Строим профиль студента по тегам (из пройденных курсов)
        2. Для каждого майнера строим профиль по тегам
        3. Считаем similarity score
        4. Сортируем и возвращаем топ N
        """
        # Профиль студента
        student_profile = MinorRecommendationService.calculate_student_tag_profile(
            db, user
        )

        # Получаем все активные майнеры
        all_minors = db.query(Minor).filter(Minor.is_active == True).all()

        # Исключаем майнеры, которые студент уже выбрал (кроме archived)
        user_minor_ids = [
            um.minor_id
            for um in db.query(UserMinor)
            .filter(
                UserMinor.user_id == user.id,
                UserMinor.status.in_(["selected", "completed"]),
            )
            .all()
        ]

        available_minors = [m for m in all_minors if m.id not in user_minor_ids]

        # Считаем score для каждого майнера
        recommendations = []

        for minor in available_minors:
            minor_profile = MinorRecommendationService.calculate_minor_tag_profile(
                db, minor
            )
            score, matching_tags = (
                MinorRecommendationService.calculate_similarity_score(
                    student_profile, minor_profile
                )
            )

            # Формируем причину рекомендации
            if matching_tags:
                reason = f"Совпадение по тегам: {', '.join(matching_tags[:3])}"
                if len(matching_tags) > 3:
                    reason += f" и ещё {len(matching_tags) - 3}"
            else:
                reason = "Новое направление для расширения навыков"

            recommendations.append(
                MinorRecommendation(
                    minor_id=minor.id,
                    minor_name=minor.name,
                    description=minor.description,
                    minor_type=minor.minor_type,
                    score=round(score, 2),
                    matching_tags=matching_tags,
                    reason=reason,
                )
            )

        # Сортируем по score (по убыванию)
        recommendations.sort(key=lambda x: x.score, reverse=True)

        # Возвращаем топ N
        top_recommendations = recommendations[:limit]

        return MinorRecommendationsResponse(
            recommendations=top_recommendations, total_count=len(recommendations)
        )

    @staticmethod
    def get_similar_minors_on_change(
        db: Session, user: User, current_minor_id: int, limit: int = 3
    ) -> MinorRecommendationsResponse:
        """
        Рекомендация похожих майнеров при смене текущего майнера.

        Логика похожа на обычные рекомендации, но:
        - учитываем теги ТЕКУЩЕГО майнера (что студент хотел изучать)
        - плюс уже пройденные курсы
        """
        # Профиль студента (из пройденных курсов)
        student_profile = MinorRecommendationService.calculate_student_tag_profile(
            db, user
        )

        # Профиль текущего майнера
        current_minor = db.query(Minor).filter(Minor.id == current_minor_id).first()
        if current_minor:
            current_minor_profile = (
                MinorRecommendationService.calculate_minor_tag_profile(
                    db, current_minor
                )
            )
            # Объединяем профили (студент + текущий майнер)
            combined_profile = defaultdict(float, student_profile)
            for tag, weight in current_minor_profile.items():
                combined_profile[tag] += weight * 0.5  # Меньший вес для "намерения"
            student_profile = dict(combined_profile)

        # Получаем все активные майнеры (кроме текущего)
        all_minors = (
            db.query(Minor)
            .filter(Minor.is_active == True, Minor.id != current_minor_id)
            .all()
        )

        # Исключаем уже выбранные майнеры
        user_minor_ids = [
            um.minor_id
            for um in db.query(UserMinor)
            .filter(
                UserMinor.user_id == user.id,
                UserMinor.status.in_(["selected", "completed"]),
            )
            .all()
        ]
        available_minors = [m for m in all_minors if m.id not in user_minor_ids]

        # Считаем score
        recommendations = []
        for minor in available_minors:
            minor_profile = MinorRecommendationService.calculate_minor_tag_profile(
                db, minor
            )
            score, matching_tags = (
                MinorRecommendationService.calculate_similarity_score(
                    student_profile, minor_profile
                )
            )

            reason = (
                f"Похожий по направлению: {', '.join(matching_tags[:2])}"
                if matching_tags
                else "Альтернативное направление"
            )

            recommendations.append(
                MinorRecommendation(
                    minor_id=minor.id,
                    minor_name=minor.name,
                    description=minor.description,
                    minor_type=minor.minor_type,
                    score=round(score, 2),
                    matching_tags=matching_tags,
                    reason=reason,
                )
            )

        recommendations.sort(key=lambda x: x.score, reverse=True)

        return MinorRecommendationsResponse(
            recommendations=recommendations[:limit], total_count=len(recommendations)
        )

    @staticmethod
    def get_minor_detailed(db: Session, minor_id: int) -> Optional[MinorDetailed]:
        """Получить детальную информацию о майнере"""
        minor = db.query(Minor).filter(Minor.id == minor_id).first()
        if not minor:
            return None

        # Получаем целевые навыки
        minor_skills = (
            db.query(MinorSkill, Skill)
            .join(Skill, MinorSkill.skill_id == Skill.id)
            .filter(MinorSkill.minor_id == minor_id)
            .all()
        )

        target_skills = [
            MinorSkillDetailed(
                skill_id=ms.skill_id,
                skill_name=skill.name,
                required_level=ms.required_level,
            )
            for ms, skill in minor_skills
        ]

        # Получаем курсы майнера с тегами
        minor_courses = (
            db.query(MinorCourse, Course)
            .join(Course, MinorCourse.course_id == Course.id)
            .filter(MinorCourse.minor_id == minor_id)
            .all()
        )

        courses = []
        aggregated_tags = defaultdict(float)

        for mc, course in minor_courses:
            # Теги курса
            tags = db.query(CourseTag).filter(CourseTag.course_id == course.id).all()

            # Агрегируем теги для майнера
            for tag in tags:
                aggregated_tags[tag.tag_name] += tag.weight

            courses.append(
                CourseWithTags(
                    id=course.id,
                    name=course.name,
                    description=course.description,
                    credits=course.credits,
                    semester=course.semester,
                    tags=[
                        CourseTagSimple(tag_name=tag.tag_name, weight=tag.weight)
                        for tag in tags
                    ],
                )
            )

        return MinorDetailed(
            id=minor.id,
            name=minor.name,
            description=minor.description,
            minor_type=minor.minor_type,
            is_active=minor.is_active,
            target_skills=target_skills,
            courses=courses,
            aggregated_tags=dict(aggregated_tags),
        )
