from __future__ import print_function
import google_auth_oauthlib
import google_auth_oauthlib.flow
import httplib2
import os
from oauth2client.file import Storage, client
from oauth2client import tools
from django.db import transaction, connection

from datetime import datetime
from .models import Googledrivesettings, Googledrivefiles
from ..models import BoxFile
from django.utils import timezone

from .serializers import GoogleDriveFilesSerializer, BoxFileSerializer

from ..service import FileExplorer
import io
import json
from googleapiclient.http import MediaIoBaseDownload

from conf import settings
from apiclient import errors

from pytz import timezone

import shutil

import google.oauth2.credentials

from rest_framework.response import Response

from common.type.exception import Code

import requests

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from apiclient import discovery, errors

# 클라이언트 ID, client_secret 설정
CLIENT_ID = "709956208735-djf9haapuhi2qn89ancedvkmlkbi8rer.apps.googleusercontent.com"
CLIENT_SECRET = "ztyrSUKTAqMWB7WQbR3AB_fK"

# https://developers.google.com/drive/api/v2/about-auth
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# credentials = google_auth_oauthlib.get_user_credentials(
#     scopes, client_id, client_secret
# )

_google_callback = "http://127.0.0.1:8000/box/storage_service/connect_to_google_drive/"

REDIRECT_URI = "http://127.0.0.1:8000/box/storage_service/connect_to_google_drive/"

_client_secrets_file = "D://workspace/db_project_2019/SITE/SiteBack/user/storage_service/google_signin.json"

CLIENT_SECRET_FILE = 'google_signin.json'

APPLICATION_NAME = 'Drive API Python'


def get_credentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_cred():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')

    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'credentials.json')

    store = Storage(credential_path)
    creds = store.get()

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    else:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(_client_secrets_file, scopes=SCOPES)
        flow.redirect_uri = _google_callback
        google_auth_url = flow.authorization_url(access_type='offline', include_granted_scopes='true')
        # flow = client.flow_from_clientsecrets(_client_secrets_file, SCOPES)
        # creds = tools.run_flow(flow, store)

    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))


from oauth2client.client import flow_from_clientsecrets

from os import path

CREDS_FILE = os.path.join(os.path.dirname(__file__), 'credentials_gow.json')
from apiclient import errors


