# Generated by Django 4.2 on 2023-08-08 03:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("adminpage", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Notice",
            fields=[
                ("Notice_num", models.AutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=100)),
                ("text", models.TextField()),
                ("creat_date", models.DateField(auto_now_add=True)),
                ("count", models.IntegerField(default=0)),
                (
                    "admin_id",
                    models.ForeignKey(
                        db_column="admin_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="adminpage.admin",
                    ),
                ),
            ],
            options={
                "db_table": "notice",
            },
        ),
    ]