from django.shortcuts import render

from django.views import View
from django.http.response import HttpResponseRedirect, HttpResponse, responses
from rest_framework.response import Response
from rest_framework.decorators import api_view

from django.shortcuts import redirect

from . import google
from django.views.decorators.csrf import csrf_exempt
import json
import shutil
import uuid
import boto3

from ..service import FileExplorer

from .models import Googledrivesettings, Googledrivefiles
from .serializers import GoogleDriveSettingsSerializer, BoxFileSerializer

from django.http.response import JsonResponse

from rest_framework import views
from rest_framework.response import Response
from django.http.response import HttpResponse, StreamingHttpResponse
from django.db import transaction, connection
from wsgiref.util import FileWrapper
import os
from conf import settings
from ..models import BoxUsers, BoxFile

from os import remove

from common.type.exception import Code

# Create your views here.

ACCESS_ID = settings.S3_ACCESS_ID
ACCESS_KEY = settings.S3_ACCESS_KEY


def google_login(request):
    google_sign_in = google.GoogleSignIn()
    auth_url = google_sign_in.google_auth()

    return HttpResponseRedirect(auth_url)


@api_view(['POST'])
def callback(request):
    googleSignIn = google.GoogleSignIn()
    data = googleSignIn.google_callback(request)

    if data == "error":
        return Response({'code': Code.INTERNAL_SERVER_ERROR.value, 'message': Code.INTERNAL_SERVER_ERROR.name})
    else:
        storage_service = {
            'google_drive': True
        }
        result = {
            'data': data,
            'storage_service': storage_service
        }
        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'data': result})


@api_view(['GET'])
def google_drive(request):
    googleSignIn = google.GoogleSignIn()
    list = googleSignIn.get_google_drive(request)
    result = {}
    result['list'] = list
    # result['fileList'] = fileList
    return Response({'code': "success", 'data': result})


class downloadFile(views.APIView):
    @transaction.atomic
    def post(self, request):
        params = request.POST
        payload = request.body

        print("parmas", params)
        print("payload", payload)

        folders = json.loads(params.get('folders'))
        files = json.loads(params.get('files'))
        user = BoxUsers.objects.get(pk=payload['userId'])

        tempPath = params.get('tempPath')

        tid = transaction.savepoint()

        tempFileName = tempPath

        if (tempPath == '' or tempPath is None):
            tempPath = settings.MEDIA_ROOT + "temp/" + str(uuid.uuid4())
        else:
            tempPath = settings.MEDIA_ROOT + "temp/" + tempPath

        if not os.path.isdir(tempPath):
            os.mkdir(tempPath)

        fileList = []
        if (len(files) > 0):
            list = BoxFile.objects.filter(fi_id__in=files)
            result = FileExplorer.fileDown(list, tempPath, user)
            fileList.extend(result)

        if (len(folders) > 0):
            result = FileExplorer.folderDown(folders, tempPath, user)
            fileList.extend(result)

        downFileSize = 0
        for file in fileList:
            downFileSize = downFileSize + file.fi_file_size

        # 파일 사이즈 리턴
        if downFileSize > 2 * 1024 * 1024 * 1024:
            httpResponse = HttpResponse(status=200)
            httpResponse['Content-Length'] = 0
            shutil.rmtree(tempPath)
            transaction.savepoint_rollback(tid)
            return httpResponse

        if len(files) == 1 and len(folders) == 0:

            filePath = tempPath + "/" + file.fi_name

            s3 = boto3.client('s3', aws_access_key_id=ACCESS_ID,
                              aws_secret_access_key=ACCESS_KEY)

            with open(filePath, 'wb') as f:
                s3.download_fileobj(settings.S3_BUCKET_NAME, file.fi_path, f)
            contentType = fileList[0].fi_mimetype
            fileName = fileList[0].fi_name

            with open(filePath, 'rb') as resultFile:
                response = HttpResponse(resultFile, content_type=contentType)

            shutil.rmtree(tempPath)
        else:
            os.system("bash /home/aos/s3down4.sh {0} {1}".format(tempPath + '/s3download.list', tempFileName))
            # 압축
            # with zipfile.ZipFile(tempPath + ".zip", 'w', zipfile.ZIP_DEFLATED) as zip:
            #     for folder, subfolders, files in os.walk(tempPath):
            #
            #         for dir in subfolders:
            #             absolute_path = os.path.join(folder, dir)
            #             relative_path = absolute_path.replace(tempPath + '/', '')
            #             zip.write(absolute_path, relative_path)
            #
            #         for file in files:
            #             absolute_path = os.path.join(folder, file)
            #             relative_path = absolute_path.replace(tempPath + '/', '')
            #             zip.write(absolute_path, relative_path)

            # commendTxt = '7z a {0} {1}'.format(tempPath + '.zip', tempPath + "/*")
            # result = os.system(commendTxt)
            # if result < 0:
            #     Exception('zip Exception')

            resultFile = open(tempPath + '.zip', 'rb')
            contentType = 'application/zip'

            # shutil.rmtree(tempPath)
            response = StreamingHttpResponse(FileWrapper(resultFile, 8192), content_type=contentType)
            # remove(tempPath + '.zip')

        # except Exception as e:
        #
        #     print('****************')
        #     print(e)
        #     print('****************')
        #     transaction.rollback(tid)

        # response['Content-Disposition'] = 'attachment; filename="%s"' % fileName

        return response


