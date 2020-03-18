from datetime import datetime
from django.db import transaction
from django.db.models import F, Q, Case, When, Value, CharField
from django.db.models.functions import Concat, TruncDate
from rest_framework import views
from rest_framework.response import Response

from .serializers import SettingSerializer, CodeSerializer, SettingadvanceSerializer, UsersSerializer, userStorageListSerializer
from common.utils.admin_utils import *
from user.common.service.common_service import get_my_account_user, get_my_group_user_list
from user.main.models import BoxUsers
from user.models import BoxCode, BoxSetting, BoxSettingadvance, BoxUserstorage

"""
    관리 - 설정
"""


# 설정 > 보유 설정 - 조회
class PossessionSetting(views.APIView):
    @transaction.atomic
    def post(self, request):
        # account의 setting 구하기
        user_id = request.session['LOGGED_IN_USER_ID']
        box_setting = get_account_user_setting(user_id)

        serialized_setting = SettingSerializer(box_setting).data

        data = {
            'setting': serialized_setting,
            'code': Code.SUCCESS.value,
        }

        return Response(data)


# 세대 카테고리, 기간 카테고리 조회 (selectbox용)
class GetCategory(views.APIView):
    @transaction.atomic
    def post(self, request):
        # 세대별
        box_code_generation = BoxCode.objects.filter(pcode__bc_code='A01').order_by('bc_id')
        serialized_code_generation = CodeSerializer(box_code_generation, many=True).data

        # 기간별
        box_code_period = BoxCode.objects.filter(pcode__bc_code='A02').order_by('bc_id')
        serialized_code_period = CodeSerializer(box_code_period, many=True).data

        data = {
            'code': Code.SUCCESS.value,
            'generation': serialized_code_generation,
            'period': serialized_code_period,
        }
        return Response(data)


# 설정 저장
class SaveSetting(views.APIView):
    @transaction.atomic
    def post(self, request):

        tab_name = request.data['tabName']
        data = request.data['data']

        # account의 setting 구하기
        user_id = request.session['LOGGED_IN_USER_ID']
        box_setting = get_account_user_setting(user_id)

        # 보유 설정 저장
        if tab_name == 'possessionSetting':
            general = data['general']
            cold = data['cold']
            delete = data['delete']

            # update
            st_storageval = general['val']
            st_coldval = cold['val']
            st_retperfile = delete['val']

            box_setting.st_storagediv = general['div']
            box_setting.stovalCode = BoxCode.objects.get(bc_code=st_storageval)
            box_setting.st_colddiv = cold['div']
            box_setting.coldvalCode = BoxCode.objects.get(bc_code=st_coldval)
            box_setting.retperfileCode = BoxCode.objects.get(bc_code=st_retperfile)

        # 클라이언트 스토리지 경고 설정 저장
        elif tab_name == 'warningSetting':
            hide_warn = data['hideWarn']

            # update
            box_setting.st_period = hide_warn['val']

        box_setting.save()

        data = {
            'code': Code.SUCCESS.value
        }
        return Response(data)


# 보유설정(상세) 목록 조회
class GetList(views.APIView):
    @transaction.atomic
    def post(self, request):
        current_page = int(request.data['currentPage'])
        data_per_page = int(request.data['dataPerPage'])
        order_name = request.data['orderName']
        order_type = request.data['orderType']

        start_index = (current_page - 1) * data_per_page
        end_index = current_page * data_per_page

        user_id = request.session['LOGGED_IN_USER_ID']
        my_group_user_list = get_my_group_user_list(user_id)    # 내 그룹 사용자 목록 조회
        data_list = BoxSettingadvance.objects.filter(boxUser__in=my_group_user_list).annotate(
            sa_user_name=Case(
                When(
                    Q(boxUser__bu_lastname=None) | Q(boxUser__bu_lastname=''),
                    then='boxUser__bu_firstname'
                ),
                default=Concat('boxUser__bu_firstname', Value(' '), 'boxUser__bu_lastname'),
                output_field=CharField()
            ),
            sa_sto_name=F('boxUserstorage__bs_name'),
            sa_div_name=Case(
                When(
                    Q(sa_div='D'),
                    then=Value('날짜')
                ),
                default=Value('세대'),
                output_field=CharField()
            ),
            sa_settingval_name=F('boxCode__bc_name'),
            sa_modifydate_name=TruncDate('sa_modifydate')
        )

        # 리스트 총 수
        total_count = len(data_list)

        # order by
        if order_name == '':
            data_list = data_list.order_by('-sa_modifydate')
        else:
            if order_type == 'asc':
                order_type = ''
            else:
                order_type = '-'

            if order_name == 'username':
                order_name = 'sa_user_name'
            elif order_name == 'storage':
                order_name = 'sa_sto_name'
            elif order_name == 'path':
                order_name = 'sa_path'
            elif order_name == 'div':
                order_name = 'sa_div'
            elif order_name == 'code':
                order_name = 'boxCode'
            elif order_name == 'modifydate':
                order_name = 'sa_modifydate'

            data_list = data_list.order_by(f'{order_type}{order_name}')

        # 리스트 갯수 제한
        data_list = data_list[start_index:end_index]

        serialized_box_settingadvance_list = SettingadvanceSerializer(data_list, many=True).data

        data = {
            'code': Code.SUCCESS.value,
            'list': serialized_box_settingadvance_list,
            'totalCount': total_count
        }

        return Response(data)


