import random, string
import binascii
import hashlib
import json
import requests
from datetime import datetime

import onetimepass as otp
from django.db import transaction
from django.db.models import CharField, IntegerField, Count
from django.db.models import F, Q, Case, When, Value
from django.db.models.functions import Concat
from django.utils import translation
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.views import APIView
from rest_framework.response import Response

from common.service import login_service
from common.service.mail_service import MailService
from common.type.fieldType import Status
from common.utils.AESCipher import AESCipher
from common.utils.admin_utils import *
from common.utils.log_utils import *
from conf import settings
from user.main.models import BoxUserinfo
from user.management.views_user import create_box_users
from user.models import BoxLicensekey
from reseller.models import Reseller
from common.service.common_service import get_response_code

logger = logging.getLogger(__name__)

super_admin_br_id = 1
admin_br_id = 2
default_bu_roleid = 3


# 로그인
class Login(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            email = request.data['email']
            password = request.data['password']
            language = request.data['language']
        except MultiValueDictKeyError:
            return Response({'code': '키없음', 'message': Code.LOGIN_FAIL.name})

        try:
            reseller = Reseller.objects.filter(rs_status='A').get(rs_email=email)
        except Reseller.DoesNotExist:
            return Response(get_response_code(Code.NO_EXIST_USER))     # 없는 email

        # 비밀번호 확인
        encoded_password = password.encode()
        hexdigest = hashlib.sha256(encoded_password).hexdigest()

        if reseller.rs_pw != hexdigest:
            return Response(get_response_code(Code.WRONG_PASSWORD))   # 틀린 password

        # 로그인 성공
        payload = {
            'userId': reseller.rs_id,
            'email': reseller.rs_email,
            'iat': datetime.now().timestamp(),
        }

        authKey = ""

        for i in range(16):
            authKey += random.choice(string.ascii_letters)

        cipher = AESCipher(authKey)
        accessToken = cipher.encrypt(str(payload))
        accessToken = accessToken.decode('utf-8')

        request.session['HTTP_X_BOX_ACCESSKEY'] = authKey
        request.session['HTTP_X_BOX_ACCESSTOKEN'] = accessToken
        request.session['LOGGED_IN_RESELLER_ID'] = reseller.rs_id

        language = language.lower()

        if translation.LANGUAGE_SESSION_KEY in request.session:
            del request.session[translation.LANGUAGE_SESSION_KEY]

        translation.activate(language)
        request.session[translation.LANGUAGE_SESSION_KEY] = language

        response = Response(get_response_code(Code.SUCCESS))

        # create cookies
        secure = settings.IS_REAL
        response.set_cookie(key='HTTP_X_BOX_ACCESSKEY', value=authKey, httponly=True, secure=secure)
        response.set_cookie(key='HTTP_X_BOX_ACCESSTOKEN', value=accessToken, httponly=True, secure=secure)

        return response


# 비밀번호 찾기 이메일 발송
class SendEmailToResetPassword(APIView):
    @transaction.atomic
    def post(self, request, format=None):
        email = request.data['email']

        logger.info(get_request_params(request))

        # 해당 email이 계정 중에 있는지 확인
        try:
            reseller = Reseller.objects.filter(rs_status='A').get(rs_email=email)
        except Reseller.DoesNotExist:
            return Response({'code': Code.NO_EXIST_USER.value, 'message': Code.NO_EXIST_USER.name})

        # 해당 이메일로 이메일 전송
        proc_result = MailService.send_email_reset_password(request)
        model = response_model(proc_result)

        return Response(model)


# 비밀번호 변경
class ResetPassword(APIView):
    @transaction.atomic
    def post(self, request, format=None):
        k = request.data['k']
        email = request.data['email']
        password = request.data['password']
        re_password = request.data['rePassword']

        # password 빈 것 or 6자리 이하 검사
        if password is '' or len(password) < 6:
            return Response({'code': Code.WRONG_PASSWORD.value, 'message': Code.WRONG_PASSWORD.name})

        # password 일치 여부 검사
        if password != re_password:
            return Response({'code': Code.WRONG_RE_PASSWORD.value, 'message':Code.WRONG_RE_PASSWORD.name})

        # k 검사
        try:
            code = check_data_and_email(k)
        except Exception as exc:
            code = exc.args[0]

        if code is not Code.SUCCESS:
            return Response({'code': code.value, 'message': code.name})

        # k의 email과 email의 일치 여부 검사
        cipher = AESCipher(key='AOS_BOX_EMAIL_KEY')
        decrypted_k = cipher.decrypt(k)
        decrypted_k_arr = decrypted_k.split('/')
        valid_email = decrypted_k_arr[1]

        if email != valid_email:
            return Response({'code': Code.NO_AUTHORITY.value, 'message': Code.NO_AUTHORITY.name})

        # email의 password 수정
        try:
            reseller = Reseller.objects.filter(rs_status='A').get(rs_email=email)
        except Reseller.DoesNotExist:
            return Response({'code': Code.NO_EXIST_USER.value, 'message': Code.NO_EXIST_USER.name})

        encoded_password = password.encode()
        hexdigest = hashlib.sha256(encoded_password).hexdigest()
        reseller.rs_pw = hexdigest
        reseller.save()

        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name})


