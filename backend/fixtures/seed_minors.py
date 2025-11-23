"""
Расширенный скрипт для заполнения базы данных с майнерами и тегами
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app.models import Course, CourseTag, Minor, MinorCourse, MinorSkill, Skill


def create_course_tags(db, courses):
    """Создание дифференцированных тегов для курсов"""
    print("Создание тегов курсов...")

    # Теги с весами: 1.0 - дополнительный, 2.0 - важный, 3.0 - основной
    course_tags_data = {
        "Introduction to Python": [
            ("python", 3.0),
            ("programming", 2.0),
            ("basics", 2.0),
        ],
        "Advanced Python": [("python", 3.0), ("advanced", 2.0), ("programming", 2.0)],
        "Data Analysis with Pandas": [
            ("python", 2.0),
            ("pandas", 3.0),
            ("data_analysis", 3.0),
            ("numpy", 2.0),
        ],
        "Statistics and Probability": [
            ("statistics", 3.0),
            ("mathematics", 2.0),
            ("probability", 2.0),
        ],
        "Linear Algebra": [("mathematics", 3.0), ("linear_algebra", 3.0)],
        "Machine Learning Basics": [
            ("machine_learning", 3.0),
            ("python", 2.0),
            ("data_science", 2.0),
        ],
        "Deep Learning": [
            ("deep_learning", 3.0),
            ("neural_networks", 3.0),
            ("machine_learning", 2.0),
            ("python", 1.0),
        ],
        "Data Visualization": [
            ("visualization", 3.0),
            ("python", 2.0),
            ("data_analysis", 2.0),
        ],
        "Big Data Processing": [
            ("big_data", 3.0),
            ("spark", 3.0),
            ("python", 2.0),
            ("data_engineering", 2.0),
        ],
        "ML in Production": [
            ("mlops", 3.0),
            ("machine_learning", 2.0),
            ("production", 2.0),
            ("devops", 1.0),
        ],
        "SQL and Databases": [("sql", 3.0), ("databases", 3.0), ("postgresql", 2.0)],
        "Java Programming": [("java", 3.0), ("programming", 2.0), ("backend", 1.0)],
        "Object-Oriented Design": [("oop", 3.0), ("design", 2.0), ("programming", 2.0)],
        "Design Patterns": [
            ("design_patterns", 3.0),
            ("software_engineering", 2.0),
            ("architecture", 2.0),
        ],
        "Software Testing": [
            ("testing", 3.0),
            ("quality_assurance", 2.0),
            ("software_engineering", 2.0),
        ],
        "Spring Framework": [
            ("spring", 3.0),
            ("java", 2.0),
            ("backend", 3.0),
            ("web_development", 1.0),
        ],
        "DevOps Practices": [
            ("devops", 3.0),
            ("ci_cd", 2.0),
            ("docker", 2.0),
            ("automation", 2.0),
        ],
        "Docker and Containerization": [
            ("docker", 3.0),
            ("containerization", 3.0),
            ("devops", 2.0),
        ],
        "CI/CD Pipelines": [("ci_cd", 3.0), ("devops", 3.0), ("automation", 2.0)],
        "AWS Cloud Services": [("aws", 3.0), ("cloud", 3.0), ("devops", 2.0)],
        "Supervised Learning Algorithms": [
            ("machine_learning", 3.0),
            ("supervised_learning", 3.0),
            ("algorithms", 2.0),
        ],
        "Neural Networks and Deep Learning": [
            ("neural_networks", 3.0),
            ("deep_learning", 3.0),
            ("machine_learning", 2.0),
        ],
        "JavaScript Fundamentals": [
            ("javascript", 3.0),
            ("programming", 2.0),
            ("web_development", 2.0),
        ],
        "React Development": [
            ("react", 3.0),
            ("javascript", 2.0),
            ("frontend", 3.0),
            ("web_development", 2.0),
        ],
        "Node.js and Express": [
            ("nodejs", 3.0),
            ("javascript", 2.0),
            ("backend", 3.0),
            ("web_development", 2.0),
        ],
        "REST API Design": [
            ("rest_api", 3.0),
            ("backend", 2.0),
            ("web_development", 2.0),
            ("api_design", 2.0),
        ],
        "GraphQL": [("graphql", 3.0), ("api_design", 2.0), ("backend", 2.0)],
        "MLOps": [
            ("mlops", 3.0),
            ("machine_learning", 2.0),
            ("devops", 2.0),
            ("production", 2.0),
        ],
    }

    course_dict = {course.name: course for course in courses}
    count = 0

    for course_name, tags in course_tags_data.items():
        if course_name not in course_dict:
            continue

        course = course_dict[course_name]
        for tag_name, weight in tags:
            tag = CourseTag(course_id=course.id, tag_name=tag_name, weight=weight)
            db.add(tag)
            count += 1

    db.commit()
    print(f"Создано {count} тегов для курсов.")


def create_minors(db):
    """Создание майнеров (дополнительного образования)"""
    print("Создание майнеров...")

    minors_data = [
        {
            "name": "Data Science & Analytics",
            "description": "Углубленное изучение анализа данных и машинного обучения",
            "minor_type": "deepening",  # углубление
        },
        {
            "name": "Backend Development",
            "description": "Разработка серверной части приложений",
            "minor_type": "deepening",
        },
        {
            "name": "MLOps & Production ML",
            "description": "Внедрение моделей машинного обучения в production",
            "minor_type": "cross_domain",  # смежная область
        },
        {
            "name": "Full Stack Web Development",
            "description": "Комплексная разработка веб-приложений",
            "minor_type": "deepening",
        },
        {
            "name": "Cloud & DevOps",
            "description": "Облачные технологии и автоматизация",
            "minor_type": "cross_domain",
        },
        {
            "name": "Product Analytics",
            "description": "Аналитика продуктов и работа с метриками",
            "minor_type": "reskill",  # смена области
        },
        {
            "name": "AI & Deep Learning",
            "description": "Искусственный интеллект и глубокое обучение",
            "minor_type": "deepening",
        },
    ]

    minors = []
    for minor_data in minors_data:
        minor = Minor(**minor_data, is_active=True)
        minors.append(minor)
        db.add(minor)

    db.commit()
    print(f"Создано {len(minors)} майнеров.")
    return minors


def link_minors_to_skills(db, minors, skills):
    """Связывание майнеров с целевыми навыками"""
    print("Связывание майнеров с навыками...")

    # Словарь: название майнера -> [(skill_id, required_level)]
    minor_skills_data = {
        "Data Science & Analytics": [
            (2, 3),  # Python - уровень 3
            (3, 2),  # Pandas - уровень 2
            (4, 2),  # NumPy - уровень 2
            (12, 3),  # Statistics - уровень 3
            (17, 2),  # Supervised Learning - уровень 2
            (23, 2),  # SQL - уровень 2
            (42, 2),  # Data Cleaning - уровень 2
        ],
        "Backend Development": [
            (2, 2),  # Python - уровень 2
            (9, 3),  # Java - уровень 3
            (23, 3),  # SQL - уровень 3
            (28, 2),  # Design Patterns - уровень 2
            (35, 3),  # Backend - уровень 3
            (36, 3),  # REST API - уровень 3
        ],
        "MLOps & Production ML": [
            (2, 3),  # Python - уровень 3
            (17, 2),  # Supervised Learning - уровень 2
            (31, 3),  # Docker - уровень 3
            (30, 2),  # CI/CD - уровень 2
            (44, 2),  # Model Evaluation - уровень 2
        ],
        "Full Stack Web Development": [
            (6, 3),  # JavaScript - уровень 3
            (7, 3),  # React - уровень 3
            (8, 3),  # Node.js - уровень 3
            (23, 2),  # SQL - уровень 2
            (34, 3),  # Frontend - уровень 3
            (35, 3),  # Backend - уровень 3
            (36, 2),  # REST API - уровень 2
        ],
        "Cloud & DevOps": [
            (30, 3),  # CI/CD - уровень 3
            (31, 3),  # Docker - уровень 3
            (39, 3),  # AWS - уровень 3
            (2, 2),  # Python - уровень 2
        ],
        "Product Analytics": [
            (2, 2),  # Python - уровень 2
            (23, 3),  # SQL - уровень 3
            (12, 2),  # Statistics - уровень 2
            (5, 2),  # Data Visualization - уровень 2
            (42, 2),  # Data Cleaning - уровень 2
        ],
        "AI & Deep Learning": [
            (2, 3),  # Python - уровень 3
            (18, 3),  # Neural Networks - уровень 3
            (19, 3),  # Deep Learning - уровень 3
            (14, 2),  # Linear Algebra - уровень 2
            (12, 2),  # Statistics - уровень 2
        ],
    }

    minor_dict = {minor.name: minor for minor in minors}
    count = 0

    for minor_name, skill_requirements in minor_skills_data.items():
        if minor_name not in minor_dict:
            continue

        minor = minor_dict[minor_name]
        for skill_id, required_level in skill_requirements:
            minor_skill = MinorSkill(
                minor_id=minor.id, skill_id=skill_id, required_level=required_level
            )
            db.add(minor_skill)
            count += 1

    db.commit()
    print(f"Создано {count} связей майнеров с навыками.")


def link_minors_to_courses(db, minors, courses):
    """Связывание майнеров с курсами"""
    print("Связывание майнеров с курсами...")

    # Словарь: название майнера -> [(course_name, order, is_required)]
    minor_courses_data = {
        "Data Science & Analytics": [
            ("Introduction to Python", 1, True),
            ("Data Analysis with Pandas", 2, True),
            ("Statistics and Probability", 3, True),
            ("Machine Learning Basics", 4, True),
            ("Data Visualization", 5, False),
            ("SQL and Databases", 6, False),
        ],
        "Backend Development": [
            ("Java Programming", 1, True),
            ("Object-Oriented Design", 2, True),
            ("Spring Framework", 3, True),
            ("Database Design", 4, True),
            ("REST API Design", 5, True),
            ("Microservices Architecture", 6, False),
        ],
        "MLOps & Production ML": [
            ("Machine Learning Basics", 1, True),
            ("ML in Production", 2, True),
            ("Docker and Containerization", 3, True),
            ("CI/CD Pipelines", 4, True),
            ("MLOps", 5, True),
            ("AWS Cloud Services", 6, False),
        ],
        "Full Stack Web Development": [
            ("JavaScript Fundamentals", 1, True),
            ("React Development", 2, True),
            ("Node.js and Express", 3, True),
            ("REST API Design", 4, True),
            ("Database Management", 5, True),
            ("GraphQL", 6, False),
        ],
        "Cloud & DevOps": [
            ("DevOps Practices", 1, True),
            ("Docker and Containerization", 2, True),
            ("CI/CD Pipelines", 3, True),
            ("AWS Cloud Services", 4, True),
            ("Kubernetes", 5, False),
            ("Infrastructure as Code", 6, True),
        ],
        "Product Analytics": [
            ("Introduction to Python", 1, True),
            ("SQL and Databases", 2, True),
            ("Statistics and Probability", 3, True),
            ("Data Analysis with Pandas", 4, True),
            ("Data Visualization", 5, True),
        ],
        "AI & Deep Learning": [
            ("Advanced Python", 1, True),
            ("Mathematical Foundations of ML", 2, True),
            ("Neural Networks and Deep Learning", 3, True),
            ("Deep Learning", 4, True),
            ("Computer Vision", 5, False),
        ],
    }

    minor_dict = {minor.name: minor for minor in minors}
    course_dict = {course.name: course for course in courses}
    count = 0

    for minor_name, course_list in minor_courses_data.items():
        if minor_name not in minor_dict:
            continue

        minor = minor_dict[minor_name]
        for course_name, order, is_required in course_list:
            if course_name not in course_dict:
                continue

            course = course_dict[course_name]
            minor_course = MinorCourse(
                minor_id=minor.id,
                course_id=course.id,
                order=order,
                is_required=is_required,
            )
            db.add(minor_course)
            count += 1

    db.commit()
    print(f"Создано {count} связей майнеров с курсами.")


def seed_minors_data():
    """Основная функция для добавления майнеров и тегов"""
    print("=" * 50)
    print("Добавление майнеров и тегов в базу данных")
    print("=" * 50)

    db = SessionLocal()

    try:
        # Получаем существующие курсы и навыки
        courses = db.query(Course).all()
        skills = db.query(Skill).all()

        if not courses:
            print("❌ Сначала запустите seed.py для создания основных данных!")
            return

        # Создаём теги для курсов
        create_course_tags(db, courses)

        # Создаём майнеры
        minors = create_minors(db)

        # Связываем майнеры с навыками
        link_minors_to_skills(db, minors, skills)

        # Связываем майнеры с курсами
        link_minors_to_courses(db, minors, courses)

        print("\n" + "=" * 50)
        print("✅ Майнеры и теги успешно добавлены!")
        print("=" * 50)
        print("Создано:")
        print(f"  - Майнеров: {len(minors)}")
        print("  - Связей майнеров с навыками")
        print("  - Связей майнеров с курсами")
        print("  - Тегов для курсов")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_minors_data()
