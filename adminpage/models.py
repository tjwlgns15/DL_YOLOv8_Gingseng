from django.db import models

from Account.models import UserInfo


class PointSetting(models.Model):
    label_point = models.PositiveIntegerField()
    upload_point = models.PositiveIntegerField()

    class Meta:
        db_table = 'point_setting'

class Admin(models.Model):
    admin_id = models.CharField(max_length=50, primary_key=True)
    pwd = models.CharField(max_length=50)

    class Meta:
        db_table = 'admin'


class point_A(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='중복제거')
    user_name = models.CharField(max_length=20, null=False, verbose_name='유저 아이디')
    remaining_points = models.IntegerField(default=0, verbose_name='남은 포인트')

    class Meta:
        db_table = 'point_a'
        indexes = [
            models.Index(fields=['user_name']),
        ]
        verbose_name = '유저의 남은 포인트 조회하는 테이블'
        verbose_name_plural = '유저의 남은 포인트 조회하는 테이블'

class point_B(models.Model):
    point_num = models.IntegerField(primary_key=True, verbose_name='중복제거')
    user_name = models.CharField(max_length=20, null=False, verbose_name='지급 유저')
    point_version = models.IntegerField(null=False, verbose_name='작업 환경(1원시 2라벨)')
    point_pay = models.IntegerField(null=False, verbose_name='지급 포인트')
    point_date = models.DateField(null=False, verbose_name='지급 일자')

    class Meta:
        db_table = 'point_b'
        indexes = [
            models.Index(fields=['user_name']),
        ]
        verbose_name = '포인트 지급 테이블 (원시 / 라벨링 데이터 검증되면 포인트(로그) 지급됨)'

class point_C(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name='중복제거')
    point_version = models.IntegerField(null=False, verbose_name='변경하는 포인트 (1 원시 2라벨링)')
    point_pay = models.IntegerField(null=False, verbose_name='변경하는 가격')
    point_date = models.DateField(null=False, verbose_name='변경일자')

    class Meta:
        db_table = 'point_c'
        verbose_name = '포인트 가격 조정하는 테이블'


class point_D(models.Model):
    money_num = models.IntegerField(primary_key=True, verbose_name='중복제거')
    money_Payments = models.IntegerField(null=False, verbose_name='전환 가격')
    money_date = models.DateField(null=False, verbose_name='요청일자')
    money_a = models.IntegerField(null=False, verbose_name='상태(0 대기 1 지급 2반환)')
    user_name = models.CharField(max_length=20, null=False, verbose_name='요청 유저')

    class Meta:
        db_table = 'point_d'
        indexes = [
            models.Index(fields=['user_name']),
        ]
        verbose_name = '포인트 현금 전환 로그 테이블'