from ast import literal_eval

from django.db import transaction
from django.db.models import CharField, IntegerField, Count
from django.db.models import Q, Case, When, Value
from django.http import JsonResponse
from rest_framework import views
from rest_framework.response import Response

from common.utils.AESCipher import AESCipher
from common.utils.admin_utils import *
from common.utils.log_utils import *
from .models import BoxUserinfo

logger = logging.getLogger(__name__)

super_admin_br_id = 1
admin_br_id = 2
default_bu_roleid = 3


# 로그아웃
class Logout(views.APIView):
    @transaction.atomic
    def post(self, request, format=None):
        tokenName = 'HTTP_X_BOX_ACCESSTOKEN'
        keyName = 'HTTP_X_BOX_ACCESSKEY'

        # delete session
        del request.session[tokenName]
        del request.session[keyName]

        # delete cookie
        result = {'result': True}
        model = response_model(result)
        response = Response(model)
        response.delete_cookie(key='HTTP_X_BOX_ACCESSKEY')
        response.delete_cookie(key='HTTP_X_BOX_ACCESSTOKEN')

        return response


# 메인
class Main(views.APIView):
    @transaction.atomic
    def post(self, request, format=None):
        return Response()


# 사용자정보
class UserInfo(views.APIView):
    @transaction.atomic
    def post(self, request, format=None):

        tokenName = 'HTTP_X_BOX_ACCESSTOKEN'
        keyName = 'HTTP_X_BOX_ACCESSKEY'

        accessToken = ''
        accessKey = ''

        try:
            accessToken = request.COOKIES[tokenName]
            accessKey = request.COOKIES[keyName]
        except Exception as e:
            return JsonResponse({'code': Code.ACCESS_IS_NOT_FOUND.value, 'message': Code.ACCESS_IS_NOT_FOUND.name})

        if accessToken == '' or accessKey == '' or accessToken is None or accessKey is None:
            return JsonResponse({'code': Code.ACCESS_IS_NOT_FOUND.value,
                                 'message': Code.ACCESS_IS_NOT_FOUND.name})

        cipher = AESCipher(key=accessKey)

        try:
            decodeToken = cipher.decrypt(enc=accessToken)
        except Exception as e:
            return JsonResponse({'code': Code.INTERNAL_SERVER_ERROR.value, 'message': Code.INTERNAL_SERVER_ERROR.name})

        if decodeToken:
            payload = literal_eval(decodeToken)
            print("payload :", payload)
        else:
            return JsonResponse(
                {'code': Code.INTERNAL_SERVER_ERROR.value, 'message': Code.INTERNAL_SERVER_ERROR.name})

        if request.path.find('admin') < 0:
            user = BoxUsers.objects.annotate(
                bu_super_admin=Count('boxRoles', filter=Q(boxRoles__br_id=super_admin_br_id)),
                bu_admin=Count('boxRoles', filter=Q(boxRoles__br_id=admin_br_id)),
                bu_count_admin=Count('boxRoles', filter=(Q(boxRoles__br_id=super_admin_br_id) | Q(boxRoles__br_id=admin_br_id))),
                bu_admin_yn=Case(
                    When(
                        bu_count_admin__gt=0,
                        then=Value('Y')
                    ),
                    default=Value('N'),
                    output_field=CharField()
                ),
                bu_roleid=Case(
                    When(
                        bu_super_admin=1,
                        then=super_admin_br_id
                    ),
                    When(
                        bu_admin=1,
                        then=admin_br_id
                    ),
                    default=default_bu_roleid,
                    output_field=IntegerField()
                ),
            ).get(pk=payload['userId'])

        # 관리자 권한 설정
        isAdmin = is_admin(user)

        # 2단계 인증 설정 여부
        try:
            user_info = BoxUserinfo.objects.get(boxUsers=user)

            if user_info.ui_certify is None or user_info.ui_certify == '':
                existCertify = False
            else:
                existCertify = True

            lang = user_info.ui_lang
            permitfile = user_info.ui_permitfile

        except BoxUserinfo.DoesNotExist:
            lang = 'KR'
            permitfile = 'N'
            existCertify = False

        result = {
            'result': True,
            'firstname': user.bu_firstname,
            'lastname': user.bu_lastname,
            'email': user.bu_email,
            'id': user.bu_id,
            'labelid': user.bu_labelid,
            'resellerid': user.reseller.rs_id if user.reseller else None,
            'isAdmin': isAdmin,
            'existCertify': existCertify,
            'lang': lang,
            'permitfile': permitfile,
        }

        model = response_model(result)

        return Response(model)


def is_admin(user):
    admin = False

    if user.bu_roleid == super_admin_br_id or user.bu_roleid == admin_br_id:
        admin = True

    return admin
