from django.db import models


class BoxPolicydata(models.Model):
    pd_id           = models.IntegerField(primary_key=True)                                         # 정책관리 ID
    pd_div          = models.CharField(max_length=1)                                                # 스토리지 구분(G:일반스토리지, C:콜드스토리지)
    pd_emailchk     = models.CharField(max_length=1, default='N')                                   # 임의백업 이메일(Y:체크, N:미체크)
    pd_wallpaperchk = models.CharField(max_length=1, default='N')                                   # 임의백업 바탕화면(Y:체크, N:미체크)
    pd_documentchk  = models.CharField(max_length=1, default='N')                                   # 임의백업 문서(Y:체크, N:미체크)
    pd_officechk    = models.CharField(max_length=1, default='N')                                   # 임의백업 오피스파일(Y:체크, N:미체크)
    pd_acntnfilechk = models.CharField(max_length=1, default='N')                                   # 임의백업 회계파일(Y:체크, N:미체크)
    pd_bookmarkchk  = models.CharField(max_length=1, default='N')                                   # 임의백업 북마크(Y:체크, N:미체크)
    pd_imagechk     = models.CharField(max_length=1, default='N')                                   # 임의백업 이미지(Y:체크, N:미체크)
    pd_musicchk     = models.CharField(max_length=1, default='N')                                   # 임의백업 음악(Y:체크, N:미체크)
    pd_videochk     = models.CharField(max_length=1, default='N')                                   # 임의백업 비디오(Y:체크, N:미체크)
    pd_ebookchk     = models.CharField(max_length=1, default='N')                                   # 임의백업 전자책과 연하장 데이터(Y:체크, N:미체크)
    pd_createdate   = models.DateTimeField(auto_now_add=True)                                       # 생성일
    pd_modifydate   = models.DateTimeField(auto_now=True)                                           # 수정일
    # bp_policyid     = models.ForeignKey('BoxPolicy', on_delete=models.CASCADE, db_column='bp_id')   # 정책 ID
    pd_policyid      = models.IntegerField()

    class Meta:
        db_table = 'box_policydata'

    def __str__(self):
        return self.pd_div


class BoxPolicyextension(models.Model):
    ex_id           = models.AutoField(primary_key=True)                                         # 정책확장자 ID
    ex_shadowcopy   = models.TextField()                                                            # shadow copy 확장자(* .doc; *. txt; * .pst)
    ex_blocklevel   = models.TextField()                                                            # Block-Level Backup 확장자(*.pst;)
    ex_ebook        = models.TextField()                                                            # e-book and New Year's card data 확장자
    ex_office       = models.TextField()                                                            # 오피스파일 확장자
    ex_account      = models.TextField()                                                            # 회계파일 확장자
    ex_exclusion    = models.TextField()                                                            # 전체 제외항목
    # ex_policyid     = models.ForeignKey('Policy', on_delete=models.CASCADE, db_column='bp_id')   # 정책 ID
    ex_policyid      = models.IntegerField()

    class Meta:
        db_table = 'box_policyextension'

    def __str__(self):
        return self.ex_policyid + "_" + self.ex_id


class BoxPolicyfiles(models.Model):
    bf_id           = models.IntegerField(primary_key=True)                                         # 정책파일 ID
    bf_type         = models.CharField(max_length=1)                                                # 파일타입(G:일반스토리지 파일, C:콜드스토리 파일, O:OCR 파일, E:확장자, D:듀얼백업)
    bf_filepath     = models.CharField(max_length=200)                                              # 파일경로
    bf_folderpath   = models.CharField(max_length=200)                                              # 폴더경로
    bf_createdate   = models.DateTimeField(auto_now_add=True)                                       # 생성일
    bf_extensionchk = models.CharField(max_length=1)                                                # 확장자나 조건식 필터(Y:사용)
    bf_filetypechk  = models.CharField(max_length=1)                                                # 파일유형 표현식(Y:포함, N:제외)
    bf_regexchk     = models.CharField(max_length=1)                                                # 정규식 사용여부(Y:사용)
    bf_expression   = models.CharField(max_length=500)                                              # 표현식
    bf_filebackchk  = models.CharField(max_length=1)                                                # 파일백업 여부(Y:사용)
    bf_size         = models.IntegerField()                                                         # 파일 사이즈
    bf_volumechk    = models.CharField(max_length=1)                                                # 파일단위(G:GB, M:MB)
    bf_datebackchk  = models.CharField(max_length=1)                                                # 날짜백업(Y:사용)
    bf_dateback     = models.DateTimeField()                                                        # 백업일
    # bf_policyid     = models.ForeignKey('BoxPolicy', on_delete=models.CASCADE, db_column='bf_policyid')   # 정책 ID
    bf_policyid     = models.IntegerField()
    bf_div          = models.IntegerField()

    class Meta:
        db_table = 'box_policyfiles'

    def __str__(self):
        return self.bf_policyid + "_" + self.bf_id


