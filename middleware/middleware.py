from ast import literal_eval
from datetime import datetime, timedelta

from django.db import transaction
from django.http import HttpResponse, JsonResponse

from common.type.exception import Code
# from user.common.type.admin_code import AdminCode
from common.type.fieldType import Status, AdminType
from common.utils.AESCipher import AESCipher
from conf import settings


from user.main.models import BoxUsers
# from admin.models import Admin
from django.utils import timezone
# from admin.utils.validate_data_utils import *


class AuthMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        # 최초 설정 및 초기화

    def __call__(self, request):
        # 뷰가 호출되기 전에 실행될 코드들

        test = False
        if test:
            user = BoxUsers.objects.get(pk=1)
            request._body = user
            # response = self.get_response(request)
            # return response

        meta = request.META
        user = None
        admin_model = None

        # print('path: ' + request.path)

        # 로그인 유효 시간
        requestTime = datetime.now()
        requestTimezone = timezone.now()
        disconnectTime = timedelta(minutes=settings.DISCONNECT_TIME)

        print(meta)

        # 요청 위치 체크
        try:
            http_referer = request.environ['HTTP_REFERER']  # ex) http://dbox-dev.net/before_login/login'
            host = http_referer.replace("http://", "")
            path_index = host.find("/")
            host = host[:path_index]
            port_index = host.find(":")

            if port_index > -1:
                host = host[:port_index]

            if host not in settings.ALLOWED_HOSTS:
                return JsonResponse({'code': Code.ACCESS_DENIED.value, 'message': Code.ACCESS_DENIED.name})
        except KeyError:
            return JsonResponse({'code': Code.ACCESS_DENIED.value, 'message': Code.ACCESS_DENIED.name})

        # 로그인 없이 진행하는 게 아니면 토큰 확인
        if 'before_login' not in request.path:

            # 토큰 확인
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

                # user = BoxUsers.objects.get(pk=payload['userId'])

                # if user.last_connect_date:
                #     if (disconnectTime > timedelta(minutes=0)):
                #         if requestTime - user.last_connect_date > disconnectTime:
                #             return JsonResponse({'code': Code.CONNECTION_TIME_OUT.value, 'message': Code(-1002).name})
                #

                if request.session.get('HTTP_X_BOX_ACCESSTOKEN') != accessToken:
                    return JsonResponse(
                        {'code': Code.ACCESS_DENIED.value, 'message': Code.ACCESS_DENIED.name})
            # else:
            #     admin_model = Admin.objects.get(pk=payload['aid'])
            #
            #     if admin_model.auth_token != accessToken:
            #         return JsonResponse(
            #             {'code': Code.ACCESSTOKEN_IS_DENIED.value, 'message': Code.ACCESSTOKEN_IS_DENIED.name})

                # if 'eid' in payload:
                #     if admin_model.admin_type != AdminType.SITE:
                #         env_model = Env.objects.get(id=admin_model.env_id_id)
                #
                #         if env_model.status_type == Status.INACTIVE:
                #             return JsonResponse(
                #                 {'code': AdminCode.INACTIVE_ENV.value, 'message': AdminCode.INACTIVE_ENV.name})
                #
                # if admin_model.status_type == Status.INACTIVE:
                #     return JsonResponse(
                #         {'code': AdminCode.INACTIVE_ACCOUNT.value, 'message': AdminCode.INACTIVE_ACCOUNT.name})

            request._body = payload

        # if user:
        #     user.last_connect_date = datetime.now()
        #     user.save()
        # elif admin_model:
        #     admin_model.last_connect_date = timezone.now()
        #     admin_model.save()

        response = self.get_response(request)

        # 뷰가 호출된 뒤에 실행될 코드들
        # if user:
        #     if request.path not in exceptUrls:
        #         afterUser = BoxUsers.objects.get(pk=payload['userId'])
        #         afterUser.last_connect_date = datetime.now()
        #         afterUser.save()

        return response
