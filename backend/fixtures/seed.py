"""
Скрипт для заполнения базы данных тестовыми данными
"""
import sys
import os

# Добавляем путь к приложению
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, engine, Base
from app.models import (
    User, Specialization, Course, Skill, CourseSkill,
    StudentCourse, StudentSkill, CourseDependency, Semester
)
from app.models.student_course import CourseStatus
from app.utils.security import get_password_hash
from datetime import datetime, timedelta


def clear_database():
    """Очистка базы данных"""
    print("Очистка базы данных...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("База данных очищена и пересоздана.")


def create_skills(db):
    """Создание древовидной структуры навыков"""
    print("Создание навыков...")
    
    skills_data = [
        # Программирование (корень)
        {"id": 1, "name": "Programming", "parent_id": None, "level": 0},
        {"id": 2, "name": "Python", "parent_id": 1, "level": 1},
        {"id": 3, "name": "Pandas", "parent_id": 2, "level": 2},
        {"id": 4, "name": "NumPy", "parent_id": 2, "level": 2},
        {"id": 5, "name": "Data Visualization", "parent_id": 2, "level": 2},
        {"id": 6, "name": "JavaScript", "parent_id": 1, "level": 1},
        {"id": 7, "name": "React", "parent_id": 6, "level": 2},
        {"id": 8, "name": "Node.js", "parent_id": 6, "level": 2},
        {"id": 9, "name": "Java", "parent_id": 1, "level": 1},
        {"id": 10, "name": "Spring Framework", "parent_id": 9, "level": 2},
        
        # Математика (корень)
        {"id": 11, "name": "Mathematics", "parent_id": None, "level": 0},
        {"id": 12, "name": "Statistics", "parent_id": 11, "level": 1},
        {"id": 13, "name": "Probability Theory", "parent_id": 12, "level": 2},
        {"id": 14, "name": "Linear Algebra", "parent_id": 11, "level": 1},
        {"id": 15, "name": "Calculus", "parent_id": 11, "level": 1},
        
        # Machine Learning (корень)
        {"id": 16, "name": "Machine Learning", "parent_id": None, "level": 0},
        {"id": 17, "name": "Supervised Learning", "parent_id": 16, "level": 1},
        {"id": 18, "name": "Neural Networks", "parent_id": 17, "level": 2},
        {"id": 19, "name": "Deep Learning", "parent_id": 18, "level": 3},
        {"id": 20, "name": "Unsupervised Learning", "parent_id": 16, "level": 1},
        {"id": 21, "name": "Reinforcement Learning", "parent_id": 16, "level": 1},
        
        # Базы данных (корень)
        {"id": 22, "name": "Databases", "parent_id": None, "level": 0},
        {"id": 23, "name": "SQL", "parent_id": 22, "level": 1},
        {"id": 24, "name": "PostgreSQL", "parent_id": 23, "level": 2},
        {"id": 25, "name": "NoSQL", "parent_id": 22, "level": 1},
        {"id": 26, "name": "MongoDB", "parent_id": 25, "level": 2},
        
        # Software Engineering (корень)
        {"id": 27, "name": "Software Engineering", "parent_id": None, "level": 0},
        {"id": 28, "name": "Design Patterns", "parent_id": 27, "level": 1},
        {"id": 29, "name": "Testing", "parent_id": 27, "level": 1},
        {"id": 30, "name": "CI/CD", "parent_id": 27, "level": 1},
        {"id": 31, "name": "Docker", "parent_id": 27, "level": 1},
        {"id": 32, "name": "Git", "parent_id": 27, "level": 1},
        
        # Web Development (корень)
        {"id": 33, "name": "Web Development", "parent_id": None, "level": 0},
        {"id": 34, "name": "Frontend", "parent_id": 33, "level": 1},
        {"id": 35, "name": "Backend", "parent_id": 33, "level": 1},
        {"id": 36, "name": "REST API", "parent_id": 35, "level": 2},
        {"id": 37, "name": "GraphQL", "parent_id": 35, "level": 2},
        
        # Cloud & DevOps (корень)
        {"id": 38, "name": "Cloud Computing", "parent_id": None, "level": 0},
        {"id": 39, "name": "AWS", "parent_id": 38, "level": 1},
        {"id": 40, "name": "Azure", "parent_id": 38, "level": 1},
        
        # Data Science специфичные
        {"id": 41, "name": "Data Analysis", "parent_id": None, "level": 0},
        {"id": 42, "name": "Data Cleaning", "parent_id": 41, "level": 1},
        {"id": 43, "name": "Feature Engineering", "parent_id": 41, "level": 1},
        {"id": 44, "name": "Model Evaluation", "parent_id": 16, "level": 1},
        {"id": 45, "name": "Big Data", "parent_id": 41, "level": 1},
        {"id": 46, "name": "Spark", "parent_id": 45, "level": 2},
    ]
    
    skills = []
    for skill_data in skills_data:
        skill = Skill(
            id=skill_data["id"],
            name=skill_data["name"],
            parent_id=skill_data["parent_id"],
            level=skill_data["level"],
            description=f"Навык: {skill_data['name']}"
        )
        skills.append(skill)
        db.add(skill)
    
    db.commit()
    print(f"Создано {len(skills)} навыков.")
    return skills


def create_specializations(db):
    """Создание специальностей"""
    print("Создание специальностей...")
    
    specializations_data = [
        {
            "name": "Data Science",
            "description": "Специализация по анализу данных и машинному обучению",
            "market_demand": 95.0,
            "duration_years": 2,
            "required_skills": {
                "2": 5,   # Python - уровень 5
                "3": 3,   # Pandas - уровень 3
                "4": 3,   # NumPy - уровень 3
                "12": 4,  # Statistics - уровень 4
                "13": 3,  # Probability Theory - уровень 3
                "14": 3,  # Linear Algebra - уровень 3
                "17": 4,  # Supervised Learning - уровень 4
                "18": 3,  # Neural Networks - уровень 3
                "23": 3,  # SQL - уровень 3
                "42": 3,  # Data Cleaning - уровень 3
                "43": 3,  # Feature Engineering - уровень 3
            }
        },
        {
            "name": "Software Engineering",
            "description": "Разработка программного обеспечения",
            "market_demand": 92.0,
            "duration_years": 2,
            "required_skills": {
                "2": 4,   # Python - уровень 4
                "9": 4,   # Java - уровень 4
                "10": 3,  # Spring Framework - уровень 3
                "23": 3,  # SQL - уровень 3
                "28": 4,  # Design Patterns - уровень 4
                "29": 3,  # Testing - уровень 3
                "30": 3,  # CI/CD - уровень 3
                "31": 3,  # Docker - уровень 3
                "32": 4,  # Git - уровень 4
                "36": 3,  # REST API - уровень 3
            }
        },
        {
            "name": "Machine Learning Engineer",
            "description": "Разработка и внедрение ML моделей в production",
            "market_demand": 97.0,
            "duration_years": 2,
            "required_skills": {
                "2": 5,   # Python - уровень 5
                "17": 5,  # Supervised Learning - уровень 5
                "18": 4,  # Neural Networks - уровень 4
                "19": 3,  # Deep Learning - уровень 3
                "20": 3,  # Unsupervised Learning - уровень 3
                "14": 4,  # Linear Algebra - уровень 4
                "12": 4,  # Statistics - уровень 4
                "31": 3,  # Docker - уровень 3
                "44": 4,  # Model Evaluation - уровень 4
            }
        },
        {
            "name": "Full Stack Developer",
            "description": "Разработка веб-приложений (frontend + backend)",
            "market_demand": 89.0,
            "duration_years": 2,
            "required_skills": {
                "6": 4,   # JavaScript - уровень 4
                "7": 4,   # React - уровень 4
                "8": 4,   # Node.js - уровень 4
                "2": 3,   # Python - уровень 3
                "23": 3,  # SQL - уровень 3
                "32": 3,  # Git - уровень 3
                "36": 4,  # REST API - уровень 4
                "34": 4,  # Frontend - уровень 4
                "35": 4,  # Backend - уровень 4
            }
        },
        {
            "name": "DevOps Engineer",
            "description": "Автоматизация и управление инфраструктурой",
            "market_demand": 88.0,
            "duration_years": 2,
            "required_skills": {
                "2": 3,   # Python - уровень 3
                "30": 5,  # CI/CD - уровень 5
                "31": 5,  # Docker - уровень 5
                "32": 4,  # Git - уровень 4
                "39": 4,  # AWS - уровень 4
                "23": 3,  # SQL - уровень 3
            }
        }
    ]
    
    specializations = []
    for spec_data in specializations_data:
        spec = Specialization(**spec_data)
        specializations.append(spec)
        db.add(spec)
    
    db.commit()
    print(f"Создано {len(specializations)} специальностей.")
    return specializations


def create_courses(db, specializations):
    """Создание курсов"""
    print("Создание курсов...")
    
    courses_data = [
        # Data Science courses
        {"name": "Introduction to Python", "spec": "Data Science", "semester": 1, "is_elective": False, "credits": 4},
        {"name": "Statistics and Probability", "spec": "Data Science", "semester": 1, "is_elective": False, "credits": 4},
        {"name": "Linear Algebra", "spec": "Data Science", "semester": 1, "is_elective": False, "credits": 3},
        {"name": "Data Analysis with Pandas", "spec": "Data Science", "semester": 2, "is_elective": False, "credits": 4},
        {"name": "Machine Learning Basics", "spec": "Data Science", "semester": 2, "is_elective": False, "credits": 5},
        {"name": "SQL and Databases", "spec": "Data Science", "semester": 2, "is_elective": True, "credits": 3},
        {"name": "Deep Learning", "spec": "Data Science", "semester": 3, "is_elective": False, "credits": 5},
        {"name": "Data Visualization", "spec": "Data Science", "semester": 3, "is_elective": True, "credits": 3},
        {"name": "Big Data Processing", "spec": "Data Science", "semester": 4, "is_elective": True, "credits": 4},
        {"name": "ML in Production", "spec": "Data Science", "semester": 4, "is_elective": True, "credits": 4},
        
        # Software Engineering courses
        {"name": "Java Programming", "spec": "Software Engineering", "semester": 1, "is_elective": False, "credits": 4},
        {"name": "Object-Oriented Design", "spec": "Software Engineering", "semester": 1, "is_elective": False, "credits": 4},
        {"name": "Algorithms and Data Structures", "spec": "Software Engineering", "semester": 1, "is_elective": False, "credits": 5},
        {"name": "Design Patterns", "spec": "Software Engineering", "semester": 2, "is_elective": False, "credits": 4},
        {"name": "Software Testing", "spec": "Software Engineering", "semester": 2, "is_elective": False, "credits": 3},
        {"name": "Spring Framework", "spec": "Software Engineering", "semester": 2, "is_elective": True, "credits": 4},
        {"name": "DevOps Practices", "spec": "Software Engineering", "semester": 3, "is_elective": False, "credits": 4},
        {"name": "Microservices Architecture", "spec": "Software Engineering", "semester": 3, "is_elective": True, "credits": 4},
        {"name": "Database Design", "spec": "Software Engineering", "semester": 3, "is_elective": True, "credits": 3},
        {"name": "Cloud Computing", "spec": "Software Engineering", "semester": 4, "is_elective": True, "credits": 4},
        
        # ML Engineer courses
        {"name": "Advanced Python", "spec": "Machine Learning Engineer", "semester": 1, "is_elective": False, "credits": 4},
        {"name": "Mathematical Foundations of ML", "spec": "Machine Learning Engineer", "semester": 1, "is_elective": False, "credits": 5},
        {"name": "Supervised Learning Algorithms", "spec": "Machine Learning Engineer", "semester": 2, "is_elective": False, "credits": 5},
        {"name": "Neural Networks and Deep Learning", "spec": "Machine Learning Engineer", "semester": 2, "is_elective": False, "credits": 5},
        {"name": "Unsupervised Learning", "spec": "Machine Learning Engineer", "semester": 3, "is_elective": False, "credits": 4},
        {"name": "Reinforcement Learning", "spec": "Machine Learning Engineer", "semester": 3, "is_elective": True, "credits": 4},
        {"name": "MLOps", "spec": "Machine Learning Engineer", "semester": 4, "is_elective": False, "credits": 4},
        {"name": "Computer Vision", "spec": "Machine Learning Engineer", "semester": 4, "is_elective": True, "credits": 4},
        
        # Full Stack courses
        {"name": "Web Development Basics", "spec": "Full Stack Developer", "semester": 1, "is_elective": False, "credits": 4},
        {"name": "JavaScript Fundamentals", "spec": "Full Stack Developer", "semester": 1, "is_elective": False, "credits": 4},
        {"name": "React Development", "spec": "Full Stack Developer", "semester": 2, "is_elective": False, "credits": 5},
        {"name": "Node.js and Express", "spec": "Full Stack Developer", "semester": 2, "is_elective": False, "credits": 5},
        {"name": "REST API Design", "spec": "Full Stack Developer", "semester": 3, "is_elective": False, "credits": 4},
        {"name": "Database Management", "spec": "Full Stack Developer", "semester": 3, "is_elective": False, "credits": 3},
        {"name": "GraphQL", "spec": "Full Stack Developer", "semester": 3, "is_elective": True, "credits": 3},
        
        # DevOps courses
        {"name": "Linux Administration", "spec": "DevOps Engineer", "semester": 1, "is_elective": False, "credits": 4},
        {"name": "Scripting with Python", "spec": "DevOps Engineer", "semester": 1, "is_elective": False, "credits": 3},
        {"name": "Docker and Containerization", "spec": "DevOps Engineer", "semester": 2, "is_elective": False, "credits": 5},
        {"name": "CI/CD Pipelines", "spec": "DevOps Engineer", "semester": 2, "is_elective": False, "credits": 5},
        {"name": "AWS Cloud Services", "spec": "DevOps Engineer", "semester": 3, "is_elective": False, "credits": 5},
        {"name": "Kubernetes", "spec": "DevOps Engineer", "semester": 3, "is_elective": True, "credits": 4},
        {"name": "Infrastructure as Code", "spec": "DevOps Engineer", "semester": 4, "is_elective": False, "credits": 4},
    ]
    
    spec_dict = {spec.name: spec for spec in specializations}
    courses = []
    
    for course_data in courses_data:
        spec_name = course_data.pop("spec")
        course = Course(
            **course_data,
            specialization_id=spec_dict[spec_name].id,
            difficulty_levels={"base": 1, "advanced": 2}
        )
        courses.append(course)
        db.add(course)
    
    db.commit()
    print(f"Создано {len(courses)} курсов.")
    return courses


def link_courses_to_skills(db, courses):
    """Связывание курсов с навыками"""
    print("Связывание курсов с навыками...")
    
    # Упрощенное связывание (можно расширить)
    course_skill_mappings = [
        # Python курсы
        ("Introduction to Python", [(2, 1, 2), (32, 1, 1)]),  # Python, Git
        ("Advanced Python", [(2, 1, 3), (2, 2, 4)]),  # Python разные уровни
        ("Data Analysis with Pandas", [(3, 1, 2), (4, 1, 2), (5, 1, 2)]),  # Pandas, NumPy, Visualization
        
        # Statistics
        ("Statistics and Probability", [(12, 1, 2), (13, 1, 2)]),  # Statistics, Probability
        ("Linear Algebra", [(14, 1, 2), (14, 2, 3)]),  # Linear Algebra
        
        # ML courses
        ("Machine Learning Basics", [(17, 1, 2), (44, 1, 2)]),  # Supervised Learning, Model Evaluation
        ("Deep Learning", [(18, 1, 2), (19, 1, 2), (18, 2, 3)]),  # Neural Networks, Deep Learning
        ("Supervised Learning Algorithms", [(17, 1, 3), (17, 2, 4)]),  # Supervised Learning
        ("Neural Networks and Deep Learning", [(18, 1, 3), (19, 1, 3)]),  # NN, DL
        ("Unsupervised Learning", [(20, 1, 2), (20, 2, 3)]),  # Unsupervised Learning
        
        # Software Engineering
        ("Java Programming", [(9, 1, 2), (9, 2, 3)]),  # Java
        ("Design Patterns", [(28, 1, 2), (28, 2, 3)]),  # Design Patterns
        ("Software Testing", [(29, 1, 2), (29, 2, 3)]),  # Testing
        ("Spring Framework", [(10, 1, 2), (10, 2, 3)]),  # Spring
        
        # Databases
        ("SQL and Databases", [(23, 1, 2), (24, 1, 1)]),  # SQL, PostgreSQL
        ("Database Design", [(23, 1, 2), (23, 2, 3)]),  # SQL
        ("Database Management", [(23, 1, 2), (25, 1, 1)]),  # SQL, NoSQL
        
        # DevOps
        ("DevOps Practices", [(30, 1, 2), (31, 1, 2)]),  # CI/CD, Docker
        ("Docker and Containerization", [(31, 1, 3), (31, 2, 4)]),  # Docker
        ("CI/CD Pipelines", [(30, 1, 3), (30, 2, 4)]),  # CI/CD
        ("AWS Cloud Services", [(39, 1, 3), (39, 2, 4)]),  # AWS
        
        # Web Development
        ("JavaScript Fundamentals", [(6, 1, 2), (6, 2, 3)]),  # JavaScript
        ("React Development", [(7, 1, 3), (7, 2, 4), (34, 1, 2)]),  # React, Frontend
        ("Node.js and Express", [(8, 1, 3), (8, 2, 4), (35, 1, 2)]),  # Node.js, Backend
        ("REST API Design", [(36, 1, 2), (36, 2, 3)]),  # REST API
        ("GraphQL", [(37, 1, 2), (37, 2, 3)]),  # GraphQL
    ]
    
    course_dict = {course.name: course for course in courses}
    count = 0
    
    for course_name, skill_mappings in course_skill_mappings:
        if course_name not in course_dict:
            continue
        
        course = course_dict[course_name]
        for skill_id, difficulty_level, skill_weight in skill_mappings:
            course_skill = CourseSkill(
                course_id=course.id,
                skill_id=skill_id,
                difficulty_level=difficulty_level,
                skill_weight=skill_weight
            )
            db.add(course_skill)
            count += 1
    
    db.commit()
    print(f"Создано {count} связей курсов с навыками.")


def create_test_users(db, specializations, courses):
    """Создание тестовых пользователей"""
    print("Создание тестовых пользователей...")
    
    users_data = [
        {
            "email": "student1@urfu.ru",
            "full_name": "Иван Иванов",
            "password": "password123",
            "specialization": "Data Science",
            "completed_courses": ["Introduction to Python", "Statistics and Probability"]
        },
        {
            "email": "student2@urfu.ru",
            "full_name": "Мария Петрова",
            "password": "password123",
            "specialization": "Software Engineering",
            "completed_courses": ["Java Programming", "Object-Oriented Design"]
        },
        {
            "email": "student3@urfu.ru",
            "full_name": "Алексей Сидоров",
            "password": "password123",
            "specialization": "Machine Learning Engineer",
            "completed_courses": []
        }
    ]
    
    spec_dict = {spec.name: spec for spec in specializations}
    course_dict = {course.name: course for course in courses}
    users = []
    
    for user_data in users_data:
        spec_name = user_data.pop("specialization")
        completed_course_names = user_data.pop("completed_courses")
        password = user_data.pop("password")
        
        user = User(
            **user_data,
            hashed_password=get_password_hash(password),
            specialization_id=spec_dict[spec_name].id,
            is_active=True
        )
        db.add(user)
        db.flush()  # Получаем ID
        
        # Добавляем завершенные курсы
        for course_name in completed_course_names:
            if course_name in course_dict:
                course = course_dict[course_name]
                student_course = StudentCourse(
                    student_id=user.id,
                    course_id=course.id,
                    status=CourseStatus.COMPLETED,
                    difficulty_level=1,
                    grade=85,
                    completed_at=datetime.utcnow() - timedelta(days=30)
                )
                db.add(student_course)
                
                # Добавляем навыки
                course_skills = db.query(CourseSkill).filter(
                    CourseSkill.course_id == course.id,
                    CourseSkill.difficulty_level <= 1
                ).all()
                
                for cs in course_skills:
                    student_skill = StudentSkill(
                        student_id=user.id,
                        skill_id=cs.skill_id,
                        level=cs.skill_weight,
                        acquired_from=f"course_{course.id}"
                    )
                    db.add(student_skill)
        
        users.append(user)
    
    db.commit()
    print(f"Создано {len(users)} тестовых пользователей.")
    print("Данные для входа:")
    for user in users:
        print(f"  Email: {user.email}, Password: password123")
    
    return users


def main():
    """Основная функция"""
    print("=" * 50)
    print("Заполнение базы данных тестовыми данными")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        clear_database()
        
        skills = create_skills(db)
        specializations = create_specializations(db)
        courses = create_courses(db, specializations)
        link_courses_to_skills(db, courses)
        users = create_test_users(db, specializations, courses)
        
        print("\n" + "=" * 50)
        print("✅ База данных успешно заполнена!")
        print("=" * 50)
        print(f"Создано:")
        print(f"  - Навыков: {len(skills)}")
        print(f"  - Специальностей: {len(specializations)}")
        print(f"  - Курсов: {len(courses)}")
        print(f"  - Пользователей: {len(users)}")
        print("\nAPI доступен по адресу: http://localhost:8000")
        print("Документация: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Ошибка при заполнении базы данных: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()