class BoxPolicypermission(models.Model):
    pp_id           = models.IntegerField(primary_key=True)                                         # 정책권한 ID
    pp_deletechk    = models.CharField(max_length=1, default='N')                                   # web관리 - 데이터 삭제 활성화 (Y:활성, N:비활성)
    pp_sharingchk   = models.CharField(max_length=1, default='N')                                   # web관리 - 공유 활성화 (Y:활성, N:비활성)
    pp_editchk      = models.CharField(max_length=1, default='N')                                   # web관리 - 로그인 이메일주소 변경 활성화 (Y:활성, N:비활성)
    pp_pwchk        = models.CharField(max_length=1, default='N')                                   # web관리 - 암호변경 활성화 (Y:활성, N:비활성)
    pp_changechk    = models.CharField(max_length=1, default='N')                                   # web관리 - 사용자 이름 변경 활성화 (Y:활성, N:비활성)
    pp_clientdiv    = models.CharField(max_length=1, default='P')                                   # 클라이언트의 권한(P:클라이언트 암호를 설정, A:AOSBOX AI PLUS 권한의 사용자)
    pp_pluspw       = models.IntegerField()                                                         # 클라이언트 암호
    pp_backupchk    = models.CharField(max_length=1, default='N')                                   # 클라이언트 권한 - 지금 백업 활성화 (Y:활성, N:비활성)
    pp_pausechk     = models.CharField(max_length=1, default='N')                                   # 클라이언트 권한 - 일시중지 활성화(Y:활성, N:비활성)
    pp_terminate    = models.CharField(max_length=1, default='N')                                   # 클라이언트 권한 - 종료 활성화(Y:활성, N:비활성)
    pp_remove       = models.CharField(max_length=1, default='N')                                   # AOSBOX의 제거를 허용(Y:허용, N:비허용)
    # pp_policyid     = models.ForeignKey('Policy', on_delete=models.CASCADE, db_column='pp_policyid')   # 정책 ID
    pp_policyid     = models.IntegerField()

    class Meta:
        db_table = 'box_policypermission'

    def __str__(self):
        return self.pp_policyid + "_" + self.pp_id


class BoxPolicysetting(models.Model):
    ps_id            = models.IntegerField(primary_key=True)                                        # 정책설정 ID
    ps_hidefile      = models.CharField(max_length=1)                                               # 숨겨진 파일포함
    ps_battery       = models.CharField(max_length=1)                                               # 배터리모드 활성화
    ps_presentation  = models.CharField(max_length=1)                                               # 프레젠테이션모드 활성화
    ps_policysetting = models.CharField(max_length=1)                                               # 컴퓨터 시작시 AOSBOX AI plus를 시작
    ps_multithread   = models.CharField(max_length=1)                                               # 멀티스레드로 업로드
    ps_lan           = models.CharField(max_length=1)                                               # 업로드 연결방법(유선 LAN)
    ps_wifi          = models.CharField(max_length=1)                                               # 업로드 연결방법(무선 LAN - WiFi)
    ps_lte           = models.CharField(max_length=1)                                               # 업로드 연결방법(모바일 데이터 통신 3G / LTE)
    ps_schedulediv   = models.CharField(max_length=1, default='G')                                  # 백업일정선택(G:간격으로 실행, S:일정에따라 실행)
    ps_stime         = models.IntegerField()                                                        # 간격 실행시간
    ps_itime         = models.IntegerField()                                                        # 무결성 검사빈도 시간
    ps_backtime      = models.IntegerField()                                                        # 블록 백업 실행간격 시간
    ps_starttime     = models.DateTimeField()                                                       # 일정 시작시간
    ps_endtime       = models.DateTimeField()                                                       # 일정 종료시간
    ps_netdiv        = models.CharField(max_length=1, default='N')                                  # 네트워크 대역폭 조정 활성화(Y:활성화)
    ps_upspeed       = models.IntegerField()                                                        # 업로드속도
    ps_banddiv       = models.CharField(max_length=1, default='N')                                  # 대역 조정 일정(Y:활성화)
    ps_bandstarttime = models.DateTimeField()                                                       # 대역조정 시작시간
    ps_bandendtime   = models.DateTimeField()                                                       # 대역조정 종료시간
    ps_policyid   = models.IntegerField()
    ps_endtimechk = models.CharField(max_length=1)
    ps_weekday = models.CharField(max_length=45)
    # ps_policyid      = models.ForeignKey('Policy', on_delete=models.CASCADE, db_column='ps_policyid')  # 정책 ID

    class Meta:
        db_table = 'box_policysetting'

    def __str__(self):
        return self.pp_policyid + "_" + self.ps_id



