# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from user.models import BoxUsers
from reseller.models import Reseller
from ast import literal_eval
from common.utils.AESCipher import AESCipher

tokenName = 'HTTP_X_BOX_ACCESSTOKEN'
keyName = 'HTTP_X_BOX_ACCESSKEY'


def get_authorization_header(request):
    auth = None



    auth = request.META.get('HTTP_AUTHORIZATION', b'')

    if isinstance(auth, type('')):
        auth = auth.encode('HTTP_HEADER_ENCODING')

    return auth


class MyTokenAuthentication:

    def authenticate(self, request):
        try:
            accessToken = request.COOKIES[tokenName]
            accessKey = request.COOKIES[keyName]
        except Exception as e:
            return None

        if accessToken == '' or accessKey == '' or accessToken is None or accessKey is None:
            return None

        cipher = AESCipher(key=accessKey)

        try:
            decodeToken = cipher.decrypt(enc=accessToken)
        except Exception as e:
            return None

        if decodeToken:
            payload = literal_eval(decodeToken)
        else:
            return None

        # token 만료 확인
        iat = payload.get('iat')    # time
        expired_datetime = datetime.now() + timedelta(hours=6)  # datetime
        expired_time = time.mktime(expired_datetime.timetuple())

        if int(iat) > expired_time:
            return None

        # user 객체
        user_id = payload.get('userId')

        User = BoxUsers

        paths = request.path.split("/")

        if len(paths) > 1 and paths[1] == 'reseller':
            User = Reseller

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

        return (user, payload)
