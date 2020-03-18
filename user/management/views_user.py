import csv
import hashlib
import json
import os
import re
import uuid
import requests
from datetime import datetime, timedelta
from os import remove

from user.common.service.common_service import get_my_group_user_list, get_my_group_policy_list
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.db.models import F, Q, Sum, Case, When, Value, CharField, IntegerField, Max, Count
from django.db.models.functions import Coalesce, Concat
from django.http import HttpResponse
from rest_framework import views
from rest_framework.response import Response

from common.service.mail_service import MailService
from common.utils.AESCipher import AESCipher
from common.utils.admin_utils import *
from user.main.models import BoxUsers, BoxUserrole, BoxUserinfo, BoxRoles
from user.models import BoxStoragediv, BoxLicensekey, BoxLicensemap, BoxUserstorage, Policy, BoxGroupmember
from .serializers import BoxUsersSerializer, ExtendedUserStorageSerializer, policyEditListSerializer, UsersSerializer

"""
    관리 - 사용자 또는 서버
"""


# 목록 조회 (사용자, 컴퓨터, 서버)
class UserServerList(views.APIView):
    @transaction.atomic
    def post(self, request, list_type):

        data_list = []
        total_count = 0

        data_list, total_count, have_new = get_user_server_list(request, list_type)

        if list_type == 'User':
            serialized_data_list = BoxUsersSerializer(data_list, many=True).data
        elif list_type == 'Computer' or list_type == 'Server':
            serialized_data_list = ExtendedUserStorageSerializer(data_list, many=True).data

        data = {
            'code': Code.SUCCESS.value,
            'list': serialized_data_list,
            'totalListCount': total_count,
            'haveNew': have_new
        }

        return Response(data)


# 상세 조회
class UserDetail(views.APIView):
    @transaction.atomic
    def post(self, request, user_id):
        user = append_column(BoxUsers.objects, 'User').get(bu_id=user_id)
        user.bu_pw = ""

        user_serializer = BoxUsersSerializer([user], many=True)

        data = {
            'user': user_serializer.data
        }

        return Response(data)


# 상세의 목록 조회
class UserDetailList(views.APIView):
    @transaction.atomic
    def post(self, request, user_id, list_type):
        current_page = int(request.data['currentPage'])
        data_per_page = int(request.data['dataPerPage'])

        start_index = (current_page - 1) * data_per_page
        end_index = current_page * data_per_page

        user = BoxUsers.objects.get(pk=user_id)

        bs_sdcode = list(BoxStoragediv.objects.filter(sd_category=list_type).values_list('sd_code', flat=True))

        userstorage_list = []
        totalListCount = 0

        try:
            userstorage_list = BoxUserstorage.objects.filter(bs_userid=user).filter(
                Q(bs_sdcode__in=bs_sdcode) & ~Q(bs_status=4)).annotate(bs_new=Case(
                When(bs_createdate__gt=datetime.now() + timedelta(days=-7),
                     then=Value('Y')),
                default=Value('N'),
                output_field=CharField(),
            ))

            totalListCount = len(userstorage_list)
            userstorage_list = append_column(userstorage_list.order_by('-bs_createdate')[start_index:end_index],
                                             'Computer')
            serialized_userstorage_list = ExtendedUserStorageSerializer(userstorage_list, many=True).data

        except BoxUserstorage.DoesNotExist:
            pass

        data = {
            'code': Code.SUCCESS.value,
            'list': serialized_userstorage_list,
            'totalListCount': totalListCount
        }

        return Response(data)


# 초대 메일 발송
class SendEmail(views.APIView):
    @transaction.atomic
    def post(self, request):
        emails = request.data['emails']
        subject = request.data['subject']
        message = request.data['message']

        email_list = emails.split(',')

        # 이메일 보내기
        params = {
            'emailList': email_list,
            'subject': subject,
            'message': message
        }

        proc_result = MailService.send_email_join(params)
        data = response_model(proc_result)

        return Response(data)


