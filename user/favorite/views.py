from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response
from .. import dynamo
from common.type.exception import Code


# Create your views here.
class GetFavoriteData(views.APIView):

    def post(self, request):
        params = request.POST
        payload = request.body

        print("body======", payload)

        dynamodb = dynamo.DynamoService()
        # 디렉토리 정보 가져오기
        result = dynamodb.getFavoriteInfo(str(1), payload)

        result = dict(data=result)
        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'data': result})