# # 2단계 인증
# class SecondCertification(APIView):
#     @transaction.atomic
#     def post(self, request, format=None):
#         valid = False
#         user_id = request.data['userId']
#         verification_code = request.data['verificationCode']
#
#         user = BoxUsers.objects.annotate(bu_roleid=F('boxuserrole__boxRoles__br_id'),
#                                   bu_fullname=Case(
#                                       When(
#                                           Q(bu_lastname=None) | Q(bu_lastname=''),
#                                           then='bu_firstname'
#                                       ),
#                                       default=Concat('bu_firstname', Value(' '), 'bu_lastname')),
#                                   ).get(pk=user_id)
#         box_user_info = BoxUserinfo.objects.filter(boxUsers__bu_id=user_id)
#
#         if len(box_user_info) > 0:
#             certify = box_user_info[0].ui_certify
#             valid = otp.valid_totp(verification_code, certify)
#
#         if valid is False:
#             return Response({'code': Code.IMPROPER_CODE.value, 'message': Code.IMPROPER_CODE.name})
#
#         return login_success(request, user)
#
#
# 메일 링크의 유효한 key인지 확인
class CheckValidKey(APIView):
    @transaction.atomic
    def post(self, request):
        k_type = request.data['kType']

        try:
            k = request.data['k']
        except KeyError:
            return Response({'code': Code.INVALID_KEY.value, 'message': Code.INVALID_KEY.name})

        valid_email = None

        # 회원 초대 이메일
        if k_type == 'join':
            # decypt k
            try:
                cipher = AESCipher(key='AOS_BOX_EMAIL_KEY')
                decrypted_k = cipher.decrypt(k)
            except binascii.Error:
                return Response({'code': Code.IMPROPER_MAIL_LINK.value, 'message': Code.IMPROPER_MAIL_LINK.name})

            # decrypted_k 날짜 형식인지 확인
            try:
                datetime.strptime(decrypted_k, '%Y%m%d')
                now = datetime.now().strftime('%Y%m%d')

                # decrypted_k가 유효한 날짜인지 확인
                if decrypted_k < now:
                    return Response({'code': Code.IMPROPER_MAIL_LINK.value, 'message': Code.IMPROPER_MAIL_LINK.name})

            except ValueError:
                return Response({'code': Code.IMPROPER_MAIL_LINK.value, 'message': Code.IMPROPER_MAIL_LINK.name})

        # 비밀번호 변경 이메일
        elif k_type == 'password':
            # k가 날짜/이메일 형식인지 확인
            try:
                code = check_data_and_email(k)

                cipher = AESCipher(key='AOS_BOX_EMAIL_KEY')
                decrypted_k = cipher.decrypt(k)
                decrypted_k_arr = decrypted_k.split('/')
                valid_email = decrypted_k_arr[1]
            except Exception as exc:
                code = exc.args[0]
                return Response({'code': code.value, 'message': code.name})

        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'email': valid_email})


# def login_success(request, user):
#     meta = request.META
#     language = request.data['language']
#
#     # create session
#     result = login_service.login(user, meta, language)
#     request.session['HTTP_X_BOX_ACCESSKEY'] = result['accessKey']
#     request.session['HTTP_X_BOX_ACCESSTOKEN'] = result['accessToken']
#     request.session['LOGGED_IN_USER_ID'] = user.bu_id
#
#     language = language.lower()
#
#     if translation.LANGUAGE_SESSION_KEY in request.session:
#         del request.session[translation.LANGUAGE_SESSION_KEY]
#
#     translation.activate(language)
#     request.session[translation.LANGUAGE_SESSION_KEY] = language
#
#     # 관리자 권한 설정
#     isAdmin = is_admin(user)
#
#     # 스토리지 서비스 연결 정보 확인
#     google_drive = False
#     # todo 에러 발생 확인하여 수정할것!
#     # try:
#     #     Googledrivesettings.objects.get(userid=user.bu_id, flag='N')
#     #     google_drive = True
#     # except Googledrivesettings.DoesNotExist:
#     #     pass
#
#     storage_service = {
#         'google_drive': google_drive
#     }
#
#     data = {
#         'code': Code.SUCCESS.value,
#         'message': Code.SUCCESS.name,
#         'isPass': True,
#         'isAdmin': isAdmin,
#         'storage_service': storage_service
#     }
#     response = Response(data)
#
#     # create cookies
#     secure = settings.IS_REAL
#     response.set_cookie(key='HTTP_X_BOX_ACCESSKEY', value=result['accessKey'], httponly=True, secure=secure)
#     response.set_cookie(key='HTTP_X_BOX_ACCESSTOKEN', value=result['accessToken'], httponly=True, secure=secure)
#
#     return response