# 정책 조회
class GetPolicyList(views.APIView):
    @transaction.atomic
    def post(self, request):
        try:
            user_id = request.data['userId']
        except KeyError:
            user_id = request.session['LOGGED_IN_USER_ID']

        # user = BoxUsers.objects.get(bu_id=user_id)

        policy_list = get_my_group_policy_list(user_id)
        # account_id = user.bu_accountid
        #
        # try:
        #     policy_list = Policy.objects.filter(bp_accountid=account_id)
        # except Policy.DoesNotExist:
        #     policy_list = []

        data = {
            'code': Code.SUCCESS.value,
            'message': Code.SUCCESS.name,
            'policyList': policyEditListSerializer(policy_list, many=True).data
        }
        return Response(data)


# 수동으로 사용자 등록
class RegistMember(views.APIView):
    @transaction.atomic
    def post(self, request):
        name = request.data['name']  # 이름
        email = request.data['email']  # 메일 주소
        password = request.data['password']  # 비밀번호
        permit_search = request.data['permitSearch']  # 검색허가
        gnrllimit = request.data['gnrllimit']  # 일반 스토리지 제한
        gnrlunlimit = request.data['gnrlunlimit']  # 일반 스토리지 무제한 체크 여부
        coldlimit = request.data['coldlimit']  # 콜드 스토리지 제한
        coldunlimit = request.data['coldunlimit']  # 콜드 스토리지 무제한 체크 여부
        ocrlimit = request.data['ocrlimit']  # OCR 페이지 수 제한
        ocrunlimit = request.data['ocrunlimit']  # OCR 페이지 수 무제한 체크
        policy_id = request.data['policy']  # 정책
        admin_id = request.session['LOGGED_IN_USER_ID']

        if gnrlunlimit or gnrllimit == '':
            gnrllimit = 0

        if coldunlimit or coldlimit == '':
            coldlimit = 0

        if ocrunlimit or ocrlimit == '':
            ocrlimit = 0

        if policy_id == '':
            policy_id = 0

        try:
            policy = Policy.objects.get(bp_id=policy_id)
        except Policy.DoesNotExist:
            policy = None

        params = {
            'first_name': name,
            'email': email,
            'password': password,
            'permit': permit_search,
            'gnrllimit': gnrllimit,
            'coldlimit': coldlimit,
            'ocrlimit': ocrlimit,
            'policy': policy,
            'admin_id': admin_id,
        }

        user = create_box_users(params)

        if user is None:
            return Response({'code': Code.ALREADY_EXIST_USER.value, 'message': Code.ALREADY_EXIST_USER.name})
        else:
            return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name})


# CSV로 사용자 등록
class RegistMembers(views.APIView):
    @transaction.atomic
    def post(self, request):

        files = []

        for key in request.data:
            if isinstance(request.data[key], InMemoryUploadedFile):
                files.append(request.data[key])

        valid_form = True

        # 파일 유효성 검사
        for file in files:
            # 임시 저장
            path = default_storage.save(os.path.join('tmp', file.name), ContentFile(file.read()))
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            valid_form = True

            with open(tmp_file) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                row_count = 0

                # CSV 파일 유효성 검사
                for row in csv_reader:
                    row_count += 1

                    if row_count == 1:
                        continue

                    first_name = row[0]
                    last_name = row[1]
                    email = row[2]
                    password = row[3]
                    permit = row[4]
                    policy_name = row[5]
                    gnrllimit = row[6]
                    coldlimit = row[7]
                    ocrlimit = row[8]

                    # 이름이 비어있는지
                    if first_name.strip() == '':
                        valid_form = False
                        break

                    # 이메일 형식에 맞는지, 이미 있는 지
                    if re.match('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email) is False:
                        valid_form = False
                        break
                    else:
                        try:
                            user = BoxUsers.objects.get(bu_email=email)  # 이미 사용자가 있는 이메일인 경우
                            valid_form = False
                            break
                        except BoxUsers.DoesNotExist:
                            pass

                    # 비밀번호 : 6자 이상인지
                    if len(password) < 6:
                        valid_form = False
                        break

                    # permit ( 0, 1, 2)
                    if permit not in ('0', '1', '2'):
                        valid_form = False
                        break

            if valid_form is False:
                break

        # csv 형식 안 맞을 경우
        if valid_form is False:
            for file in files:
                tmp_file = os.path.join(settings.MEDIA_ROOT, os.path.join('tmp', file.name))

                try:
                    os.remove(tmp_file)  # 파일 삭제
                except FileNotFoundError:
                    pass

            return Response({'code': Code.IMPROPER_CSV.value, 'message': Code.IMPROPER_CSV.name})

        # 회원 등록
        for file in files:
            tmp_file = os.path.join(settings.MEDIA_ROOT, os.path.join('tmp', file.name))

            with open(tmp_file) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')

                row_count = 0
                for row in csv_reader:

                    if len(row) != 9:
                        continue

                    row_count += 1

                    if row_count != 1:
                        first_name = row[0]
                        last_name = row[1]
                        email = row[2]
                        password = row[3]
                        permit = row[4]
                        policy_name = row[5]
                        gnrllimit = row[6]
                        coldlimit = row[7]
                        ocrlimit = row[8]
                        admin_id = request.session['LOGGED_IN_USER_ID']

                        params = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': email,
                            'password': password,
                            'permit': permit,
                            'gnrllimit': gnrllimit,
                            'coldlimit': coldlimit,
                            'ocrlimit': ocrlimit,
                            'policy_name': policy_name,
                            'admin_id': admin_id
                        }

                        user = create_box_users(params)

            os.remove(tmp_file)  # 파일 삭제

        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name})


