from django.db import models
from Account.models import UserInfo
from adminpage.models import Admin


class QuestionBoard(models.Model):
    question_num = models.AutoField(primary_key=True)
    username = models.ForeignKey(UserInfo, on_delete=models.CASCADE, db_column='username')
    title = models.TextField()
    text = models.TextField()
    create_date = models.DateField(auto_now_add=True)
    count = models.IntegerField(null=True)

    class Meta:
        db_table = 'question_board'

    @property
    def update_counter(self):
        self.count +=1
        self.save()

class Answer(models.Model):
    admin_id = models.ForeignKey(Admin, on_delete=models.CASCADE, db_column='admin_id')
    question_num = models.ForeignKey(QuestionBoard, on_delete=models.CASCADE, db_column='question_num')
    text = models.TextField()
    create_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'answer'

