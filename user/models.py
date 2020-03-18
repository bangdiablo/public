from django.db import models

from .management.models import Policy
from .main.models import BoxUsers
from reseller.models import Reseller


class BoxStoragediv(models.Model):
    sd_code = models.CharField(primary_key=True, max_length=1)
    sd_name = models.CharField(max_length=50)
    sd_category = models.CharField(max_length=50, blank=True, null=True)
    box_storagedivcol = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'box_storagediv'


class BoxUserstorage(models.Model):
    bs_id = models.AutoField(primary_key=True)
    bs_storage_id = models.CharField(max_length=255, unique=True)
    bs_name = models.CharField(max_length=100, blank=True, null=True)
    bs_sdcode = models.ForeignKey(BoxStoragediv, models.DO_NOTHING, db_column='bs_sdcode')
    bs_status = models.IntegerField(default=1)
    bs_token = models.CharField(max_length=45, blank=True, null=True)
    bs_gnrlsto = models.IntegerField(blank=True, null=True)
    bs_coldsto = models.IntegerField(blank=True, null=True)
    bs_ocr = models.IntegerField(blank=True, null=True)
    bs_gnrllimit = models.IntegerField(blank=True, null=True)
    bs_coldlimit = models.IntegerField(blank=True, null=True)
    bs_ocrlimit = models.IntegerField(blank=True, null=True)
    bs_logdate = models.DateTimeField(blank=True, null=True)
    bs_createdate = models.DateTimeField(blank=True, null=True)
    bs_downdate = models.DateTimeField(blank=True, null=True)
    bs_update = models.DateTimeField(blank=True, null=True)
    bs_email = models.CharField(max_length=200, blank=True, null=True)
    bs_phone = models.CharField(max_length=14, blank=True, null=True)
    bs_policyid = models.ForeignKey(Policy, models.DO_NOTHING, db_column='bs_policyid', blank=True, null=True)
    bs_userid = models.ForeignKey(BoxUsers, models.DO_NOTHING, db_column='bs_userid')
    bs_fileid = models.IntegerField(blank=True, null=True)
    bs_system = models.CharField(max_length=100, blank=True, null=True)
    bs_version = models.CharField(max_length=100, blank=True, null=True)
    bs_os = models.CharField(max_length=100, blank=True, null=True)
    bs_os_version = models.CharField(max_length=100, blank=True, null=True)
    bs_os_bit = models.CharField(max_length=100, blank=True, null=True)
    bs_backup = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'box_userstorage'


class BoxFile(models.Model):
    fi_bsusserid = models.IntegerField(blank=True, null=True)
    fi_bsid = models.ForeignKey(BoxUserstorage, models.DO_NOTHING, db_column='fi_bsid', null=True)
    fi_bsdiv = models.CharField(max_length=1)
    fi_bsname = models.CharField(max_length=100)
    fi_id = models.AutoField(primary_key=True)
    fi_parent_id = models.IntegerField(blank=True, null=True)
    fi_is_root = models.BooleanField(default=False)
    fi_is_folder = models.BooleanField(default=False)
    fi_icon_type = models.CharField(max_length=100, blank=True, null=True)
    fi_name = models.CharField(max_length=100, blank=True, null=True)
    fi_path = models.TextField(blank=True, null=True)
    fi_status = models.CharField(max_length=1)
    fi_file_size = models.BigIntegerField(default=0)
    fi_ext = models.CharField(max_length=10, blank=True, null=True)
    fi_favorite = models.CharField(max_length=1)
    fi_createdate = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    fi_modifydate = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    fi_backupdate = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    fi_thumb = models.CharField(max_length=200, blank=True, null=True)
    fi_tags = models.CharField(max_length=200, blank=True, null=True)
    fi_mimetype = models.CharField(max_length=30, blank=True, null=True)
    fi_meta_image_px_size = models.CharField(db_column='fi_meta.image.px_size', max_length=10, blank=True,
                                             null=True)  # Field renamed to remove unsuitable characters.
    fi_meta_doc_author = models.CharField(db_column='fi_meta.doc.author', max_length=50, blank=True,
                                          null=True)  # Field renamed to remove unsuitable characters.
    fi_meta_doc_page = models.IntegerField(db_column='fi_meta.doc.page', blank=True,
                                           null=True)  # Field renamed to remove unsuitable characters.
    fi_meta_video_quality = models.CharField(db_column='fi_meta.video.quality', max_length=20, blank=True,
                                             null=True)  # Field renamed to remove unsuitable characters.
    fi_meta_video_bitrate = models.CharField(db_column='fi_meta.video.bitrate', max_length=20, blank=True,
                                             null=True)  # Field renamed to remove unsuitable characters.
    fi_meta_video_duration = models.IntegerField(db_column='fi_meta.video.duration', blank=True,
                                                 null=True)  # Field renamed to remove unsuitable characters.
    fi_meta_sound_duration = models.IntegerField(db_column='fi_meta.sound.duration', blank=True,
                                                 null=True)  # Field renamed to remove unsuitable characters.
    box_file_newcol = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'box_file'


