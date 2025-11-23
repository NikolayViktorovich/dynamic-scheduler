"""Сервис для генерации резюме студента"""

from sqlalchemy.orm import Session

from app.models import (
    Minor,
    MinorSkill,
    Skill,
    Specialization,
    StudentCourse,
    StudentSkill,
    User,
    UserMinor,
)
from app.models.student_course import CourseStatus
from app.schemas.resume import (
    ResumeEducation,
    ResumeMinor,
    ResumePersonalInfo,
    ResumeResponse,
    ResumeSkill,
)


class ResumeService:
    """Сервис генерации резюме навыков студента"""

    @staticmethod
    def generate_resume(db: Session, user: User) -> ResumeResponse:
        """
        Генерирует полное резюме студента.

        Включает:
        - личную информацию
        - все навыки (из основной специальности и всех майнеров, включая архивные)
        - информацию о майнерах (текущие и завершённые)
        - образование и статистику
        """
        # Личная информация
        specialization_name = None
        if user.specialization_id:
            spec = (
                db.query(Specialization)
                .filter(Specialization.id == user.specialization_id)
                .first()
            )
            if spec:
                specialization_name = spec.name

        personal = ResumePersonalInfo(
            name=user.full_name, email=user.email, specialization=specialization_name
        )

        # Получаем все навыки студента
        student_skills = (
            db.query(StudentSkill, Skill)
            .join(Skill, StudentSkill.skill_id == Skill.id)
            .filter(StudentSkill.student_id == user.id)
            .all()
        )

        # Группируем навыки по источнику (core/orbit)
        skills = []
        for ss, skill in student_skills:
            # Определяем источник навыка
            source = "core"
            acquired_from = specialization_name

            # Если навык был получен из майнера, отмечаем это
            if ss.acquired_from and "minor_" in ss.acquired_from:
                source = "orbit"
                # Можно извлечь название майнера из acquired_from
                acquired_from = ss.acquired_from

            skills.append(
                ResumeSkill(
                    name=skill.name,
                    level=ss.level,
                    source=source,
                    acquired_from=acquired_from,
                )
            )

        # Получаем информацию о майнерах студента (текущие и завершённые)
        user_minors_data = (
            db.query(UserMinor, Minor)
            .join(Minor, UserMinor.minor_id == Minor.id)
            .filter(
                UserMinor.user_id == user.id,
                UserMinor.status.in_(["selected", "completed"]),
            )
            .all()
        )

        minors = []
        for um, minor in user_minors_data:
            # Получаем навыки, которые даёт этот майнер
            minor_skills = (
                db.query(MinorSkill, Skill)
                .join(Skill, MinorSkill.skill_id == Skill.id)
                .filter(MinorSkill.minor_id == minor.id)
                .all()
            )

            skills_gained = [skill.name for _, skill in minor_skills]

            minors.append(
                ResumeMinor(
                    minor_name=minor.name, status=um.status, skills_gained=skills_gained
                )
            )

        # Статистика образования
        completed_courses = (
            db.query(StudentCourse)
            .filter(
                StudentCourse.student_id == user.id,
                StudentCourse.status == CourseStatus.COMPLETED,
            )
            .all()
        )

        # Подсчёт кредитов (если есть информация в связанных курсах)
        total_credits = 0
        for sc in completed_courses:
            if sc.course and sc.course.credits:
                total_credits += sc.course.credits

        education = ResumeEducation(
            completed_courses=len(completed_courses),
            total_credits=total_credits,
            average_grade=None,  # Можно добавить, если есть оценки
        )

        # Достижения (можно генерировать на основе данных)
        achievements = []
        if len(minors) > 0:
            achievements.append(f"Освоено {len(minors)} дополнительных направлений")
        if len(skills) >= 10:
            achievements.append(f"Освоено {len(skills)} навыков")
        if len(completed_courses) >= 20:
            achievements.append("Пройдено более 20 курсов")

        return ResumeResponse(
            personal=personal,
            skills=skills,
            minors=minors,
            education=education,
            achievements=achievements,
        )

    @staticmethod
    def update_skills_from_minor(db: Session, user: User, minor_id: int):
        """
        Обновляет навыки студента при завершении курсов из майнера.

        Эта функция вызывается, когда студент завершает курс в рамках майнера,
        чтобы обновить StudentSkill с пометкой источника.
        """
        # Получаем навыки майнера
        minor = db.query(Minor).filter(Minor.id == minor_id).first()
        if not minor:
            return

        minor_skills = (
            db.query(MinorSkill).filter(MinorSkill.minor_id == minor_id).all()
        )

        # Для каждого навыка майнера обновляем/создаём запись в StudentSkill
        for ms in minor_skills:
            student_skill = (
                db.query(StudentSkill)
                .filter(
                    StudentSkill.student_id == user.id,
                    StudentSkill.skill_id == ms.skill_id,
                )
                .first()
            )

            if student_skill:
                # Обновляем уровень (берём максимум)
                if ms.required_level > student_skill.level:
                    student_skill.level = ms.required_level
                # Обновляем источник
                if (
                    not student_skill.acquired_from
                    or "core" in student_skill.acquired_from
                ):
                    student_skill.acquired_from = f"minor_{minor.name}"
                db.add(student_skill)
            else:
                # Создаём новую запись
                new_skill = StudentSkill(
                    student_id=user.id,
                    skill_id=ms.skill_id,
                    level=ms.required_level,
                    acquired_from=f"minor_{minor.name}",
                )
                db.add(new_skill)

        db.commit()
