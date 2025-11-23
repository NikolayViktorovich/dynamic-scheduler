from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models import Specialization, Course, Skill, User, StudentSkill
from app.schemas.specialization import (
    SpecializationCreate, SpecializationUpdate,
    RoadmapResponse, CourseInRoadmap, SkillsMatrixResponse, SkillRequirement
)


class SpecializationService:
    """Сервис для работы со специальностями"""
    
    @staticmethod
    def get_all(db: Session) -> List[Specialization]:
        """Получить все специальности"""
        return db.query(Specialization).all()
    
    @staticmethod
    def get_by_id(db: Session, specialization_id: int) -> Optional[Specialization]:
        """Получить специальность по ID"""
        return db.query(Specialization).filter(Specialization.id == specialization_id).first()
    
    @staticmethod
    def create(db: Session, data: SpecializationCreate) -> Specialization:
        """Создать новую специальность"""
        specialization = Specialization(**data.model_dump())
        db.add(specialization)
        db.commit()
        db.refresh(specialization)
        return specialization
    
    @staticmethod
    def get_roadmap(db: Session, specialization_id: int) -> Optional[RoadmapResponse]:
        """Получить roadmap специальности"""
        specialization = db.query(Specialization).filter(
            Specialization.id == specialization_id
        ).first()
        
        if not specialization:
            return None
        
        # Получаем все курсы специальности
        courses = db.query(Course).filter(
            Course.specialization_id == specialization_id
        ).order_by(Course.semester).all()
        
        # Группируем по семестрам
        semesters_data: Dict[int, List[CourseInRoadmap]] = {}
        total_credits = 0
        
        for course in courses:
            semester = course.semester if course.semester else 1
            if semester not in semesters_data:
                semesters_data[semester] = []
            
            semesters_data[semester].append(CourseInRoadmap(
                id=course.id,
                name=course.name,
                semester=semester,
                is_elective=course.is_elective,
                credits=course.credits
            ))
            total_credits += course.credits
        
        return RoadmapResponse(
            specialization_id=specialization.id,
            specialization_name=specialization.name,
            duration_years=specialization.duration_years,
            semesters=semesters_data,
            total_credits=total_credits
        )
    
    @staticmethod
    def get_skills_matrix(
        db: Session,
        specialization_id: int,
        user: Optional[User] = None
    ) -> Optional[SkillsMatrixResponse]:
        """Получить матрицу навыков специальности"""
        specialization = db.query(Specialization).filter(
            Specialization.id == specialization_id
        ).first()
        
        if not specialization or not specialization.required_skills:
            return None
        
        # Получаем текущие навыки пользователя (если указан)
        user_skills = {}
        if user:
            student_skills = db.query(StudentSkill).filter(
                StudentSkill.student_id == user.id
            ).all()
            user_skills = {ss.skill_id: ss.level for ss in student_skills}
        
        # Формируем список требуемых навыков
        required_skills_list = []
        for skill_id, required_level in specialization.required_skills.items():
            skill = db.query(Skill).filter(Skill.id == int(skill_id)).first()
            if skill:
                required_skills_list.append(SkillRequirement(
                    skill_id=skill.id,
                    skill_name=skill.name,
                    required_level=required_level,
                    current_level=user_skills.get(skill.id, 0)
                ))
        
        return SkillsMatrixResponse(
            specialization_id=specialization.id,
            specialization_name=specialization.name,
            required_skills=required_skills_list
        )

