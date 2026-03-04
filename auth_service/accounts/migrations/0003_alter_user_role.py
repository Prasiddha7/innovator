from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('admin', 'Admin'), ('coordinator', 'Coordinator'), ('teacher', 'Teacher'), ('principal', 'Principal'), ('elearning_vendor', 'Elearning Vendor'), ('student', 'Student'), ('ecommerce_vendor', 'Ecommerce Vendor'), ('customer', 'Customer')], max_length=30, null=True),
        ),
    ]
