from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response
from common.type.exception import Code
from rest_framework.decorators import api_view
import configparser

from .. import dynamo
import threading, time, os

from ..models import BoxUserstorage

from .serializers import BoxUserStorageSerializer


# Create your views here.
class DeviceName(views.APIView):

    def get(self, request):
        payload = request.body

        box_user_storage_list = []
        try:
            box_user_storage = BoxUserstorage.objects.filter(bs_userid=payload['userId'])
            box_user_storage_list = BoxUserStorageSerializer(box_user_storage, many=True).data
        except:
            pass
        result = {
            'data': box_user_storage_list
        }
        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'data': result})


# Create your views here.
class GetData(views.APIView):

    def post(self, request):
        params = request.POST
        dynamodb = dynamo.DynamoService()
        # 디렉토리 정보 가져오기
        result = dynamodb.getDirectorys(str(1), params['storage_id'])

        result = dict(data=result)
        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'data': result})


class GetFolderFile(views.APIView):

    def post(self, request):
        params = request.POST
        payload = request.body
        dynamodb = dynamo.DynamoService()
        # 디렉토리 하위 정보 가져오기
        result = dynamodb.get_directory_file(str(1), params)
        result = dict(data=result)
        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'data': result})


#  버전 정보 취득
class GetVersionInfo(views.APIView):

    def post(self, request):
        params = request.POST
        dynamodb = dynamo.DynamoService()
        # 디렉토리 하위 정보 가져오기
        result = dynamodb.get_version_info(str(1), params['id'])
        result = dict(data=result)
        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'data': result})


# 상위폴더 클릭시 정보가져오기
class GetParent(views.APIView):

    def post(self, request):
        params = request.POST
        dynamodb = dynamo.DynamoService()
        # 디렉토리 하위 정보 가져오기
        result = dynamodb.get_parent(str(1), params['id'])
        result = dict(data=result)
        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'data': result})


# 카테고리별 분류
class GetCategory(views.APIView):

    def post(self, request):
        params = request.POST
        dynamodb = dynamo.DynamoService()
        # 디렉토리 하위 정보 가져오기
        result = dynamodb.get_file_by_category(str(1), params)
        result = dict(data=result)
        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'data': result})


# 즐겨찾기 등록
class FavoriteRegistration(views.APIView):

    def post(self, request):
        params = request.POST
        dynamodb = dynamo.DynamoService()
        # 디렉토리 하위 정보 가져오기
        result = dynamodb.favorite_registration(str(1), params)
        result = dict(data=result)
        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'data': result})


# 즐겨찾기 등록 해제
class FavoriteRegistrationDel(views.APIView):

    def post(self, request):
        params = request.POST
        dynamodb = dynamo.DynamoService()
        # 디렉토리 하위 정보 가져오기
        result = dynamodb.favorite_registration_del(str(1), params)
        result = dict(data=result)
        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'data': result})