# 사용자 활성화/비활성화 수정
class UpdateUserActive(views.APIView):
    @transaction.atomic
    def post(self, request):
        userids = request.data['userids']
        active = request.data['active']

        boxUsers = BoxUsers.objects.all().filter(bu_id__in=userids)

        for boxUser in boxUsers:
            boxUser.bu_status = active
            boxUser.save()

        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name})


# 사용자 제한 수정
class UpdateUserLimit(views.APIView):
    @transaction.atomic
    def post(self, request):
        userids = request.data['userids']
        type = request.data['type']
        size = request.data['size']

        if size == '' or size == '0':
            size = 0
        else:
            size = int(size)

        boxUsers = BoxUsers.objects.all().filter(bu_id__in=userids)

        for boxUser in boxUsers:
            if type == 'gnrllimit':
                boxUser.bu_gnrllimit = size
            elif type == 'coldlimit':
                boxUser.bu_coldlimit = size
            elif type == 'ocrlimit':
                boxUser.bu_ocrlimit = size
            boxUser.save()

        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name})


# 사용자 관리자 권한 수정
class ChangeAdminAuth(views.APIView):
    @transaction.atomic
    def post(self, request):
        user_id = request.data['userId']

        user = BoxUsers.objects.get(pk=user_id)
        boxUserrole = user.boxuserrole_set.all().get()
        role_id = boxUserrole.boxRoles.br_id

        if role_id == 1:
            br_id = 2
        elif role_id == 2:
            br_id = 1

        newBoxRoles = BoxRoles.objects.get(pk=br_id)
        boxUserrole.boxRoles = newBoxRoles
        boxUserrole.save()

        data = {'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name, 'ci': br_id}
        return Response(data)


# 사용자 정보 수정
class ChangeUserInfo(views.APIView):
    @transaction.atomic
    def post(self, request):
        user_id = request.data['userId']
        type = request.data['type']
        value = request.data['value']

        user = BoxUsers.objects.get(pk=user_id)

        if type == 'password':
            encoded_password = value.encode()
            hexdigest = hashlib.sha256(encoded_password).hexdigest()
            user.bu_pw = hexdigest
        elif type == 'name':
            user.bu_firstname = value
            user.bu_lastname = None
        elif type == 'email':
            user.bu_email = value
        elif type == 'permit':
            user.bu_permit = int(value)
        elif type == 'policyId':
            try:
                policy = Policy.objects.get(pk=value)
            except Policy.DoesNotExist:
                policy = None

            user.policy = policy

        user.save()

        data = {'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name}
        return Response(data)


# 목록(사용자, 컴퓨터, 서버) CSV 내보내기
class DownloadCSV(views.APIView):
    @transaction.atomic
    def post(self, request, list_type):
        subject_list = []
        data_list = []

        print(request.POST.get('currentPage'))

        data_list = get_user_server_list(request, list_type)

        if len(data_list) > 0:
            data_list = data_list[0]

            if list_type == 'User':
                subject_list = [('이름', '정책', '일반 스토리지 사용량', '일반 스토리지 최대',
                                 '콜드 스토리지 사용량', '콜드 스토리지 최대', 'OCR 사용량', 'OCR 최대', '종류')]

                data_list = data_list.values_list('bu_fullname', 'bu_policyname', 'bu_gnrlsto', 'bu_gnrllimit',
                                                  'bu_coldsto', 'bu_coldlimit', 'bu_ocr', 'bu_ocrlimit',
                                                  'bu_permitname')

            elif list_type == 'Computer':
                subject_list = [('유저명/컴퓨터이름', '상황', '전회 사용', '일반 스토리지 사용량',
                                 '일반 스토리지 최대', '콜드 스토리지 사용량', '콜드 스토리지 최대', 'OCR 사용량', 'OCR 최대')]

                data_list = data_list.values_list('bs_user_computer', 'bs_status', 'bs_logdate', 'bs_gnrlsto',
                                                  'bs_gnrllimit', 'bs_coldsto', 'bs_coldlimit', 'bs_ocr', 'bs_ocrlimit')
            elif list_type == 'Server':
                subject_list = [('관리 사용자', '서버 이름', '정책', '일반 스토리지 사용량',
                                 '일반 스토리지 최대', '콜드 스토리지 사용량', '콜드 스토리지 최대', 'OCR 사용량', 'OCR 최대')]

                data_list = data_list.values_list('bs_user_fullname', 'bs_name', 'bs_policyname', 'bs_gnrlsto',
                                                  'bs_gnrllimit', 'bs_coldsto', 'bs_coldlimit', 'bs_ocr', 'bs_ocrlimit')

        tmp_file_path = make_csv(request, list_type, subject_list, list(data_list))
        file_name = os.path.basename(tmp_file_path)

        resultFile = open(tmp_file_path, 'rb')
        httpResponse = HttpResponse(resultFile, content_type=u"text/csv; charset=utf-8")
        httpResponse['Content-Disposition'] = 'attachment; filename="%s"' % file_name
        resultFile.close()
        remove(tmp_file_path)

        return httpResponse


# 사용자 스토리지 수정
class ChangeUserStorage(views.APIView):
    @transaction.atomic
    def post(self, request):
        storage_ids = request.data['storageIds']
        prop = request.data['prop']
        value = None

        try:
            value = request.data['value']
        except KeyError:
            pass

        userstorages = BoxUserstorage.objects.filter(bs_id__in=storage_ids)

        if (prop == 'gnrllimit' or prop == 'coldlimit' or prop == 'ocrlimit') and value == '':
            value = 0

        for userstorage in userstorages:
            if prop == 'status':
                if value == 'activate':
                    value = 1
                elif value == 'pause':
                    value = 2
                elif value == 'archive':
                    value = 3
                elif value == 'delete':
                    value = 4
                userstorage.bs_status = value
            elif prop == 'name':
                userstorage.bs_name = value
            elif prop == 'gnrllimit':
                userstorage.bs_gnrllimit = value
            elif prop == 'coldlimit':
                userstorage.bs_coldlimit = value
            elif prop == 'ocrlimit':
                userstorage.bs_ocrlimit = value
            elif prop == 'policy':
                if value == 'delete':
                    userstorage.bs_policyid = None
                else:
                    try:
                        policy = Policy.objects.get(pk=value)
                    except Policy.DoesNotExist:
                        policy = None

                    userstorage.bs_policyid = policy
            elif prop == 'backup':
                userstorage.bs_backup = 1

            userstorage.save()

        data = {'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name}
        return Response(data)


# 회원가입 시, key 확인
class CheckEmailKey(views.APIView):
    @transaction.atomic
    def post(self, request):
        k = request.data['k']

        cipher = AESCipher(key='AOS_BOX_EMAIL_KEY')
        date = cipher.decrypt(k)

        # date가 날짜 형식인지 확인
        try:
            datetime.strptime(date, '%Y%m%d')
        except ValueError:
            return Response({'code': Code.IMPROPER_MAIL_LINK.value, 'message': Code.IMPROPER_MAIL_LINK.name})

        now = datetime.now().strftime('%Y%m%d')

        # date가 유효한 날짜인지 확인
        if date < now:
            return Response({'code': Code.IMPROPER_MAIL_LINK.value, 'message': Code.IMPROPER_MAIL_LINK.name})

        return Response({'code': Code.SUCCESS.value, 'message': Code.SUCCESS.name})


# 사용자 등록
def create_box_users(params):
    user = None

    # set variable
    firstname = params['first_name']
    lastname = None

    try:
        lastname = params['last_name']
    except KeyError:
        pass

    email = params['email']
    password = params['password']

    permit = 2

    try:
        permit = params['permit']
    except KeyError:
        pass

    gnrllimit = 0

    try:
        gnrllimit = params['gnrllimit']
    except KeyError:
        pass

    coldlimit = 0

    try:
        coldlimit = params['coldlimit']
    except KeyError:
        pass

    ocrlimit = 0

    try:
        ocrlimit = params['ocrlimit']
    except KeyError:
        pass

    license_key = None

    try:
        license_key = params['license_key']
    except KeyError:
        pass

    policy = None
    try:
        policy = params['policy']
    except KeyError:
        pass

    try:
        policy_name = params['policy_name']
        try:
            policy = Policy.objects.get(bp_name=policy_name)
        except Policy.DoesNotExist:
            policy = None
    except KeyError:
        pass

    tel_number = None

    try:
        tel_number = params['tel_number']
    except KeyError:
        pass

    admin_id = None

    try:
        admin_id = params['admin_id']
    except KeyError:
        pass

    # email 중복 검사
    try:
        BoxUsers.objects.get(bu_email=email)
    except BoxUsers.DoesNotExist:
        # password encrypt
        encoded_password = password.encode()
        hexdigest = hashlib.sha256(encoded_password).hexdigest()

        # 유저 추가
        user = BoxUsers.objects.create(bu_firstname=firstname, bu_lastname=lastname, bu_email=email, bu_pw=hexdigest,
                                       bu_permit=permit, bu_gnrllimit=gnrllimit,
                                       bu_coldlimit=coldlimit, bu_ocrlimit=ocrlimit,
                                       policy=policy, bu_labelid=None, reseller=None)

        # 유저 role 추가
        box_roles = BoxRoles.objects.get(br_id=2)  # 일반 사용자
        BoxUserrole.objects.create(boxUsers=user, boxRoles=box_roles)

        # 유저 info 추가
        BoxUserinfo.objects.create(ui_licenseKey=license_key, ui_tel=tel_number, boxUsers=user)

        # licensekeymap 추가
        if license_key is not None:
            box_licensekey = get_box_licensekey(license_key)  # li_status가 5 (대기)인 것으로 확인

            if box_licensekey is not None:
                BoxLicensemap.objects.create(boxLicensekey=box_licensekey, boxUser=user, lu_flag='Y')  # licensemap 생성
                box_licensekey.li_status = 1
                box_licensekey.save()  # licensekey 상태 활성화(1)

        # groupmember 추가
        box_groupmember = BoxGroupmember.objects.get(boxUser__bu_id=admin_id)
        box_group = box_groupmember.boxGroup
        BoxGroupmember.objects.create(boxGroup=box_group, boxUser=user)

        # dynamodb 스토리지 추가
        storage_id = uuid.uuid4()  # 스토리지 ID 생성

        box_storagediv = BoxStoragediv.objects.get(sd_code='C')  # 클라우드

        # userstorage 추가 (cloud 생성)
        # TODO 용량은?
        BoxUserstorage.objects.create(bs_storage_id=storage_id, bs_name='기본 클라우드', bs_sdcode=box_storagediv,
                                      bs_userid=user)

    return user


# 관리 - 사용자 또는 기기 목록 조회
def get_user_server_list(request, list_type):
    data_list = []
    total_count = 0
    have_new = False

    search_text = request.data['searchText']
    current_page = int(request.data['currentPage'])
    data_per_page = int(request.data['dataPerPage'])
    order_name = request.data['orderName']
    order_type = request.data['orderType']

    search_text = search_text.strip()
    start_index = (current_page - 1) * data_per_page
    end_index = current_page * data_per_page

    user_id = request.session['LOGGED_IN_USER_ID']

    if list_type == 'User':
        user_type = request.data['userType']

        if user_type == 'backup':
            permit = 0
        elif user_type == 'search':
            permit = 1
        else:
            permit = None

        # 그룹 목록 구하기
        data_list = get_my_group_user_list(user_id)

        # 탈퇴 회원 제외하기
        data_list = data_list.exclude(bu_status=3)

        # 백업만, 검색만 허용 사용자 선택 시
        if permit is not None:
            data_list = data_list.filter(bu_permit=permit)

        # 검색어 입력 시
        if search_text != '':
            data_list = data_list.filter(Q(bu_firstname__contains=search_text) | Q(bu_lastname__contains=search_text))

        # 리스트 총 수
        total_count = len(data_list)

        # 컬럼 추가
        data_list = append_column(data_list, list_type)

        # 목록 new 포함 여부
        if len(data_list.filter(bu_new='Y')):
            have_new = True

        # order by
        if order_name == '':
            data_list = data_list.order_by('-bu_createdate')
        else:
            if order_type == 'asc':
                order_type = ''
            else:
                order_type = '-'

            if order_name == 'name':
                order_name = 'bu_firstname'
            elif order_name == 'policy':
                order_name = 'bu_policyname'
            elif order_name == 'general':
                order_name = 'bu_gnrllimit'
            elif order_name == 'cold':
                order_name = 'bu_coldlimit'
            elif order_name == 'ocr':
                order_name = 'bu_ocrlimit'
            elif order_name == 'kind':
                order_name = 'bu_permit'

            data_list = data_list.order_by(f'{order_type}{order_name}')

        # 리스트 갯수 제한
        data_list = data_list[start_index:end_index]

        for boxUser in data_list:
            boxUser.bu_pw = ""
    elif list_type == 'Computer' or list_type == 'Server':

        # 내 그룹 멤버 구하기
        my_group_user_list = get_my_group_user_list(user_id)

        users = my_group_user_list.values_list('bu_id', flat=True)
        user_ids = list(users)
        bs_sdcode = list(BoxStoragediv.objects.filter(sd_category=list_type).values_list('sd_code', flat=True))

        try:
            data_list = BoxUserstorage.objects.filter(bs_userid__in=user_ids).filter(
                Q(bs_sdcode__in=bs_sdcode) & ~Q(bs_status=4)).annotate(bs_new=Case(
                When(bs_createdate__gt=datetime.now() + timedelta(days=-7),
                     then=Value('Y')),
                default=Value('N'),
                output_field=CharField(),
            ))

            # 리스트 총 수
            total_count = len(data_list)

            # 목록 new 포함 여부
            if len(data_list.filter(bs_new='Y')):
                have_new = True

            # 컬럼 추가
            data_list = append_column(data_list, list_type)

            # 검색어 입력 시
            if search_text != '':
                data_list = data_list.filter(Q(bs_user_computer__icontains=search_text))

            # order by
            if order_name == '':
                data_list = data_list.order_by('-bs_createdate')
            else:
                if order_type == 'asc':
                    order_type = ''
                else:
                    order_type = '-'

                if order_name == 'manager':
                    order_name = 'bs_user_fullname'
                elif order_name == 'server':
                    order_name = 'bs_name'
                elif order_name == 'policy':
                    order_name = 'bs_policyname'
                elif order_name == 'general':
                    order_name = 'bs_gnrllimit'
                elif order_name == 'cold':
                    order_name = 'bs_coldlimit'
                elif order_name == 'ocr':
                    order_name = 'bs_ocrlimit'
                elif order_name == 'status':
                    order_name = 'bs_status'
                elif order_name == 'logdate':
                    order_name = 'bs_logdate'
                elif order_name == 'user':
                    order_name = 'bs_user_computer'

                data_list = data_list.order_by(f'{order_type}{order_name}')

            # 리스트 갯수 제한
            data_list = data_list[start_index:end_index]

        except BoxUserstorage.DoesNotExist:
            pass

    return data_list, total_count, have_new


def append_column(query_set, list_type):
    if list_type == 'User':

        # 권한 설정
        super_admin_br_id = 1
        admin_br_id = 2
        default_bu_roleid = 3

        query_set = query_set.annotate(
            bu_fullname=Case(
                When(
                    Q(bu_lastname=None) | Q(bu_lastname=''),
                    then='bu_firstname'
                ),
                default=Concat('bu_firstname', Value(' '), 'bu_lastname')
            ),
            bu_policyname=F('policy__bp_name'),
            bu_super_admin=Count('boxRoles', filter=Q(boxRoles__br_id=super_admin_br_id)),
            bu_admin=Count('boxRoles', filter=Q(boxRoles__br_id=admin_br_id)),
            bu_count_admin=Count('boxRoles',
                                 filter=(Q(boxRoles__br_id=super_admin_br_id) | Q(boxRoles__br_id=admin_br_id))),
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
            # Max(F('boxRoles__br_id')),
            bu_gnrlsto=Coalesce(Sum('boxuserstorage__bs_gnrlsto'), 0),
            bu_coldsto=Coalesce(Sum('boxuserstorage__bs_coldsto'), 0),
            bu_ocr=Coalesce(Sum('boxuserstorage__bs_ocr'), 0),
            bu_permitname=Case(
                When(
                    bu_permit=0,
                    then=Value('백업 전용')
                ),
                When(
                    bu_permit=1,
                    then=Value('검색 전용')
                ),
                When(
                    bu_permit=2,
                    then=Value('백업과 검색')
                ),
                output_field=CharField()
            ),
            bu_new=Case(
                When(bu_createdate__gt=datetime.now() + timedelta(days=-7),
                     then=Value('Y')),
                default=Value('N'),
                output_field=CharField(),
            ),
        )
    elif list_type == 'Computer' or list_type == 'Server':
        query_set = query_set.annotate(
            bs_user_fullname=Case(
                When(
                    Q(bs_userid__bu_lastname=None) | Q(bs_userid__bu_lastname=''),
                    then='bs_userid__bu_firstname'
                ),
                default=Concat('bs_userid__bu_firstname', Value(' '), 'bs_userid__bu_lastname')
            ),
            bs_policyname=F('bs_policyid__bp_name'),
            bs_user_computer=Case(
                When(
                    Q(bs_userid__bu_lastname=None) | Q(bs_userid__bu_lastname=''),
                    then=Concat('bs_userid__bu_firstname', Value(' / '), 'bs_name')
                ),
                default=Concat('bs_userid__bu_firstname', Value(' '), 'bs_userid__bu_lastname', Value(' / '), 'bs_name')
            ),
        )

    return query_set


def make_csv(request, list_type, subject_list, data_list):
    user_id = request.session['LOGGED_IN_USER_ID']
    user = BoxUsers.objects.get(bu_id=user_id)
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    file_name = list_type.lower() + 'List_' + user.bu_email + '_' + now + '.csv'
    folder_name = os.path.join('tmp', file_name)
    tmp_file_path = os.path.join(settings.MEDIA_ROOT, folder_name)

    file = open(tmp_file_path, 'w', encoding='utf-8', newline='')
    csv_file = csv.writer(file)

    for row in subject_list:
        csv_file.writerow(row)

    for row in data_list:
        csv_file.writerow(row)

    file.close()

    return tmp_file_path


def get_box_licensekey(license_key):
    # li_status가 5 (대기)인 것으로 확인
    try:
        box_licensekey = BoxLicensekey.objects.filter(li_status=5).get(li_licensekey=license_key)
    except BoxLicensekey.DoesNotExist:
        box_licensekey = None

    return box_licensekey
