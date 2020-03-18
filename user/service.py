import uuid
import boto3
from conf import settings
from datetime import datetime, timedelta
from boto3.s3.transfer import S3Transfer
from .models import BoxFile

import os
ACCESS_ID = settings.S3_ACCESS_ID
ACCESS_KEY = settings.S3_ACCESS_KEY


class FileExplorer:
    @classmethod
    def fileUpload(self, file):
        now = datetime.now()
        year = str(now.year)
        month = '0' + str(now.month) if now.month < 10 else str(now.month)
        day = '0' + str(now.day) if now.day < 10 else str(now.day)
        envName = 'env-'

        s3 = boto3.client('s3', aws_access_key_id=ACCESS_ID,
                          aws_secret_access_key=ACCESS_KEY)

        extension = file.name.split("/")[-1]
        file_extension = extension.split(".")[-1]

        # TODO 파일 확장자 없이 파일명이 4자 이하일 경우 처리가 필요
        if len(file_extension) < 4:
            uniqueFileName = str(uuid.uuid4()) + '.' + file_extension
        else:
            uniqueFileName = str(uuid.uuid4())

        serverPath = envName + "/" + year + "/" + month + "/" + day + "/" + uniqueFileName

        try:
            s3.upload_fileobj(file, settings.S3_BUCKET_NAME, serverPath)
        except s3.exceptions as e:
            return False

        return serverPath

    @classmethod
    def fileDown(self, files, tempPath, user):

        s3 = boto3.client('s3', aws_access_key_id=ACCESS_ID,
                          aws_secret_access_key=ACCESS_KEY)

        boto3.set_stream_logger('botocore', level='DEBUG')
        list = BoxFile.objects.filter(fi_id__in=files)

        for file in list:

            # if file.is_trash:
            #     continue

            print("file-------------", file)

            # # folder = file.folder_id
            # folder = ""

            filePath = tempPath + "/" + file.fi_name
            count = 0
            while True:
                if not os.path.isfile(filePath):
                    with open(filePath, 'wb') as f:
                        s3.download_fileobj(settings.S3_BUCKET_NAME, file.fi_path, f)
                    break
                else:
                    count += 1
                    extension = "." + file.extension
                    fileName = file.name.replace(extension, "_" + str(count) + extension)
                    filePath = tempPath + "/" + fileName

            # 로그 작성: 파일 다운로드

        return list
