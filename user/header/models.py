from django.db import models


class BoxFaq(models.Model):
    fq_id = models.AutoField(primary_key=True)                  # FAQ ID
    fq_name = models.CharField(max_length=100)                  # FAQ 이름
    fq_email = models.CharField(max_length=100)                 # FAQ email
    fq_phone = models.CharField(max_length=100)                 # FAQ 전화번호
    fq_regdate = models.DateTimeField(auto_now_add=True)        # FAQ 등록일
    fq_message = models.TextField(max_length=1000)              # FAQ 메세지
    fq_status = models.CharField(max_length=1)                  # FAQ 처리여부 (Y:처리, N:처리중)
    fq_faqdiv = models.IntegerField()                           # 문의 구분(1:문의, 2:문제보고)

    class Meta:
        db_table = 'box_faq'