class GoogleSignIn():
    @transaction.atomic
    def google_callback(self, request):

        user_id = request.body.get("userId")

        # credential 파일 저장
        storage = Storage(CREDS_FILE)
        credentials = storage.get()
        if credentials is None:

            # 엑세스 코드
            code = request.data['code']
            try:
                credentials = client.credentials_from_code(CLIENT_ID, CLIENT_SECRET, scope='', code=code)
            except:
                return "error"

            id_token = credentials.id_token
            # 구글 드라이브 인증 정보 저장
            # todo 파일 요약정보 컬럼 추가 할것!
            google_drive_settings = Googledrivesettings()
            google_drive_settings.accesstoken = code
            google_drive_settings.refreshaccesstoken = credentials.refresh_token
            google_drive_settings.userid = user_id
            google_drive_settings.email = id_token['email']
            google_drive_settings.flag = 'N'
            google_drive_settings.save()
            storage.put(credentials)

            #  구글드라이브 API 연결후 파일목록취득 및 파일다운로드
            rtn = self.list_files(request)
        else:
            rtn = self.list_files(request)

        return rtn

    #  구글드라이브 최초 연결시 파일목록 다운로드후 s3에 저장
    # TODO 설정에 따라서 s3에 저장하는것과 구글 링크로 변경됨
    # TODO 24시간 단위로 스토리지 서비스와의 싱크가 필요
    @transaction.atomic
    def list_files(self, request):

        user_id = request.body.get("userId")
        storage = Storage(CREDS_FILE)
        credentials = storage.get()

        now = datetime.now()
        year = str(now.year)
        month = '0' + str(now.month) if now.month < 10 else str(now.month)
        day = '0' + str(now.day) if now.day < 10 else str(now.day)

        tmp_path = os.path.join(settings.MEDIA_ROOT + str(user_id) + "/" + year + month + day + "/")

        http = httplib2.Http()
        http = credentials.authorize(http)

        drive_service = build("drive", "v2", http=http)

        print("drive_service", drive_service)

        for x in self.get_list(drive_service):

            labels = x.get('labels')
            if (x.get('title')) and x.get('alternateLink') and x.get('shared') == False and labels['trashed'] == False:

                # 구글 드라이브 관련 메타 데이타 저장
                box_file = BoxFile()
                box_file.fi_bsusserid = user_id
                box_file.fi_bsdiv = "V"
                box_file.fi_bsname = "GD"
                box_file.fi_name = x.get('title')
                box_file.fi_path = x.get('alternateLink')
                print("구글 드라이브 내용", x)

                # 폴더 정보 가져오기
                # for y in self.print_files_in_folder(drive_service, )
                # 구글 드라이브에 파일이 저장되어 있을경우 파일을 다운로드 하여 S3에 업로드
                # 그 외에 링크는 해당 링크 정보 저장
                if x.get('webContentLink') is not None:
                    # fileid를 가지고 구글드라이브에서 파일정보를 가져옴
                    file = drive_service.files().get_media(fileId=x.get('id'))

                    print("tmp_path=================", tmp_path)

                    if not os.path.isdir(tmp_path):
                        os.mkdir(tmp_path)
                    file_path = tmp_path + x.get('title')

                    fh = io.FileIO(file_path, 'wb')
                    downloader = MediaIoBaseDownload(fh, file)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print("Download %d%%" % int(status.progress() * 100))

                    if done is True:
                        with open(file_path, 'rb') as data:
                            server_path = FileExplorer.fileUpload(file=data)
                            data.close()

                        box_file.fi_name = data.name.split("/")[-1]
                        box_file.fi_path = server_path

                # 구글드라이브 관련 정보 별도로 저장
                google_drive = Googledrivefiles()

                # 부모폴더 처리
                parent_info = x.get('parents')
                if parent_info:
                    parent = parent_info[0]
                    if parent['isRoot'] == True:
                        box_file.fi_is_root = True
                    else:
                        box_file.fi_is_root = False
                        param = {}
                        children = drive_service.children().list(folderId=x.get('id'), **param).execute()
                        print("children===============", children)

                    google_drive.parentid = parent['id']

                # 폴더여부 확인 및 파일 아이콘 타입 설정
                mimetype = x.get('mimeType')
                print("mimetype", mimetype)
                if mimetype == 'application/vnd.google-apps.folder':
                    box_file.fi_is_folder = True
                    box_file.fi_icon_type = 'folder'
                elif mimetype == 'application/vnd.google-apps.spreadsheet':
                    box_file.fi_icon_type = 'spreadsheet'
                elif mimetype == 'application/vnd.google-apps.presentation':
                    box_file.fi_icon_type = 'presentation'
                elif mimetype == 'application/vnd.google-apps.document':
                    box_file.fi_icon_type = 'document'
                elif mimetype == 'application/vnd.ms-excel':
                    box_file.fi_icon_type = 'ms-excel'
                elif mimetype == 'image/png' or mimetype == 'image/jpeg':
                    box_file.fi_icon_type = 'image'
                elif mimetype == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
                    box_file.fi_icon_type = 'presentation'
                else:
                    box_file.fi_icon_type = 'etc'

                box_file.fi_status = "G"
                box_file.fi_createdate = x.get('createdDate')
                box_file.fi_modifydate = x.get('modifiedDate')
                box_file.fi_file_size = x.get('fileSize')
                box_file.fi_mimetype = mimetype
                box_file.fi_ext = x.get('fileExtension')
                box_file.save()

                google_drive.box_file_id = box_file
                google_drive.filename = box_file.fi_name
                google_drive.filepath = x.get('webContentLink')
                google_drive.modifydate = x.get('modifiedDate')
                google_drive.mimetype = mimetype
                google_drive.googledrivefileid = x.get('id')

                google_drive.save()

        storage.delete()
        # # 구글드라이브에 있는 파일을 다운로드후 삭제
        # shutil.rmtree(tmp_path)

        return tmp_path

    def get_list(self, service):
        param = {}
        #
        # for x in self.list_files(drive_service):
        #     print("file _lst", x.get('title'))

        page_token = None
        while True:
            if page_token:
                param['pageToken'] = page_token
            files = service.files().list(**param).execute()
            for item in files['items']:
                yield item
            page_token = files.get('nextPageToken')
            if not page_token:
                break

    def get_google_drive(self, request):

        user_id = request.body.get("userId")
        folderList = BoxFile.objects.filter(fi_bsusserid=user_id, fi_bsname="GD", fi_status="G", fi_is_root=True,
                                            fi_is_folder=True).order_by('fi_name')
        folderList = BoxFileSerializer(folderList, many=True).data
        fileList = BoxFile.objects.filter(fi_bsusserid=user_id, fi_bsname="GD", fi_status="G",
                                          fi_is_root=True, fi_is_folder=False).order_by('-fi_name')
        fileList = BoxFileSerializer(fileList, many=True).data

        list = []
        list.extend(folderList)
        list.extend(fileList)
        return list

    def print_files_in_folder(service, folder_id):
        page_token = None
        while True:
            try:
                param = {}
                if page_token:
                    param['pageToken'] = page_token
                children = service.children().list(folderId=folder_id, **param).execute()

                for child in children.get('items', []):
                    yield child
                    print("child", child)
                    page_token = children.get('nextPageToken')
                if not page_token:
                    break
            except errors.HttpError:
                break