# 보유설정(상세) 추가
class CreatePossessionDetailSetting(views.APIView):
    @transaction.atomic
    def post(self, request):
        userid = request.data['userid']
        stoid = request.data['stoid']
        path = request.data['path']
        div = request.data['div']
        settingval = request.data['settingval']

        box_user = BoxUsers.objects.get(pk=userid)
        box_userstorage = BoxUserstorage.objects.get(bs_id=stoid)
        box_code = BoxCode.objects.get(bc_code=settingval)
        BoxSettingadvance.objects.create(boxUser=box_user, boxUserstorage=box_userstorage, sa_path=path, sa_div=div,
                                         boxCode=box_code)

        data = {
            'code': Code.SUCCESS.value,
        }

        return Response(data)


# 보유설정(상세) 수정
class UpdatePossessionDetailSetting(views.APIView):
    @transaction.atomic
    def post(self, request):
        data = {
            'code': Code.SUCCESS.value
        }

        return Response(data)


# 보유설정(상세) 삭제
class DeletePossessionDetailSetting(views.APIView):
    @transaction.atomic
    def post(self, request):
        id = request.data['id']

        data = {
            'code': Code.SUCCESS.value
        }

        return Response(data)


# account 포함 하위의 user list 구하기
class GetGroupUserList(views.APIView):
    @transaction.atomic
    def post(self, request):

        try:
            user_id = request.data['userId']
        except KeyError:
            user_id = request.session['LOGGED_IN_USER_ID']

        group_user_list = get_my_group_user_list(user_id)
        serialized_group_user_list = UsersSerializer(group_user_list, many=True).data


        data = {
            'code': Code.SUCCESS.value,
            'userList': serialized_group_user_list
        }

        if group_user_list is None:
            data['code'] = Code.NO_EXIST_USER.value

        return Response(data)


# 해당 유저의 단말기 목록 구하기
class GetStorageList(views.APIView):
    @transaction.atomic
    def post(self, request):
        try:
            user_id = request.data['userId']
        except KeyError:
            user_id = request.session['LOGGED_IN_USER_ID']

        storage_list = BoxUserstorage.objects.filter(bs_userid__bu_id=user_id)
        serialized_storage_list = userStorageListSerializer(storage_list, many=True).data

        data = {
            'code': Code.SUCCESS.value,
            'storageList': serialized_storage_list
        }

        return Response(data)
    

# 보유설정(상세) 추가
class CreatePossessionDetailSetting(views.APIView):
    @transaction.atomic
    def post(self, request):
        user_id = request.data['userid']
        stoid = request.data['stoid']
        path = request.data['path']
        div = request.data['div']
        settingval = request.data['settingval']

        box_user = BoxUsers.objects.get(bu_id=user_id)
        box_userstorage = BoxUserstorage.objects.get(bs_id=stoid)
        box_code = BoxCode.objects.get(bc_code=settingval)

        BoxSettingadvance.objects.create(boxUser=box_user, boxUserstorage=box_userstorage, sa_path=path, sa_div=div, boxCode=box_code)

        data = {
            'code': Code.SUCCESS.value,
        }

        return Response(data)


# 보유설정(상세) 편집
class UpdatePossessionDetailSetting(views.APIView):
    @transaction.atomic
    def post(self, request):
        id = request.data['id']
        mode = request.data['mode']
        user_id = request.data['userid']
        stoid = request.data['stoid']
        path = request.data['path']
        div = request.data['div']
        settingval = request.data['settingval']

        box_settingadvance = BoxSettingadvance.objects.get(sa_id=id)

        if mode == 'update':
            box_user = BoxUsers.objects.get(bu_id=user_id)
            box_userstorage = BoxUserstorage.objects.get(bs_id=stoid)
            box_code = BoxCode.objects.get(bc_code=settingval)

            box_settingadvance.boxUser = box_user
            box_settingadvance.boxUserstorage = box_userstorage
            box_settingadvance.sa_path = path
            box_settingadvance.sa_div = div
            box_settingadvance.boxCode = box_code
            box_settingadvance.save()
        elif mode == 'delete':
            box_settingadvance.delete()

        data = {
            'code': Code.SUCCESS.value,
        }

        return Response(data)



# account의 setting 조회
def get_account_user_setting(user_id):
    # account_user 구하기
    account_user = get_my_account_user(user_id)

    try:
        box_setting = BoxSetting.objects.get(accountUser=account_user)
    except BoxSetting.DoesNotExist:
        box_code_10gen = BoxCode.objects.get(bc_code='A0110')  # 10세대
        box_code_3days = BoxCode.objects.get(bc_code='A0201')  # 3일
        box_setting = BoxSetting.objects.create(stovalCode=box_code_10gen, coldvalCode=box_code_10gen,
                                                retperfileCode=box_code_3days, accountUser=account_user)

    return box_setting