class deleteTempPath(views.APIView):

    def post(self, request):
        params = request.POST
        payload = request.body

        print("deltetmpepath", params)

        tempPath = params.get('tempPath')
        tempPath = settings.USER_TEMP_DIR_PATH + "/" + tempPath + '.zip'

        if (os.path.isfile(tempPath)):
            remove(tempPath)
        # shutil.rmtree(tempPath)

        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name})


class get_storage_service(views.APIView):

    def post(self, request):
        params = request.data
        payload = request.body

        storage = params['storage']

        print("payload=================", payload)

        if storage.get('google_drive') == True:
            google_drive_settings = Googledrivesettings.objects.get(userid=payload['userId'])
            google_drive_settings_info = GoogleDriveSettingsSerializer(google_drive_settings).data

        result = {}
        result['google_drive_settings'] = google_drive_settings_info
        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'data': result})


class get_folder_list(views.APIView):

    def post(self, request):
        params = request.POST
        payload = request.body

        print("params=================", params)

        get_google_drive_file_id = Googledrivefiles.objects.get(box_file_id=params['id'])
        google_dirve_file_list = Googledrivefiles.objects.filter(parentid=get_google_drive_file_id.googledrivefileid)

        parentId = get_google_drive_file_id.googledrivefileid

        print("parentId", parentId)

        query = '''SELECT 
                    bf.fi_id, 
                    bf.fi_name, 
                    bf.fi_is_root,
                    bf.fi_path,
                    bf.fi_status,
                    bf.fi_is_folder,
                    bf.fi_icon_type, 
                    bf.fi_file_size, 
                    bf.fi_ext,
                    bf.fi_favorite,
                    bf.fi_createdate,
                    bf.fi_modifydate, 
                    bf.fi_backupdate 
                    FROM box_files bf INNER JOIN googledrivefiles gd ON bf.fi_id = gd.box_file_id 
                    WHERE gd.ParentID = '%s' order by fi_name asc  ''' % (parentId)

        box_file = BoxFile.objects.raw(query)

        print("query", query)

        result = {}
        result['list'] = BoxFileSerializer(box_file, many=True).data
        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'data': result})


class disconnected_google_drive(views.APIView):

    def post(self, request):
        params = request.POST
        payload = request.body

        print("params=================", params)

        # google drvie 연결정보 및 등록 파일 전부 삭제

        Googledrivesettings.objects.get(userid=payload['userId']).delete()
        BoxFile.objects.get(fi_bsusserid=payload['userId']).delete()

        result = {}

        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'data': result})


class delete(views.APIView):

    def post(self, request):
        params = request.data['list']
        payload = request.body

        print("params=================", params)

        # TODO 하위폴더까지 상태 변경!!
        for item in params:
            print("params", item['fi_id'])
            box_file_update = BoxFile.objects.get(fi_id=item['fi_id'])
            box_file_update.fi_status = 'T'
            box_file_update.save()

        # google drvie 연결정보 및 등록 파일 전부 삭제
        result = {}
        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'data': result})
