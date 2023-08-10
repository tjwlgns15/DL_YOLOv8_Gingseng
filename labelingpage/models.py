from django.db import models

from Account.models import UserInfo
from adminpage.models import Admin
from uploadpage.models import WonsiData


class LabelingWork(models.Model):
    work_num = models.AutoField(primary_key=True)
    image_id = models.ForeignKey(WonsiData, on_delete=models.CASCADE, db_column='image_id')
    username = models.ForeignKey(UserInfo, on_delete=models.CASCADE, db_column='username')
    label_verification = models.PositiveIntegerField()

    class Meta:
        db_table = 'labeling_work'


class LabelingData(models.Model):
    label_num = models.AutoField(primary_key=True)
    image_id = models.ForeignKey(WonsiData, on_delete=models.CASCADE, db_column='image_id')
    head = models.CharField(max_length=50, null=True, default='[0, 0, 0, 0]')
    body = models.CharField(max_length=50, null=True, default='[0, 0, 0, 0]')
    leg = models.CharField(max_length=50, null=True, default='[0, 0, 0, 0]')
    total = models.CharField(max_length=50, null=True, default='[0, 0, 0, 0]')
    label_verification = models.PositiveIntegerField()

    class Meta:
        db_table = 'labeling_data'


class LabelingBoard(models.Model):
    board_num = models.AutoField(primary_key=True)
    title = models.TextField()
    create_date = models.DateField(auto_now_add=True)
    state = models.PositiveIntegerField()
    work_num = models.ForeignKey(LabelingWork, on_delete=models.CASCADE, db_column='work_num')
    class Meta:
        db_table = 'labeling_board'


class LabelingComments(models.Model):
    labeling_comments_num = models.AutoField(primary_key=True)
    board_num = models.ForeignKey(LabelingBoard, on_delete=models.CASCADE, db_column='board_num')
    admin_id = models.ForeignKey(Admin, on_delete=models.CASCADE, db_column='admin_id')
    text = models.TextField()
    create_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'labeling_comments'
