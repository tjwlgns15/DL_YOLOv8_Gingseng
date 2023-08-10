from django.db import models

class UserInfo(models.Model):
    username = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=20,null=False, default=0)
    pwd = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    authority = models.PositiveSmallIntegerField(null=False, default=0)
    total_point = models.FloatField(null=False, default=0)
    upload_post = models.PositiveIntegerField(null=False, default=0)
    labeling_post = models.PositiveIntegerField(null=False, default=0)
    question_post = models.PositiveIntegerField(null=False, default=0)

    class Meta:
        db_table = 'UserInfo'