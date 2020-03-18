from django.db.models import Model, BigAutoField, ForeignKey, OneToOneField, PositiveSmallIntegerField,\
    BigIntegerField, CharField, IntegerField, FloatField, TextField, BooleanField, DateTimeField, CASCADE


# 리셀러
class Reseller(Model):
    rs_id = BigAutoField(primary_key=True)                                      # 리셀러 ID
    rs_phone = CharField(max_length=64, null=True, default=None)                # 전화번호
    rs_companyname = CharField(max_length=200)                                  # 회사명
    rs_status = CharField(max_length=1)                                         # 상태(A:활성화, S:일시정지, D:삭제)
    rs_createdate = DateTimeField(auto_now_add=True)                            # 등록일
    rs_expiredate = DateTimeField()                                             # 만료일
    rs_windowbuild = CharField(max_length=64, null=True, default=None)          # 윈도우 빌드번호
    rs_macbuild = CharField(max_length=64, null=True, default=None)             # 맥 빌드번호
    rs_language = IntegerField(null=True, default=None)                         # 언어
    rs_deletedate = DateTimeField(null=True, default=None)                      # 삭제일
    rs_email = CharField(max_length=200)                                        # 이메일
    rs_pw = CharField(max_length=200)                                           # 패스워드
    rs_credit = FloatField()                                                    # 신용거래
    rs_type = CharField(max_length=1)                               # 리셀러 타입(P:partner, W:white label, R:reseller)
    rs_confirm = CharField(max_length=1, default='N')                           # 이메일확인(Y:확인, N:미확인)
    rs_hotcapacity = BigIntegerField(default=0)                                 # 일반 사용량
    rs_coldcapacity = BigIntegerField(default=0)                                # 콜드 사용량
    rs_clientsignupplanid = IntegerField(null=True, default=None)               # 배포빌드번호
    rs_deploymentbuildno = CharField(max_length=64, null=True, default=None)    # 플랜ID
    rs_autotopupcredit = FloatField()                                           # 자동신용거래
    rs_accountmanager = IntegerField()                                          # 관리자ID
    rs_subdomain = CharField(max_length=255, null=True, default=None)           # 도메인주소
    rs_country = CharField(max_length=16, null=True, default=None)              # 국가
    rs_ipaddress = CharField(max_length=64, null=True, default=None)            # IP 주소
    rs_tenantid = IntegerField(null=True, default=None)                         # 관리자 Reseller ID
    rs_unlimitedcredit = CharField(max_length=1, default='F')                   # 무제한 신용(T:true, F:false)

    class Meta:
        managed = False
        db_table = 'box_reseller'


# 리셀러 역할
class ResellerRoles(Model):
    ro_id = BigAutoField(primary_key=True)     # 리셀러역할 ID
    ro_rolename = CharField(max_length=45)  # 리셀러 롤명

    class Meta:
        managed = False
        db_table = 'box_resellerroles'


# 리셀러 - 리셀러 역할 맵핑
class ResellerRoleMapping(Model):
    rr_id = BigAutoField(primary_key=True) # 리셀러Role맵핑 ID
    reseller = OneToOneField(Reseller, on_delete=CASCADE, db_column='rr_rsid')    # 리셀러 ID
    resellerRoles = ForeignKey(ResellerRoles, on_delete=CASCADE, db_column='rr_roleid')     # 리셀러Roles ID

    class Meta:
        managed = False
        db_table = 'box_resellerrole'


# 플랜
class Plan(Model):
    pl_id = BigAutoField(primary_key=True)                              # 계획 ID
    pl_name = CharField(max_length=300)                                 # 계획명
    pl_hotcapacity = BigIntegerField()                                  # Hot Capacity
    pl_coldcapacity = BigIntegerField()                                 # Cold Capacity
    pl_mediacapacity = BigIntegerField()                                # Media Capacity
    pl_ocr = IntegerField()                                             # OCR 페이지수
    pl_users = IntegerField()                                           # 사용자 수
    pl_servers = IntegerField()                                         # 서버대수
    pl_mobiles = IntegerField()                                         # 모바일
    pl_type = PositiveSmallIntegerField()   # 계획타입(1:home, 2:business, 3:business starter, 4:business basic,
    #                                                 5:business starterNew, 6: business Standard)
    pl_subscription = CharField(max_length=1)   # 신청구분 (T:trial, F:free, M:monthly, Y:yearly, L:life-time)
    pl_mediatype = CharField(max_length=1)                              # 미디어타입(N:none, S:sd, H:hd, F:fhd)
    pl_audittype = CharField(max_length=1)                              # 승인타입(N:none, B:basic, L:lifetime, F:free)
    pl_flagdr = CharField(max_length=1, null=True, default='N')         # 플래그 DR(Y:선택, N:미선택)
    pl_cloudservice = CharField(max_length=1, null=True, default='N')   # 클라우드서비스(Y:선택, N:미선택)
    pl_ediscovery = CharField(max_length=1, null=True, default='N')     # E Discovery(Y:선택, N:미선택)
    pl_face = CharField(max_length=1, null=True, default='N')           # Disable Faces(Y:선택, N:미선택)
    pl_lable = CharField(max_length=1, null=True, default='N')          # Disable Lables(Y:선택, N:미선택)
    pl_createdate = DateTimeField(auto_now_add=True)                    # 생성일
    pl_modifydate = DateTimeField(auto_now=True)                        # 수정일
    reseller = ForeignKey(Reseller, on_delete=CASCADE, db_column='pl_resellerid')   # 프로덕트 ID
    pl_tenantid = IntegerField(null=True)                               # 테넌트 ID
    pl_backuptype = CharField(max_length=1)                            # A:Computers And Mobiles, C:Computers, M:Mobiles

    class Meta:
        managed = False
        db_table = 'box_plan'
