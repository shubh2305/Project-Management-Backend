# Generated by Django 3.2.5 on 2021-11-17 10:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
