from django.db import models

from user.management.models import Policy
from reseller.models import Reseller


class BoxRoles(models.Model):
    br_id       = models.AutoField(primary_key=True)    # 사용자역할 ID
    br_rolename = models.CharField(max_length=50)       # 사용자역할 이름

    class Meta:
        db_table = 'box_roles'

    def __str__(self):
        return self.br_rolename


class BoxUsers(models.Model):
    bu_id           = models.AutoField(primary_key=True)            # 유저번호
    bu_firstname    = models.CharField(max_length=50, null=True)    # 성
    bu_lastname     = models.CharField(max_length=50, null=True)    # 이름
    bu_email        = models.CharField(max_length=200)              # 이메일(유저 ID)
    bu_pw           = models.CharField(max_length=200, null=True)   # 비밀번호
    bu_permit       = models.IntegerField(default=0)                # 검색허용(2=모든사용자, 0=백업만, 1=검색만)
    bu_createdate   = models.DateTimeField(auto_now_add=True)       # 생성일
    bu_modifydate   = models.DateTimeField(auto_now=True)           # 수정일
    bu_status       = models.IntegerField(default=1)                # 유저상태(1:활성화, 2:일시정지, 3:탈퇴)
    bu_permission   = models.CharField(max_length=1, default='N')   # 권한(A=관리자, N=일반사용자)  *box_roles 테이블 생성으로 인하여 삭제예정
    bu_gnrllimit    = models.FloatField(default=0)                  # 일반 저장소 제한(GB) (0=제한없음)
    bu_coldlimit    = models.FloatField(default=0)                  # 콜드 스토리지 제한(GB) (0=제한없음)
    bu_ocrlimit     = models.IntegerField(default=0)                # OCR 페이지 수 제한(0=제한없음)
    bu_labelid      = models.IntegerField(default=0)                # 라벨
    reseller        = models.ForeignKey(Reseller, db_column='bu_resellerid', on_delete=models.SET_NULL, null=True)   # 리셀러 ID
    policy          = models.ForeignKey(Policy, db_column='bu_policyid', on_delete=models.DO_NOTHING, null=True)    # 정책 ID
    boxRoles        = models.ManyToManyField(BoxRoles, through='BoxUserrole', through_fields=('boxUsers', 'boxRoles',))

    class Meta:
        db_table = 'box_users'

    def __str__(self):
        return self.bu_email


class BoxUserrole(models.Model):
    ur_id    = models.AutoField(primary_key=True)
    boxUsers = models.ForeignKey(BoxUsers, on_delete=models.CASCADE, db_column='ur_userid')
    boxRoles = models.ForeignKey(BoxRoles, on_delete=models.CASCADE, db_column='ur_roleid')

    class Meta:
        db_table = 'box_userrole'
        unique_together = (('boxUsers', 'boxRoles'),)

    def __str__(self):
        return self.boxUsers.bu_firstname + ' ' + self.boxUsers.bu_lastname + ":" + self.boxRoles.br_rolename


class BoxUserinfo(models.Model):
    ui_id = models.AutoField(primary_key=True)          # 유저정보 ID
    ui_licenseKey = models.CharField(max_length=16)     # 라이센스 키
    ui_certify = models.CharField(max_length=45)        # 2단계 인증키
    ui_supercertify = models.CharField(max_length=45)   # 2단계 슈퍼 인증키 (OTP 분실 시 사용)
    ui_location = models.CharField(max_length=45)       # 데이터 저장위치
    ui_apikey = models.CharField(max_length=32)         # 공개 API ID
    ui_apipw = models.CharField(max_length=32)          # 공개 API PW
    ui_connection = models.CharField(max_length=45)     # 연결설정(A=모든 API 주소에 대해 액세스 허용, B=특정 주소 연결만 액세스 허용, C=지정된 IP 주소는 액세스 제한)
    boxUsers = models.ForeignKey(BoxUsers, on_delete=models.CASCADE, db_column='ui_userid')  # 유저 ID
    ui_tel = models.CharField(max_length=20)            # 전화번호
    ui_lang = models.CharField(max_length=2)            # 언어
    ui_permitfile = models.CharField(max_length=1, default='N') # 관리자에게 파일 검색 허용

    class Meta:
        db_table = 'box_userinfo'

    def __str__(self):
        return self.ui_id
