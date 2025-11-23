from typing import List, Optional
import random
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import (
    User, Course, Specialization, Skill, StudentCourse,
    StudentSkill, CourseSkill
)
from app.models.student_course import CourseStatus
from app.schemas.recommendation import (
    RecommendationsResponse, RecommendedCourse,
    WhatIfResponse, WhatIfRequest, WhatIfSkillComparison
)


class RecommendationService:
    """Сервис рекомендаций курсов"""
    
    @staticmethod
    def get_recommendations(
        db: Session,
        user: User,
        limit: int = 5
    ) -> RecommendationsResponse:
        """
        Получить рекомендации курсов (заглушка на первом этапе).
        Возвращает случайные курсы, которые восполняют дефицит навыков.
        """
        # Получаем специальность студента
        if not user.specialization_id:
            return RecommendationsResponse(
                specialization_id=None,
                specialization_name=None,
                recommended_courses=[]
            )
        
        specialization = db.query(Specialization).filter(
            Specialization.id == user.specialization_id
        ).first()
        
        if not specialization or not specialization.required_skills:
            return RecommendationsResponse(
                specialization_id=specialization.id if specialization else None,
                specialization_name=specialization.name if specialization else None,
                recommended_courses=[]
            )
        
        # Получаем текущие навыки студента
        student_skills = db.query(StudentSkill).filter(
            StudentSkill.student_id == user.id
        ).all()
        current_skills_dict = {ss.skill_id: ss.level for ss in student_skills}
        
        # Определяем навыки с дефицитом
        deficit_skills = []
        for skill_id_str, required_level in specialization.required_skills.items():
            skill_id = int(skill_id_str)
            current_level = current_skills_dict.get(skill_id, 0)
            if current_level < required_level:
                skill = db.query(Skill).filter(Skill.id == skill_id).first()
                if skill:
                    deficit_skills.append({
                        "id": skill_id,
                        "name": skill.name,
                        "deficit": required_level - current_level
                    })
        
        # Получаем курсы специальности, которые студент еще не прошел
        completed_course_ids = [
            sc.course_id for sc in db.query(StudentCourse).filter(
                and_(
                    StudentCourse.student_id == user.id,
                    StudentCourse.status == CourseStatus.COMPLETED
                )
            ).all()
        ]
        
        available_courses = db.query(Course).filter(
            and_(
                Course.specialization_id == user.specialization_id,
                Course.id.notin_(completed_course_ids) if completed_course_ids else True
            )
        ).all()
        
        # Заглушка: выбираем случайные курсы
        recommendations = []
        selected_courses = random.sample(
            available_courses,
            min(limit, len(available_courses))
        )
        
        for i, course in enumerate(selected_courses):
            # Получаем навыки, которые дает курс
            course_skills = db.query(CourseSkill, Skill).join(
                Skill, CourseSkill.skill_id == Skill.id
            ).filter(CourseSkill.course_id == course.id).all()
            
            missing_skills = []
            for cs, skill in course_skills:
                if skill.id in [ds["id"] for ds in deficit_skills]:
                    missing_skills.append(skill.name)
            
            reason = "Восполняет дефицит навыков" if missing_skills else "Рекомендуемый курс для вашей специальности"
            priority = 1 if missing_skills else 2
            
            recommendations.append(RecommendedCourse(
                course_id=course.id,
                course_name=course.name,
                reason=reason,
                priority=priority,
                missing_skills=missing_skills[:3]  # Показываем до 3 навыков
            ))
        
        # Сортируем по приоритету
        recommendations.sort(key=lambda x: x.priority)
        
        return RecommendationsResponse(
            specialization_id=specialization.id,
            specialization_name=specialization.name,
            recommended_courses=recommendations
        )
    
    @staticmethod
    def what_if_analysis(
        db: Session,
        user: User,
        request: WhatIfRequest
    ) -> Optional[WhatIfResponse]:
        """Моделирование смены специальности"""
        # Получаем новую специальность
        new_specialization = db.query(Specialization).filter(
            Specialization.id == request.new_specialization_id
        ).first()
        
        if not new_specialization:
            return None
        
        # Получаем текущую специальность (если есть)
        current_specialization = None
        if user.specialization_id:
            current_specialization = db.query(Specialization).filter(
                Specialization.id == user.specialization_id
            ).first()
        
        # Получаем текущие навыки студента
        student_skills = db.query(StudentSkill).filter(
            StudentSkill.student_id == user.id
        ).all()
        current_skills_dict = {ss.skill_id: ss.level for ss in student_skills}
        
        # Анализируем соответствие навыков
        skills_comparison = []
        
        # Старые требования
        old_required = {}
        if current_specialization and current_specialization.required_skills:
            old_required = {
                int(k): v for k, v in current_specialization.required_skills.items()
            }
        
        # Новые требования
        new_required = {}
        if new_specialization.required_skills:
            new_required = {
                int(k): v for k, v in new_specialization.required_skills.items()
            }
        
        # Объединяем все навыки
        all_skill_ids = set(list(old_required.keys()) + list(new_required.keys()))
        
        new_satisfied = 0
        for skill_id in all_skill_ids:
            skill = db.query(Skill).filter(Skill.id == skill_id).first()
            if not skill:
                continue
            
            current_level = current_skills_dict.get(skill_id, 0)
            old_req = old_required.get(skill_id, 0)
            new_req = new_required.get(skill_id, 0)
            
            will_satisfy = current_level >= new_req if new_req > 0 else True
            if will_satisfy and new_req > 0:
                new_satisfied += 1
            
            skills_comparison.append(WhatIfSkillComparison(
                skill_id=skill.id,
                skill_name=skill.name,
                current_level=current_level,
                old_required_level=old_req,
                new_required_level=new_req,
                will_satisfy=will_satisfy
            ))
        
        # Расчет процента завершения
        current_completion = 0.0
        if current_specialization and old_required:
            current_satisfied = sum(
                1 for skill_id in old_required.keys()
                if current_skills_dict.get(skill_id, 0) >= old_required[skill_id]
            )
            current_completion = (current_satisfied / len(old_required) * 100) if old_required else 0
        
        new_completion = (new_satisfied / len(new_required) * 100) if new_required else 0
        
        # Количество пройденных курсов
        completed_courses = db.query(StudentCourse).filter(
            and_(
                StudentCourse.student_id == user.id,
                StudentCourse.status == CourseStatus.COMPLETED
            )
        ).all()
        
        # Курсы, которые останутся актуальными (упрощенная логика)
        courses_to_keep = len(completed_courses)  # Все курсы сохраняются
        
        return WhatIfResponse(
            current_specialization_id=user.specialization_id,
            current_specialization_name=current_specialization.name if current_specialization else None,
            new_specialization_id=new_specialization.id,
            new_specialization_name=new_specialization.name,
            current_completion_percentage=round(current_completion, 2),
            new_completion_percentage=round(new_completion, 2),
            skills_comparison=skills_comparison,
            courses_to_keep=courses_to_keep,
            total_completed_courses=len(completed_courses)
        )