def check_data_and_email(k):
    # decypt k
    try:
        cipher = AESCipher(key='AOS_BOX_EMAIL_KEY')
        decrypted_k = cipher.decrypt(k)
    except binascii.Error:
        return Code.IMPROPER_MAIL_LINK

    try:
        decrypted_k_arr = decrypted_k.split('/')
        valid_date = decrypted_k_arr[0]
        valid_email = decrypted_k_arr[1]

        datetime.strptime(valid_date, '%Y%m%d%H%M%S')
        now = datetime.now().strftime('%Y%m%d%H%M%S')

        # valid_date가 유효한 날짜인지 확인
        if decrypted_k < now:
            return Code.IMPROPER_MAIL_LINK

        # valid_email이 유효한 이메일인지 확인
        try:
            BoxUsers.objects.get(bu_email=valid_email)
        except BoxUsers.DoesNotExist:
            return Code.IMPROPER_MAIL_LINK

    except ValueError:
        return Code.IMPROPER_MAIL_LINK

    return Code.SUCCESS


# def is_admin(user):
#     admin = False
#
#     if user.bu_roleid == super_admin_br_id or user.bu_roleid == admin_br_id:
#         admin = True
#
#     return admin
#
#
# # 이메일 중복 조회
# class CheckExistEmail(views.APIView):
#     @transaction.atomic
#     def post(self, request):
#         email = request.data['email']  # 메일 주소
#
#         # email 중복 검사
#         try:
#             user = BoxUsers.objects.get(bu_email=email)
#             return Response({'code': Code.ALREADY_EXIST_USER.value, 'message': Code.ALREADY_EXIST_USER.name})
#
#         except BoxUsers.DoesNotExist:
#             return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name})
#
#
# # 라이센스 키 검증
# class CheckLicenseKey(views.APIView):
#     @transaction.atomic
#     def post(self, request):
#         license_key = request.data['licenseKey']  # 메일 주소
#
#         try:
#             BoxLicensekey.objects.filter(li_status=1).get(li_licensekey=license_key)
#         except BoxLicensekey.DoesNotExist:
#             return Response({'code': Code.IMPROPER_LICENSE_KEY.value, 'message': Code.IMPROPER_LICENSE_KEY.name})
#
#         return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name})
#
#
# # CheckCaptcha
# class CheckRecaptcha(views.APIView):
#     @transaction.atomic
#     def post(self, request):
#         token = request.data['token']
#         secret = '6LfkR9wUAAAAAEr1EVjAHDHnj_KfH-MvQopengna'
#         url = 'https://www.google.com/recaptcha/api/siteverify'
#
#         data = {'response': token, 'secret': secret}
#         response = requests.post(url, data=data)
#
#         if response.status_code == 200:
#             data = {'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'result': json.loads(response.text)}
#         else:
#             data = {'code': Code.INVALID_KEY.value, 'message': Code.INVALID_KEY.name}
#
#         return Response(data)
#
#
# # 이메일로 사용자 등록
# class RegistMemberWithLicenseKey(views.APIView):
#     @transaction.atomic
#     def post(self, request):
#
#         name = request.data['name']  # 이름
#         email = request.data['email']  # 메일 주소
#         password = request.data['password']  # 비밀번호
#         license_key = request.data['licenseKey']  # 라이센스 키
#         check_agree = request.data['checkAgree']  # 동의 체크
#         tel_number = None  # 전화번호
#         admin_id = 1  # TODO admin_id(email의 key에서부터 user_id 추출) 추가할 것
#
#         if 'telNumber' in request.data:
#             tel_number = request.data['telNumber']
#
#         if license_key:
#             if not check_agree:
#                 return Response({'code': '동의 체크 안 함', 'message': '동의 체크 안 함'})
#
#         params = {
#             'first_name': name,
#             'email': email,
#             'password': password,
#             'license_key': license_key,
#             'tel_number': tel_number,
#             'admin_id': admin_id,
#         }
#
#         user = create_box_users(params)
#
#         if user is None:
#             return Response({'code': Code.ALREADY_EXIST_USER.value, 'message': Code.ALREADY_EXIST_USER.name})
#         else:
#             return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name})