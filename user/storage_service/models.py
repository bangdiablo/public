from django.db import models

from ..main.models import BoxUsers
from ..models import BoxFile
# from oauth2client.contrib.django_util.storage import DjangoORMStorage
# from oauth2client.contrib.django_util.models import CredentialsField


class Googledrivesettings(models.Model):
    id = models.IntegerField(db_column='ID', blank=True, primary_key=True)  # Field name made lowercase.
    accesstoken = models.CharField(db_column='AccessToken', max_length=512, blank=True,
                                   null=True)  # Field name made lowercase.
    refreshaccesstoken = models.CharField(db_column='RefreshAccessToken', max_length=512, blank=True,
                                          null=True)  # Field name made lowercase.
    nextstreamposition = models.CharField(db_column='NextStreamPosition', max_length=512, blank=True,
                                          null=True)  # Field name made lowercase.
    accountid = models.IntegerField(db_column='AccountID', blank=True, null=True)  # Field name made lowercase.
    userid = models.IntegerField(db_column='UserID', blank=True, null=True)  # Field name made lowercase.
    status = models.IntegerField(db_column='Status', blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True, auto_now_add=True)  # Field name made lowercase.
    errorcode = models.IntegerField(db_column='ErrorCode', blank=True, null=True)  # Field name made lowercase.
    errormessage = models.CharField(db_column='ErrorMessage', max_length=512, blank=True,
                                    null=True)  # Field name made lowercase.
    googledriveuserid = models.CharField(db_column='GoogleDriveUserID', max_length=64, blank=True,
                                         null=True)  # Field name made lowercase.
    machineid = models.CharField(db_column='MachineID', max_length=11, blank=True,
                                 null=True)  # Field name made lowercase.
    machineguid = models.CharField(db_column='MachineGUID', max_length=32, blank=True,
                                   null=True)  # Field name made lowercase.
    flag = models.CharField(db_column='Flag', max_length=11, blank=True, null=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=128, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=64, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'googledrivesettings'


# class CredentialsModel(models.Model):
#     id = models.ForeignKey(Googledrivesettings, primary_key=True, on_delete=models.DO_NOTHING)
#     # credential = CredentialsField()

class Googledrivefiles(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    googledrivefileid = models.CharField(db_column='GoogleDriveFileID', max_length=128)  # Field name made lowercase.
    box_file_id = models.ForeignKey(BoxFile, on_delete=models.CASCADE, db_column='box_file_id')
    filename = models.CharField(db_column='FileName', max_length=256)  # Field name made lowercase.
    filepath = models.CharField(db_column='FilePath', max_length=256)  # Field name made lowercase.
    filemd5 = models.CharField(db_column='FileMD5', max_length=80)  # Field name made lowercase.
    size = models.BigIntegerField(db_column='Size')  # Field name made lowercase.
    parentid = models.CharField(db_column='ParentID', max_length=128)  # Field name made lowercase.
    userid = models.IntegerField(db_column='UserID')  # Field name made lowercase.
    filetype = models.IntegerField(db_column='FileType')  # Field name made lowercase.
    mimetype = models.CharField(db_column='MimeType', max_length=256)  # Field name made lowercase.
    status = models.IntegerField(db_column='Status')  # Field name made lowercase.
    modifydate = models.DateTimeField(db_column='modifydate', auto_now_add=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='createdate', auto_now_add=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'googledrivefiles'
