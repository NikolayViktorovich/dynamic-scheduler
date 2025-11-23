"""SQLAlchemy модели базы данных"""

from app.models.course import Course, CourseDependency
from app.models.minor import Minor, MinorCourse, MinorSkill, UserMinor
from app.models.semester import Semester
from app.models.skill import CourseSkill, Skill, StudentSkill
from app.models.specialization import Specialization
from app.models.student_course import CourseStatus, StudentCourse
from app.models.tag import CourseTag
from app.models.user import User

__all__ = [
    "User",
    "Specialization",
    "Course",
    "CourseDependency",
    "Skill",
    "CourseSkill",
    "StudentSkill",
    "StudentCourse",
    "CourseStatus",
    "Semester",
    "CourseTag",
    "Minor",
    "MinorSkill",
    "MinorCourse",
    "UserMinor",
]
