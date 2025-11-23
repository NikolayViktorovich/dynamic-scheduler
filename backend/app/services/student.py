from typing import Any, Dict

from sqlalchemy.orm import Session

from app.models import Course, Skill, Specialization, StudentCourse, StudentSkill, User
from app.models.student_course import CourseStatus
from app.schemas.resume import (
    ResumeEducation,
    ResumePersonalInfo,
    ResumeResponse,
    ResumeSkill,
)


class StudentService:
    """Сервис для работы с профилем и прогрессом студента"""

    @staticmethod
    def get_student_courses(db: Session, user: User) -> Dict[str, Any]:
        """
        Получить курсы студента, разделенные по статусам:
        - completed: завершенные курсы
        - in_progress: текущие курсы
        - available: доступные для записи курсы
        """
        # Получаем все записи студента на курсы
        student_courses = (
            db.query(StudentCourse, Course)
            .join(Course, StudentCourse.course_id == Course.id)
            .filter(StudentCourse.student_id == user.id)
            .all()
        )

        # Разделяем по статусам
        completed = []
        in_progress = []
        enrolled_course_ids = set()

        for sc, course in student_courses:
            enrolled_course_ids.add(course.id)

            course_data = {
                "id": course.id,
                "name": course.name,
                "description": course.description,
                "credits": course.credits,
                "semester": course.semester,
                "difficulty_level": sc.difficulty_level,
                "enrolled_at": sc.enrolled_at.isoformat() if sc.enrolled_at else None,
            }

            if sc.status == CourseStatus.COMPLETED:
                course_data["grade"] = sc.grade
                course_data["completed_at"] = (
                    sc.completed_at.isoformat() if sc.completed_at else None
                )
                completed.append(course_data)
            elif sc.status in [CourseStatus.ENROLLED, CourseStatus.IN_PROGRESS]:
                in_progress.append(course_data)

        # Получаем доступные курсы (на которые студент еще не записан)
        available_courses = (
            db.query(Course).filter(~Course.id.in_(enrolled_course_ids)).all()
        )

        # Если у студента есть специальность, фильтруем курсы
        if user.specialization_id:
            available_courses = [
                c
                for c in available_courses
                if c.specialization_id == user.specialization_id or c.is_elective
            ]

        available = []
        for course in available_courses:
            available.append(
                {
                    "id": course.id,
                    "name": course.name,
                    "description": course.description,
                    "credits": course.credits,
                    "semester": course.semester,
                    "is_elective": course.is_elective,
                }
            )

        return {
            "completed": completed,
            "in_progress": in_progress,
            "available": available,
        }

    @staticmethod
    def get_student_progress(db: Session, user: User) -> Dict[str, Any]:
        """
        Получить прогресс обучения студента:
        - Статистика по курсам
        - Статистика по навыкам
        - Процент завершения относительно специальности
        """
        # Статистика по курсам
        student_courses = (
            db.query(StudentCourse).filter(StudentCourse.student_id == user.id).all()
        )

        courses_stats = {
            "total_enrolled": len(student_courses),
            "completed": sum(
                1 for sc in student_courses if sc.status == CourseStatus.COMPLETED
            ),
            "in_progress": sum(
                1
                for sc in student_courses
                if sc.status in [CourseStatus.ENROLLED, CourseStatus.IN_PROGRESS]
            ),
            "dropped": sum(
                1 for sc in student_courses if sc.status == CourseStatus.DROPPED
            ),
        }

        # Средний балл
        completed_with_grades = [
            sc
            for sc in student_courses
            if sc.status == CourseStatus.COMPLETED and sc.grade
        ]
        if completed_with_grades:
            courses_stats["average_grade"] = sum(
                sc.grade for sc in completed_with_grades
            ) / len(completed_with_grades)
        else:
            courses_stats["average_grade"] = None

        # Статистика по навыкам
        student_skills = (
            db.query(StudentSkill).filter(StudentSkill.student_id == user.id).all()
        )

        skills_stats = {
            "acquired_skills": len(student_skills),
            "average_level": sum(ss.level for ss in student_skills)
            / len(student_skills)
            if student_skills
            else 0,
        }

        # Прогресс относительно специальности
        progress_percentage = 0.0
        specialization_name = None
        required_skills_count = 0
        satisfied_skills_count = 0

        if user.specialization_id:
            specialization = (
                db.query(Specialization)
                .filter(Specialization.id == user.specialization_id)
                .first()
            )

            if specialization:
                specialization_name = specialization.name

                # Если есть требуемые навыки
                if specialization.required_skills:
                    required_skills = specialization.required_skills
                    required_skills_count = len(required_skills)

                    # Проверяем, сколько навыков студент освоил
                    student_skills_dict = {
                        ss.skill_id: ss.level for ss in student_skills
                    }

                    for skill_id_str, required_level in required_skills.items():
                        skill_id = int(skill_id_str)
                        student_level = student_skills_dict.get(skill_id, 0)
                        if student_level >= required_level:
                            satisfied_skills_count += 1

                    if required_skills_count > 0:
                        progress_percentage = (
                            satisfied_skills_count / required_skills_count
                        ) * 100

        return {
            "courses": courses_stats,
            "skills": skills_stats,
            "specialization": {
                "name": specialization_name,
                "required_skills": required_skills_count,
                "satisfied_skills": satisfied_skills_count,
                "progress_percentage": round(progress_percentage, 2),
            },
            "total_credits_earned": sum(
                sc.course.credits or 0
                for sc in student_courses
                if sc.status == CourseStatus.COMPLETED and sc.course
            ),
        }

    @staticmethod
    def generate_resume(db: Session, user: User) -> ResumeResponse:
        """
        Генерация резюме студента на основе его обучения и достижений
        """
        # Получаем специальность студента
        specialization_name = None
        if user.specialization_id:
            specialization = (
                db.query(Specialization)
                .filter(Specialization.id == user.specialization_id)
                .first()
            )
            if specialization:
                specialization_name = specialization.name

        # Личная информация
        personal = ResumePersonalInfo(
            name=user.full_name,
            email=user.email,
            specialization=specialization_name,
        )

        # Получаем навыки студента
        student_skills = (
            db.query(StudentSkill, Skill)
            .join(Skill, StudentSkill.skill_id == Skill.id)
            .filter(StudentSkill.student_id == user.id)
            .all()
        )

        skills = [
            ResumeSkill(name=skill.name, level=student_skill.level)
            for student_skill, skill in student_skills
        ]

        # Сортируем навыки по уровню (от большего к меньшему)
        skills.sort(key=lambda x: x.level, reverse=True)

        # Получаем статистику по курсам
        student_courses = (
            db.query(StudentCourse)
            .join(Course, StudentCourse.course_id == Course.id)
            .filter(StudentCourse.student_id == user.id)
            .all()
        )

        # Подсчитываем завершенные курсы и кредиты
        completed_courses = [
            sc for sc in student_courses if sc.status == CourseStatus.COMPLETED
        ]
        completed_count = len(completed_courses)

        total_credits = sum(
            sc.course.credits or 0 for sc in completed_courses if sc.course
        )

        # Средний балл
        completed_with_grades = [sc for sc in completed_courses if sc.grade]
        average_grade = None
        if completed_with_grades:
            average_grade = round(
                sum(sc.grade for sc in completed_with_grades)
                / len(completed_with_grades),
                2,
            )

        education = ResumeEducation(
            completed_courses=completed_count,
            total_credits=total_credits,
            average_grade=average_grade,
        )

        # Генерация достижений
        achievements = []

        # Достижение: высокий средний балл
        if average_grade and average_grade >= 90:
            achievements.append(f"Отличная успеваемость: средний балл {average_grade}%")
        elif average_grade and average_grade >= 80:
            achievements.append(f"Хорошая успеваемость: средний балл {average_grade}%")

        # Достижение: завершенные курсы
        if completed_count >= 10:
            achievements.append(f"Завершено {completed_count} курсов")
        elif completed_count >= 5:
            achievements.append(f"Успешно завершено {completed_count} курсов")

        # Достижение: освоенные навыки
        if len(skills) >= 15:
            achievements.append(f"Освоено {len(skills)} профессиональных навыков")
        elif len(skills) >= 10:
            achievements.append(f"Освоено {len(skills)} технических навыков")
        elif len(skills) >= 5:
            achievements.append(f"Освоено {len(skills)} навыков")

        # Достижение: курсы с отличными оценками
        excellent_courses = [
            sc for sc in completed_courses if sc.grade and sc.grade >= 95
        ]
        if excellent_courses:
            # Получаем имена курсов
            excellent_course_names = []
            for sc in excellent_courses[:3]:  # Берем максимум 3 курса
                if sc.course:
                    excellent_course_names.append(sc.course.name)

            if len(excellent_course_names) == 1:
                achievements.append(
                    f"Отлично завершен курс '{excellent_course_names[0]}' с оценкой {excellent_courses[0].grade}%"
                )
            elif len(excellent_course_names) > 1:
                achievements.append(
                    f"Отлично завершено {len(excellent_courses)} курсов с оценкой 95%+"
                )

        # Достижение: продвинутые навыки
        advanced_skills = [s for s in skills if s.level >= 3]
        if advanced_skills:
            achievements.append(
                f"Владение продвинутыми навыками: {', '.join(s.name for s in advanced_skills[:5])}"
            )

        # Достижение: набранные кредиты
        if total_credits >= 50:
            achievements.append(f"Набрано {total_credits} учебных кредитов")
        elif total_credits >= 30:
            achievements.append(f"Набрано {total_credits} кредитов")

        # Прогресс по специальности
        if user.specialization_id and specialization:
            if specialization.required_skills:
                required_skills = specialization.required_skills
                student_skills_dict = {
                    ss.skill_id: ss.level for ss, _ in student_skills
                }

                satisfied_count = 0
                for skill_id_str, required_level in required_skills.items():
                    skill_id = int(skill_id_str)
                    student_level = student_skills_dict.get(skill_id, 0)
                    if student_level >= required_level:
                        satisfied_count += 1

                if satisfied_count == len(required_skills):
                    achievements.append(
                        f"Полностью освоена специальность '{specialization_name}'"
                    )
                elif satisfied_count >= len(required_skills) * 0.8:
                    achievements.append(
                        f"Почти завершена специальность '{specialization_name}' ({satisfied_count}/{len(required_skills)} навыков)"
                    )

        # Если достижений нет, добавляем мотивационное сообщение
        if not achievements:
            if completed_count > 0:
                achievements.append("Начат путь обучения")
            else:
                achievements.append("Готов к новым знаниям и достижениям")

        return ResumeResponse(
            personal=personal,
            skills=skills,
            education=education,
            achievements=achievements,
        )
