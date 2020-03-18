import base64, os, hashlib, qrcode, random, string, asyncio, time
from threading import Timer
from os import remove
import onetimepass as otp

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from rest_framework import views
from rest_framework.response import Response

from .models import BoxFaq
from common.type.exception import Code
from user.main.models import BoxUsers, BoxUserinfo


# 사용자 정보 수정
class UpdateUserInfo(views.APIView):
    @transaction.atomic
    def post(self, request, format=None):
        post = request.POST

        id = post.get('id')
        sessionId = request.session['LOGGED_IN_USER_ID']

        code = ''
        message = ''

        # TODO 관리자일 경우에도 수정가능하도록 추가해야함
        # 수정하고자 하는 id가 현재 로그인한 id인지 체크
        if id == str(sessionId):
            try:
                user = BoxUsers.objects.get(bu_id=id)
            except BoxUsers.DoesNotExist:
                return Response({'code': Code.INTERNAL_SERVER_ERROR.value, 'message': Code.INTERNAL_SERVER_ERROR.name})

            firstname = post.get('firstname')
            lastname = post.get('lastname')
            email = post.get('email')
            currentPassword = post.get('currentPassword')

            if currentPassword != None:
                # 비밀번호 확인
                encoded_password = currentPassword.encode()
                hexdigest = hashlib.sha256(encoded_password).hexdigest()

                if user.bu_pw != hexdigest:
                    return Response({'code': Code.WRONG_PASSWORD.value, 'message': Code.WRONG_PASSWORD.name})

                newPassword = post.get('newPassword')
                newPasswordCheck = post.get('newPasswordCheck')

                if newPassword != None and newPassword != newPasswordCheck:
                    return Response({'code': Code.WRONG_RE_PASSWORD.value, 'message': Code.WRONG_RE_PASSWORD.name})

                user.bu_pw = hashlib.sha256(newPassword.encode()).hexdigest()

            if firstname != None:
                user.bu_firstname = firstname

            if lastname != None:
                user.bu_lastname = lastname

            if email != None:
                user.bu_email = email

            user.save()

            code = Code.SUCCESS.value
            message = Code.SUCCESS.name

        else:
            code = Code.INTERNAL_SERVER_ERROR.value
            message = Code.INTERNAL_SERVER_ERROR.name

        data = {
            'code': code,
            'message': message
        }

        return Response(data)


# 문의, 문제보고
class SendFaq(views.APIView):
    @transaction.atomic
    def post(self, request, format=None):

        name = request.data['name']
        email = request.data['email']
        phone = request.data['phone']
        message = request.data['message']
        faq_type = request.data['type']
        regist_user_id = request.session['LOGGED_IN_USER_ID']   # 아직 안 쓰이지만 필요할 듯
        status = 'N'

        if faq_type == 'inquiryLayer':
            faqdiv = 1
        elif faq_type == 'problemReportingLayer':
            faqdiv = 2

        BoxFaq.objects.create(fq_name=name, fq_email=email, fq_phone=phone, fq_message=message, fq_status=status, fq_faqdiv=faqdiv)

        data = {
            'code': Code.SUCCESS.value,
            'message': Code.SUCCESS.name
        }

        return Response(data)


# QR code 생성
class GetQrcode(views.APIView):
    @transaction.atomic
    def post(self, request):
        certify = request.data['certify']

        img = qrcode.make('otpauth://totp/user@myapplication.com?secret=' + certify + '&issuer=myotpgenerator')
        random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        file_name = certify + '.png'
        file_full_path = os.path.join(settings.MEDIA_ROOT, file_name)
        img.save(file_full_path)

        # 파일 삭제
        Timer(30, delete_file, (file_full_path, 5)).start()

        qrcode_url = 'http://' + request.META.get('HTTP_HOST') + settings.MEDIA_URL + file_name
        return Response({'qrcodeUrl': qrcode_url})


# OTP키 조회 (없으면 생성)
class GetOTPKey(views.APIView):
    @transaction.atomic
    def post(self, request):
        no_certify = True
        user_id = request.data['userId']

        user = BoxUsers.objects.get(pk=user_id)

        box_user_info = BoxUserinfo.objects.filter(boxUsers=user)

        if len(box_user_info) > 0:
            user_info = box_user_info[0]
            certify = user_info.ui_certify

            if certify is not None and certify != '':
                no_certify = False

        if no_certify:
            certify = make_certify()

        data = {
            'code': Code.SUCCESS.value,
            'certify': certify,
        }

        return Response(data)


# 검증 코드 체크
class CheckVerificationCode(views.APIView):
    @transaction.atomic
    def post(self, request):

        user_id = request.data['userId']
        certify = request.data['certify']
        verification_code = request.data['verificationCode']

        box_user_info = BoxUserinfo.objects.filter(boxUsers__bu_id=user_id)

        if len(box_user_info) > 0:
            user_info = box_user_info[0]
            user_certify = user_info.ui_certify

            if user_certify is not None and user_certify != '':
                certify = user_certify
        else:
            user = BoxUsers.objects.get(pk=user_id)
            user_info = BoxUserinfo.objects.create(boxUsers=user)

        valid = otp.valid_totp(verification_code, certify)

        if valid:
            user_info.ui_certify = certify
            user_info.save()

        return Response({'valid': valid})


# 2단계 인증 해제
class RemoveCertify(views.APIView):
    @transaction.atomic
    def post(self, request):
        user_id = request.data['userId']
        box_user_info = BoxUserinfo.objects.filter(boxUsers__bu_id=user_id)
        user_info = box_user_info[0]
        user_info.ui_certify = None
        user_info.save()

        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name})


# 언어 변경
class ChangeLanguage(views.APIView):
    @transaction.atomic
    def post(self, request):
        lang = request.data['lang']
        user_id = request.session['LOGGED_IN_USER_ID']
        user_info = BoxUserinfo.objects.get(boxUsers__bu_id=user_id)
        user_info.ui_lang = lang
        user_info.save()

        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name})


# 사용자 파일 검색 허용 변경
class ChangePermitfile(views.APIView):
    @transaction.atomic
    def post(self, request):
        permitfile = request.data['permitfile']
        user_id = request.session['LOGGED_IN_USER_ID']
        user_info = BoxUserinfo.objects.get(boxUsers__bu_id=user_id)
        user_info.ui_permitfile = permitfile
        user_info.save()

        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name})
    
    
# OTP 키 만들기
def make_certify():
    return base64.b32encode(os.urandom(10)).decode('utf-8')


def delete_file(file_path, seconds):
    print("start")
    time.sleep(seconds)
    print("end wait")
    remove(file_path)