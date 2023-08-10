# Generated by Django 4.2 on 2023-08-08 03:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("adminpage", "0001_initial"),
        ("Account", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="QuestionBoard",
            fields=[
                ("question_num", models.AutoField(primary_key=True, serialize=False)),
                ("title", models.TextField()),
                ("text", models.TextField()),
                ("create_date", models.DateField(auto_now_add=True)),
                ("count", models.IntegerField(null=True)),
                (
                    "username",
                    models.ForeignKey(
                        db_column="username",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Account.userinfo",
                    ),
                ),
            ],
            options={
                "db_table": "question_board",
            },
        ),
        migrations.CreateModel(
            name="Answer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.TextField()),
                ("create_date", models.DateField(auto_now_add=True)),
                (
                    "admin_id",
                    models.ForeignKey(
                        db_column="admin_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="adminpage.admin",
                    ),
                ),
                (
                    "question_num",
                    models.ForeignKey(
                        db_column="question_num",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="questionboard.questionboard",
                    ),
                ),
            ],
            options={
                "db_table": "answer",
            },
        ),
    ]
