# Generated by Django 3.2.5 on 2021-11-30 14:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_remove_project_documents'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='project_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.project'),
        ),
    ]
