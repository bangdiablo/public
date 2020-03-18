from ast import literal_eval
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.http import JsonResponse
from common.type.exception import Code
from common.utils.AESCipher import AESCipher
from rest_framework.authentication import TokenAuthentication
from common.service.common_service import get_response_code
from reseller.models import Reseller
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import AnonymousUser


class Main(APIView):
    @transaction.atomic
    def post(self, request):
        return Response()


# 사용자정보
class UserInfo(APIView):

    # authentication_classes = (TokenAuthentication,)

    @transaction.atomic
    def post(self, request, format=None):

        if isinstance(request.user, AnonymousUser):
            return Response({'code': Code.ACCESS_IS_NOT_FOUND.value, 'message': Code.ACCESS_IS_NOT_FOUND.name})

        reseller = request.user

        # 관리자 권한 설정
        # isAdmin = is_admin(user)

        data = {
            'code': Code.SUCCESS.value,
            'companyname': reseller.rs_companyname,
            'email': reseller.rs_email,
            'id': reseller.rs_id,
        }

        return Response(data)


# 로그아웃
class Logout(APIView):
    @transaction.atomic
    def post(self, request, format=None):
        tokenName = 'HTTP_X_BOX_ACCESSTOKEN'
        keyName = 'HTTP_X_BOX_ACCESSKEY'

        # delete session
        del request.session[tokenName]
        del request.session[keyName]

        # delete cookie
        response = Response(get_response_code(Code.SUCCESS))
        response.delete_cookie(key='HTTP_X_BOX_ACCESSKEY')
        response.delete_cookie(key='HTTP_X_BOX_ACCESSTOKEN')

        return response