# 라이센스 키
class BoxLicensekey(models.Model):
    li_id = models.AutoField(primary_key=True)              # 라이센스 ID
    li_licensekey = models.CharField(max_length=16)         # 라이센스 키
    li_planid = models.IntegerField()                       # 플랜 ID
    li_createdate = models.DateTimeField(auto_now_add=True) # 생성일
    li_activatedate = models.DateTimeField()                # 활성일
    li_canceldate = models.DateTimeField()                  # 취소일
    li_cost = models.FloatField()                           # 비용
    reseller = models.ForeignKey(Reseller, models.SET_NULL, db_column='li_resellerid', null=True) # 리셀러 ID
    li_status = models.IntegerField()                       # 라이센스상태(1:활성, 2:만료, 3:취소, 4:삭제, 5:대기)
    li_usernum = models.IntegerField()                      # 사용자수

    class Meta:
        managed = False
        db_table = 'box_licensekey'


# 라이센스 키 - 유저 맵핑
class BoxLicensemap(models.Model):
    lu_id = models.AutoField(primary_key=True)                                               # 라이센스 매핑 ID
    boxLicensekey = models.ForeignKey(BoxLicensekey, models.CASCADE, db_column='lu_licenseid')  # 라이센스 ID
    boxUser = models.ForeignKey(BoxUsers, models.CASCADE, db_column='lu_userid')                # 사용자 ID
    lu_flag = models.CharField(max_length=1)                                           # 라이센스 flag(Y:사용, N: 미사용)

    class Meta:
        managed = False
        db_table = 'box_licensemap'


# 코드
class BoxCode(models.Model):
    bc_id = models.AutoField(primary_key=True)
    bc_code = models.CharField(max_length=5, unique=True)
    pcode = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, to_field='bc_code', db_column='bc_pcode', related_name='child')
    bc_name = models.CharField(max_length=45)
    bc_explain = models.CharField(max_length=100)
    bc_createdate = models.DateTimeField(auto_now_add=True)
    bc_modifydate = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'box_code'


# 설정
class BoxSetting(models.Model):
    st_id = models.AutoField(primary_key=True)                      # 보존설정 ID
    st_storagediv = models.CharField(max_length=1, default='F')     # 일반 저장소 유지구분(F:파일유지버전, D:파일삭제기간)
    stovalCode = models.ForeignKey(BoxCode, on_delete=models.SET_NULL, null=True,
                                   to_field='bc_code', db_column='st_storageval',
                                   related_name='storageval')       # 일반 저장소 유지 값
    st_colddiv = models.CharField(max_length=1, default='F')        # 콜드스토리지 유지구분(F:파일유지버전, D:파일삭제기간)
    coldvalCode = models.ForeignKey(BoxCode, on_delete=models.SET_NULL, null=True,
                                    to_field='bc_code', db_column='st_coldval',
                                    related_name='coldval')         # 콜드스토리지 유지 값
    retperfileCode = models.ForeignKey(BoxCode, on_delete=models.SET_NULL, null=True,
                                       to_field='bc_code', db_column='st_retperfile',
                                       related_name='retperfile')   # 삭제 된 파일의 보유기간
    st_period = models.CharField(max_length=1, default='N')         # 클라이언트 스토리지 경고 설정(Y:경고숨김, N:경고)
    accountUser = models.OneToOneField(BoxUsers, on_delete=models.CASCADE, db_column='st_accountid')                    # 어카운트 ID

    class Meta:
        managed = False
        db_table = 'box_setting'


# 설정 (상세)
class BoxSettingadvance(models.Model):
    sa_id = models.AutoField(primary_key=True)                      # 보존설정(상세) ID
    boxUser = models.ForeignKey(BoxUsers, on_delete=models.CASCADE, db_column='sa_userid')              # 사용자 ID
    boxUserstorage = models.ForeignKey(BoxUserstorage, on_delete=models.CASCADE, db_column='sa_stoid')  # 스토리지 ID
    sa_path = models.TextField()                                    # 디렉토리 경로
    sa_div = models.CharField(max_length=1, default='F')            # 보존 설정(상세) 구분(F:파일에유지, D:이전세대 삭제)
    boxCode = models.ForeignKey(BoxCode, on_delete=models.SET_NULL, null=True, to_field='bc_code',
                                db_column='sa_settingval')  # 보존설정(상세) 구분값
    sa_modifydate = models.DateTimeField(auto_now=True)  # 수정일자

    class Meta:
        managed = False
        db_table = 'box_settingadvance'
        unique_together = ('boxUser', 'boxUserstorage',)


# 그룹
class BoxGroup(models.Model):
    bg_id = models.AutoField(primary_key=True)
    bg_groupname = models.CharField(max_length=100) # 그룹명

    class Meta:
        managed = False
        db_table = 'box_group'


# 그룹멤버
class BoxGroupmember(models.Model):
    gm_id = models.AutoField(primary_key=True)                                               # 그룹멤버 ID
    boxGroup = models.ForeignKey(BoxGroup, on_delete=models.CASCADE, db_column='gm_groupid') # 그룹 ID
    boxUser = models.ForeignKey(BoxUsers, on_delete=models.CASCADE, db_column='gm_userid')   # 유저 ID

    class Meta:
        managed = False
        db_table = 'box_groupmember'
        unique_together = ('boxGroup', 'boxUser',)