class Policy(models.Model):
    bp_id           = models.AutoField(primary_key=True)  # 정책 ID
    bp_name         = models.CharField(max_length=200)                      # 정책 이름
    bp_createdate   = models.DateTimeField(auto_now_add=True)               # 생성일
    bp_modifydate   = models.DateTimeField(auto_now=True)                   # 수정일
    bp_dualbackchk  = models.CharField(max_length=1)                        # 이중백업 이중 백업 활성화 여부(Y:활성, N:비활성)
    bp_dualpath     = models.CharField(max_length=200)                      # 이중백업 활성화 경로
    bp_dualsizechk  = models.CharField(max_length=1)                        # 이중백업의 크기 제한(Y:제한, N:비제한)
    bp_dualsize     = models.IntegerField()                                 # 이중백업의 제한크기
    bp_resellerid    = models.IntegerField()                                 # 어카운트 ID => 그룹 ID로 변경해야할 듯

    class Meta:
        managed = False
        db_table = 'box_policy'


class BoxVariable(models.Model):
    bv_id = models.AutoField(primary_key=True)
    bv_variable = models.CharField(max_length=100)
    bv_macpath = models.CharField(max_length=200)
    bv_windowspath = models.CharField(max_length=200)

    class Meta:
        db_table = 'box_variable'


class BoxPolicyfolderfiles(models.Model):
    bf_id           = models.IntegerField(primary_key=True)                                         # 정책파일 ID
    bf_type         = models.CharField(max_length=1)                                                # 파일타입(G:일반스토리지 파일, C:콜드스토리 파일, O:OCR 파일, E:확장자, D:듀얼백업)
    bf_filepath     = models.CharField(max_length=200)                                              # 파일경로
    bf_folderpath   = models.CharField(max_length=200)                                              # 폴더경로
    bf_createdate   = models.DateTimeField(auto_now_add=True)                                       # 생성일
    bf_extensionchk = models.CharField(max_length=1)                                                # 확장자나 조건식 필터(Y:사용)
    bf_filetypechk  = models.CharField(max_length=1)                                                # 파일유형 표현식(Y:포함, N:제외)
    bf_regexchk     = models.CharField(max_length=1)                                                # 정규식 사용여부(Y:사용)
    bf_expression   = models.CharField(max_length=500)                                              # 표현식
    bf_filebackchk  = models.CharField(max_length=1)                                                # 파일백업 여부(Y:사용)
    bf_size         = models.IntegerField()                                                         # 파일 사이즈
    bf_volumechk    = models.CharField(max_length=1)                                                # 파일단위(G:GB, M:MB)
    bf_datebackchk  = models.CharField(max_length=1)                                                # 날짜백업(Y:사용)
    bf_dateback     = models.DateTimeField()                                                        # 백업일
    # bf_policyid     = models.ForeignKey('BoxPolicy', on_delete=models.CASCADE, db_column='bf_policyid')   # 정책 ID
    bf_policyid     = models.IntegerField()
    bf_div          = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'box_policyfiles'


class Policypermission(models.Model):
    pp_id           = models.IntegerField(primary_key=True)                                         # 정책권한 ID
    pp_deletechk    = models.CharField(max_length=1, default='N')                                   # web관리 - 데이터 삭제 활성화 (Y:활성, N:비활성)
    pp_sharingchk   = models.CharField(max_length=1, default='N')                                   # web관리 - 공유 활성화 (Y:활성, N:비활성)
    pp_editchk      = models.CharField(max_length=1, default='N')                                   # web관리 - 로그인 이메일주소 변경 활성화 (Y:활성, N:비활성)
    pp_pwchk        = models.CharField(max_length=1, default='N')                                   # web관리 - 암호변경 활성화 (Y:활성, N:비활성)
    pp_changechk    = models.CharField(max_length=1, default='N')                                   # web관리 - 사용자 이름 변경 활성화 (Y:활성, N:비활성)
    pp_clientdiv    = models.CharField(max_length=1, default='P')                                   # 클라이언트의 권한(P:클라이언트 암호를 설정, A:AOSBOX AI PLUS 권한의 사용자)
    pp_pluspw       = models.IntegerField()                                                         # 클라이언트 암호
    pp_backupchk    = models.CharField(max_length=1, default='N')                                   # 클라이언트 권한 - 지금 백업 활성화 (Y:활성, N:비활성)
    pp_pausechk     = models.CharField(max_length=1, default='N')                                   # 클라이언트 권한 - 일시중지 활성화(Y:활성, N:비활성)
    pp_terminate    = models.CharField(max_length=1, default='N')                                   # 클라이언트 권한 - 종료 활성화(Y:활성, N:비활성)
    pp_remove       = models.CharField(max_length=1, default='N')                                   # AOSBOX의 제거를 허용(Y:허용, N:비허용)
    # pp_policyid     = models.ForeignKey('Policy', on_delete=models.CASCADE, db_column='pp_policyid')   # 정책 ID
    pp_policyid     = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'box_policypermission'




