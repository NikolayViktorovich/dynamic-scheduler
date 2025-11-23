from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from app.models import Skill, StudentSkill, User, Specialization
from app.schemas.skill import (
    SkillResponse, SkillTreeNode, StudentSkillResponse,
    GapAnalysisResponse, GapAnalysisItem
)


class SkillService:
    """Сервис для работы с навыками"""
    
    @staticmethod
    def get_all(db: Session) -> List[Skill]:
        """Получить все навыки"""
        return db.query(Skill).all()
    
    @staticmethod
    def get_tree(db: Session) -> List[SkillTreeNode]:
        """Получить древовидную структуру навыков"""
        # Получаем все навыки
        all_skills = db.query(Skill).all()
        
        # Создаем словарь для быстрого доступа
        skills_dict: Dict[int, SkillTreeNode] = {}
        for skill in all_skills:
            skills_dict[skill.id] = SkillTreeNode(
                id=skill.id,
                name=skill.name,
                description=skill.description,
                level=skill.level,
                parent_id=skill.parent_id,
                children=[]
            )
        
        # Строим дерево
        root_skills = []
        for skill_id, skill_node in skills_dict.items():
            if skill_node.parent_id is None:
                root_skills.append(skill_node)
            else:
                # Добавляем как дочерний элемент к родителю
                parent = skills_dict.get(skill_node.parent_id)
                if parent:
                    parent.children.append(skill_node)
        
        return root_skills
    
    @staticmethod
    def get_student_skills(db: Session, user: User) -> List[StudentSkillResponse]:
        """Получить навыки студента"""
        student_skills = db.query(StudentSkill, Skill).join(
            Skill, StudentSkill.skill_id == Skill.id
        ).filter(StudentSkill.student_id == user.id).all()
        
        result = []
        for ss, skill in student_skills:
            result.append(StudentSkillResponse(
                skill_id=skill.id,
                skill_name=skill.name,
                level=ss.level,
                acquired_from=ss.acquired_from
            ))
        
        return result
    
    @staticmethod
    def gap_analysis(
        db: Session,
        user: User,
        specialization_id: Optional[int] = None
    ) -> Optional[GapAnalysisResponse]:
        """Анализ дефицита навыков"""
        # Определяем специальность
        if specialization_id is None:
            if user.specialization_id is None:
                return None
            specialization_id = user.specialization_id
        
        # Получаем специальность
        specialization = db.query(Specialization).filter(
            Specialization.id == specialization_id
        ).first()
        
        if not specialization or not specialization.required_skills:
            return None
        
        # Получаем текущие навыки студента
        student_skills = db.query(StudentSkill).filter(
            StudentSkill.student_id == user.id
        ).all()
        
        current_skills_dict = {ss.skill_id: ss.level for ss in student_skills}
        
        # Анализируем дефицит
        gaps = []
        satisfied_count = 0
        
        for skill_id_str, required_level in specialization.required_skills.items():
            skill_id = int(skill_id_str)
            skill = db.query(Skill).filter(Skill.id == skill_id).first()
            
            if not skill:
                continue
            
            current_level = current_skills_dict.get(skill_id, 0)
            gap = max(0, required_level - current_level)
            is_satisfied = current_level >= required_level
            
            if is_satisfied:
                satisfied_count += 1
            
            gaps.append(GapAnalysisItem(
                skill_id=skill.id,
                skill_name=skill.name,
                required_level=required_level,
                current_level=current_level,
                gap=gap,
                is_satisfied=is_satisfied
            ))
        
        total_required = len(gaps)
        completion_percentage = (satisfied_count / total_required * 100) if total_required > 0 else 0
        
        return GapAnalysisResponse(
            specialization_id=specialization.id,
            specialization_name=specialization.name,
            total_required_skills=total_required,
            satisfied_skills=satisfied_count,
            completion_percentage=round(completion_percentage, 2),
            gaps=sorted(gaps, key=lambda x: x.gap, reverse=True)  # Сортируем по дефициту
        )

