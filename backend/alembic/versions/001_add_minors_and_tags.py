"""add minors and tags

Revision ID: 001_add_minors_and_tags
Revises:
Create Date: 2025-11-22

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "001_add_minors_and_tags"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Создание таблицы course_tags
    op.create_table(
        "course_tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("tag_name", sa.String(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_course_tags_id"), "course_tags", ["id"], unique=False)
    op.create_index(
        op.f("ix_course_tags_tag_name"), "course_tags", ["tag_name"], unique=False
    )

    # Создание таблицы minors
    op.create_table(
        "minors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("minor_type", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_minors_id"), "minors", ["id"], unique=False)

    # Создание таблицы minor_skills
    op.create_table(
        "minor_skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("minor_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("required_level", sa.Integer(), nullable=False, server_default="1"),
        sa.ForeignKeyConstraint(
            ["minor_id"],
            ["minors.id"],
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"],
            ["skills.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_minor_skills_id"), "minor_skills", ["id"], unique=False)

    # Создание таблицы minor_courses
    op.create_table(
        "minor_courses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("minor_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=True),
        sa.Column("is_required", sa.Boolean(), nullable=True, server_default="true"),
        sa.ForeignKeyConstraint(
            ["minor_id"],
            ["minors.id"],
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_minor_courses_id"), "minor_courses", ["id"], unique=False)

    # Создание таблицы user_minors
    op.create_table(
        "user_minors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("minor_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="selected"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["minor_id"],
            ["minors.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_minors_id"), "user_minors", ["id"], unique=False)


def downgrade():
    # Удаление таблиц в обратном порядке
    op.drop_index(op.f("ix_user_minors_id"), table_name="user_minors")
    op.drop_table("user_minors")

    op.drop_index(op.f("ix_minor_courses_id"), table_name="minor_courses")
    op.drop_table("minor_courses")

    op.drop_index(op.f("ix_minor_skills_id"), table_name="minor_skills")
    op.drop_table("minor_skills")

    op.drop_index(op.f("ix_minors_id"), table_name="minors")
    op.drop_table("minors")

    op.drop_index(op.f("ix_course_tags_tag_name"), table_name="course_tags")
    op.drop_index(op.f("ix_course_tags_id"), table_name="course_tags")
    op.drop_table("course_tags")
