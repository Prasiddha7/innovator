"""
Custom migration to add ON UPDATE CASCADE to all foreign keys
referencing kms_user and kms_teacher tables.

This is required because CustomJWTAuthentication may need to update
the primary key of a User row to match the Auth service's ID,
and Django's default FK constraints do not cascade PK updates.
"""

from django.db import migrations

# (constraint_name, table_name, column_name, foreign_table, foreign_column)
FK_CONSTRAINTS = [
    # FKs pointing to kms_user
    ("kms_user_groups_user_id_14675b8d_fk_kms_user_id", "kms_user_groups", "user_id", "kms_user", "id"),
    ("kms_user_user_permissions_user_id_f925e4ef_fk_kms_user_id", "kms_user_user_permissions", "user_id", "kms_user", "id"),
    ("kms_coordinator_user_id_b58e6c64_fk_kms_user_id", "kms_coordinator", "user_id", "kms_user", "id"),
    ("kms_teacher_user_id_1e2df012_fk_kms_user_id", "kms_teacher", "user_id", "kms_user", "id"),
    ("kms_student_user_id_36f6b90a_fk_kms_user_id", "kms_student", "user_id", "kms_user", "id"),
    ("django_admin_log_user_id_c564eba6_fk_kms_user_id", "django_admin_log", "user_id", "kms_user", "id"),
    # FKs pointing to kms_teacher
    ("kms_studentattendance_teacher_id_b71d3ba1_fk_kms_teacher_id", "kms_studentattendance", "teacher_id", "kms_teacher", "id"),
    ("kms_studentattendanc_marked_by_id_96e9b83f_fk_kms_teach", "kms_studentattendance", "marked_by_id", "kms_teacher", "id"),
    ("kms_teacherattendance_teacher_id_8b43df0c_fk_kms_teacher_id", "kms_teacherattendance", "teacher_id", "kms_teacher", "id"),
    ("kms_teacherclassassi_teacher_id_eb937563_fk_kms_teach", "kms_teacherclassassignment", "teacher_id", "kms_teacher", "id"),
    ("kms_teachercompensat_teacher_id_053da1aa_fk_kms_teach", "kms_teachercompensationrule", "teacher_id", "kms_teacher", "id"),
    ("kms_teachercourseass_teacher_id_1d1dff40_fk_kms_teach", "kms_teachercourseassignment", "teacher_id", "kms_teacher", "id"),
    ("kms_teacherkyc_teacher_id_59fdbef6_fk_kms_teacher_id", "kms_teacherkyc", "teacher_id", "kms_teacher", "id"),
    ("kms_teachersalary_teacher_id_71ad23d9_fk_kms_teacher_id", "kms_teachersalary", "teacher_id", "kms_teacher", "id"),
    ("kms_teachersalaryslip_teacher_id_54126dc4_fk_kms_teacher_id", "kms_teachersalaryslip", "teacher_id", "kms_teacher", "id"),
]


def add_on_update_cascade(apps, schema_editor):
    """Drop existing FKs and re-add them with ON UPDATE CASCADE."""
    with schema_editor.connection.cursor() as cursor:
        for constraint_name, table, column, ref_table, ref_column in FK_CONSTRAINTS:
            # Check if the constraint actually exists before trying to drop it
            cursor.execute(
                "SELECT 1 FROM information_schema.table_constraints "
                "WHERE constraint_name = %s AND table_name = %s",
                [constraint_name, table],
            )
            if not cursor.fetchone():
                # Constraint name might differ; skip gracefully
                continue

            # Drop the old constraint
            cursor.execute(
                f'ALTER TABLE "{table}" DROP CONSTRAINT "{constraint_name}"'
            )
            # Re-add with ON UPDATE CASCADE (keep the original ON DELETE behaviour)
            cursor.execute(
                f'ALTER TABLE "{table}" ADD CONSTRAINT "{constraint_name}" '
                f'FOREIGN KEY ("{column}") REFERENCES "{ref_table}" ("{ref_column}") '
                f"ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED"
            )


def remove_on_update_cascade(apps, schema_editor):
    """Reverse: drop cascading FKs and re-add them without ON UPDATE CASCADE."""
    with schema_editor.connection.cursor() as cursor:
        for constraint_name, table, column, ref_table, ref_column in FK_CONSTRAINTS:
            cursor.execute(
                "SELECT 1 FROM information_schema.table_constraints "
                "WHERE constraint_name = %s AND table_name = %s",
                [constraint_name, table],
            )
            if not cursor.fetchone():
                continue

            cursor.execute(
                f'ALTER TABLE "{table}" DROP CONSTRAINT "{constraint_name}"'
            )
            cursor.execute(
                f'ALTER TABLE "{table}" ADD CONSTRAINT "{constraint_name}" '
                f'FOREIGN KEY ("{column}") REFERENCES "{ref_table}" ("{ref_column}") '
                f"DEFERRABLE INITIALLY DEFERRED"
            )


class Migration(migrations.Migration):

    dependencies = [
        ("kms", "0008_student_user"),
    ]

    operations = [
        migrations.RunPython(add_on_update_cascade, remove_on_update_cascade),
    ]
