from django.utils import timezone
from django.db import models
from Account.models import UserInfo
from adminpage.models import Admin

class GenerateId(models.Model):
    ginseng_id = models.CharField(max_length=50, primary_key=True)
    username = models.ForeignKey(UserInfo, on_delete=models.CASCADE, db_column='username')

    class Meta:
        db_table = 'generate_ID'

class WonsiData(models.Model):
    image_id = models.CharField(max_length=50, primary_key=True)
    ginseng_id = models.ForeignKey(GenerateId, on_delete=models.CASCADE, db_column='ginseng_id')
    username = models.ForeignKey(UserInfo, on_delete=models.CASCADE, db_column='username')
    age = models.CharField(max_length=10, null=False, default=0)
    grade = models.CharField(max_length=10, null=False, default=0)
    variety = models.CharField(max_length=10, null=False, default=0)
    wonsi_verification = models.SmallIntegerField(null=False, default=0)

    class Meta:
        db_table = 'wonsi_data'


class WonsiBoard(models.Model):
    wonsi_num = models.IntegerField(primary_key=True)
    image_id = models.ForeignKey(WonsiData, on_delete=models.CASCADE, db_column='image_id')
    title = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True)
    state = models.PositiveSmallIntegerField(null=False, default=0)
    username = models.ForeignKey(UserInfo, on_delete=models.CASCADE, db_column='username')

    class Meta:
        db_table = 'wonsi_board'


class WonsiComments(models.Model):
    wonsi_comments_num = models.AutoField(primary_key=True)
    admin_id = models.ForeignKey(Admin, on_delete=models.CASCADE, db_column='admin_id')
    wonsi_num = models.ForeignKey(WonsiBoard, on_delete=models.CASCADE, db_column='wonsi_num')
    text = models.TextField()
    create_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'wonsi_comments'
