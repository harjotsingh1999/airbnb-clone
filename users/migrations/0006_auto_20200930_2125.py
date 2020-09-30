# Generated by Django 2.2.5 on 2020-09-30 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_user_login_method"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="login_method",
            field=models.CharField(
                choices=[("email", "Email"), ("github", "Github"), ("gmail", "Gmail")],
                default="email",
                max_length=50,
            ),
        ),
    ]
