# Generated by Django 5.0.3 on 2024-04-06 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom_pro', '0004_remove_customuser_user_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='approval',
            name='Comments',
            field=models.CharField(default='no comments', max_length=400),
        ),
    ]
