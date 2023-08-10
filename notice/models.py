from django.db import models

from adminpage.models import Admin


class Notice(models.Model):
    Notice_num = models.AutoField(primary_key=True)
    admin_id = models.ForeignKey(Admin, on_delete=models.CASCADE, db_column='admin_id')
    title = models.CharField(max_length=100)
    text = models.TextField()
    creat_date = models.DateField(auto_now_add=True)
    count = models.IntegerField(null=False, default=0)

    class Meta:
        db_table = 'notice'

