from django.db.models import OuterRef, Subquery, Count, IntegerField
from django.db.models.functions import Coalesce
from rest_framework import views, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from collections import Counter
from .models import BoxPolicyfiles, BoxVariable, BoxPolicysetting, BoxPolicypermission, BoxPolicyfolderfiles
from .serializers import *
from django.http import JsonResponse
import json
from django.utils import timezone

###정책리스트###
from ..main.models import BoxUsers
from ..models import BoxUserstorage


class policy_list(views.APIView):
    def get(self, request):
        userid = request.GET.get('userid')
        email = request.GET.get('email')
        accountid = request.GET.get('accountid')

        usercnt = BoxUserstorage.objects.filter(bs_policyid__in=OuterRef('bp_id'))
        usercntnew = BoxUsers.objects.filter(policy__in=OuterRef('bp_id'))

        todos = Policy.objects.annotate(
            usercnt=Coalesce(Subquery(
                usercntnew.values('policy').annotate(count=Count('pk')).values('count'),
                output_field=IntegerField()), 0),
            servercnt=Coalesce(Subquery(
                usercnt.filter(bs_sdcode='S').values('bs_policyid').annotate(count=Count('pk')).values('count'),
                output_field=IntegerField()), 0),
        ).filter(bp_resellerid=accountid).order_by("-bp_createdate")

        todolist = list(todos)
        response_data = policyListSerializer(todolist, many=True).data

        return Response(response_data)


##정책검색##
class policy_search(views.APIView):
    def get(self, request):
        userid = request.GET.get('userid')
        searchval = request.GET.get('searchval')
        accountid = request.GET.get('accountid')

        usercnt = BoxUserstorage.objects.filter(bs_policyid__in=OuterRef('bp_id'))
        todos = Policy.objects.annotate(
            usercnt=Coalesce(Subquery(
                usercnt.values('bs_policyid').annotate(count=Count('pk')).values('count'),
                output_field=IntegerField()), 0),
            servercnt=Coalesce(Subquery(
                usercnt.filter(bs_sdcode='S').values('bs_policyid').annotate(count=Count('pk')).values('count'),
                output_field=IntegerField()), 0),
        ).filter(bp_resellerid=accountid, bp_name__icontains=searchval).order_by("-bp_createdate")

        # todos = Policy.objects.filter(bp_resellerid=accountid, bp_name__contains=searchval)
        todolist = list(todos)
        response_data = policyListSerializer(todolist, many=True).data

        return Response(response_data)


###정책 할당되어 있 유저정보###
class policy_list_usercnt(views.APIView):
    def get(self, request):
        bp_id = request.GET.get('bp_id')
        bp_div = request.GET.get('bp_div')

        print("bp_div=====", bp_div)
        if bp_div == 'U':
            policy_usercnt = BoxUserstorage.objects.filter(bs_policyid=bp_id).order_by('-bs_createdate')
        else:
            policy_usercnt = BoxUserstorage.objects.filter(bs_policyid=bp_id, bs_sdcode=bp_div).order_by(
                '-bs_createdate')

        todolist = list(policy_usercnt)
        response_data = userStorageListSerializer(todolist, many=True).data

        return Response(response_data)


# 정책수정 리스트###
class policy_editlist(views.APIView):
    def get(self, request):
        bp_id = request.GET.get('bpId')
        policy = Policy.objects.filter(bp_id=bp_id).order_by("-bp_createdate")
        file_list = BoxPolicyfiles.objects.filter(bf_policyid=bp_id)
        general_policydata = BoxPolicydata.objects.filter(pd_policyid=bp_id, pd_div='G')
        cold_policydata = BoxPolicydata.objects.filter(pd_policyid=bp_id, pd_div='C')
        general_file = BoxPolicyfiles.objects.filter(bf_policyid=bp_id, bf_type='G', bf_div=1).order_by("bf_id")
        general_folder = BoxPolicyfiles.objects.filter(bf_policyid=bp_id, bf_type='G', bf_div=2).order_by("bf_id")
        cold_file = BoxPolicyfiles.objects.filter(bf_policyid=bp_id, bf_type='C', bf_div=1).order_by("bf_id")
        cold_folder = BoxPolicyfiles.objects.filter(bf_policyid=bp_id, bf_type='C', bf_div=2).order_by("bf_id")
        ocr_file = BoxPolicyfiles.objects.filter(bf_policyid=bp_id, bf_type='O', bf_div=1)
        ocr_folder = BoxPolicyfiles.objects.filter(bf_policyid=bp_id, bf_type='O', bf_div=2)
        # ocr_file = BoxPolicyfiles.objects.filter(bf_policyid=bp_id, bf_type='O')
        # ex_file = BoxPolicyfiles.objects.filter(bf_policyid=bp_id, bf_type='E')
        # dual_file = BoxPolicyfiles.objects.filter(bf_policyid=bp_id, bf_type='D')

        fileList = policyFileSerializer(file_list, context={'request': request}, many=True)

        policyData = policyEditListSerializer(policy, context={'request': request}, many=True)
        generalPolicydata = general_policydataEditListSerializer(general_policydata, context={'request': request},
                                                                 many=True)
        coldPolicydata = general_policydataEditListSerializer(cold_policydata, context={'request': request}, many=True)
        generalFile = policyFileSerializer(general_file, context={'request': request}, many=True)
        generalFolder = policyFileSerializer(general_folder, context={'request': request}, many=True)

        coldFile = policyFileSerializer(cold_file, context={'request': request}, many=True)
        coldFolder = policyFileSerializer(cold_folder, context={'request': request}, many=True)

        ocrFile = policyFileSerializer(ocr_file, context={'request': request}, many=True)
        ocrFolder = policyFileSerializer(ocr_folder, context={'request': request}, many=True)

        t1 = 10 + 5
        string1 = "The result of 10+5 is {}".format(t1)
        print("string1>>>>>>>", string1)

        return Response({
            'policyData': policyData.data,
            'fileList': fileList.data,
            'generalPolicydata': generalPolicydata.data,
            'coldPolicydata': coldPolicydata.data,
            'generalFile': generalFile.data,
            'generalFolder': generalFolder.data,
            'coldFile': coldFile.data,
            'coldFolder': coldFolder.data,
            'ocrFile': ocrFile.data,
            'ocrFolder': ocrFolder.data,
        })


###정책 할당되어 있 유저정보###
class policy_variablelist(views.APIView):
    def get(self, request):
        # bp_id = request.GET.get('bp_id')
        # bp_div = request.GET.get('bp_div')
        # print("bp_div=====", bp_div)
        policy_variable = BoxVariable.objects.all().order_by('bv_id')
        todolist = list(policy_variable)
        response_data = policyVariableSerializer(todolist, many=True).data

        return Response(response_data)


# 콜드스토리지 파일 및 폴더 리스트###
class policy_coldFilelist(views.APIView):
    def get(self, request):
        bp_id = request.GET.get('bpId')
        cold_file = BoxPolicyfiles.objects.filter(bf_policyid=bp_id, bf_type='C', bf_div=1)
        cold_folder = BoxPolicyfiles.objects.filter(bf_policyid=bp_id, bf_type='C', bf_div=2)
        coldFile = policyFileSerializer(cold_file, context={'request': request}, many=True)
        coldFolder = policyFileSerializer(cold_folder, context={'request': request}, many=True)

        return Response({
            'coldFile': coldFile.data,
            'coldFolder': coldFolder.data
        })


# OCR데이터 파일 및 폴더 리스트##
class policy_ocrFilelist(views.APIView):
    def get(self, request):
        bp_id = request.GET.get('bpId')
        ocr_file = BoxPolicyfiles.objects.filter(bf_policyid=bp_id, bf_type='O', bf_div=1)
        ocr_folder = BoxPolicyfiles.objects.filter(bf_policyid=bp_id, bf_type='O', bf_div=2)
        ocrFile = policyFileSerializer(ocr_file, context={'request': request}, many=True)
        ocrFolder = policyFileSerializer(ocr_folder, context={'request': request}, many=True)

        return Response({
            'ocrFile': ocrFile.data,
            'ocrFolder': ocrFolder.data
        })


# 확장 파일 및 폴더 리스트##
class policy_exFilelist(views.APIView):
    def get(self, request):
        bp_id = request.GET.get('bpId')
        ex_file = BoxPolicyfiles.objects.filter(bf_policyid=bp_id, bf_type='E', bf_div=1)
        ex_folder = BoxPolicyfiles.objects.filter(bf_policyid=bp_id, bf_type='E', bf_div=2)
        exFile = policyFileSerializer(ex_file, context={'request': request}, many=True)
        exFolder = policyFileSerializer(ex_folder, context={'request': request}, many=True)

        return Response({
            'exFile': exFile.data,
            'exFolder': exFolder.data
        })


# 확장자 리스트##
class policy_extensionlist(views.APIView):
    def get(self, request):
        bp_id = request.GET.get('bpId')
        ex_list = BoxPolicyextension.objects.filter(ex_policyid=bp_id)
        todolist = list(ex_list)
        response_data = policyExtensionSerializer(todolist, many=True).data

        return Response(response_data)


# 설정 리스트##
class policy_settinglist(views.APIView):
    def get(self, request):
        bp_id = request.GET.get('bpId')
        setting_list = BoxPolicysetting.objects.filter(ps_policyid=bp_id)
        todolist = list(setting_list)
        response_data = policySettingSerializer(todolist, many=True).data

        return Response(response_data)


# 권한 리스트##
class policy_permissionlist(views.APIView):
    def get(self, request):
        bp_id = request.GET.get('bpId')

        setting_list = BoxPolicypermission.objects.filter(pp_policyid=bp_id)
        todolist = list(setting_list)
        response_data = policyPermissionSerializer(todolist, many=True).data

        return Response(response_data)


# 정책생성##
@api_view(['POST'])
def policy_create(request):
    if request.method == 'POST':
        jtopy = json.dumps(request.data)
        json_data = json.loads(jtopy)
        bp_id = json_data['id']
        bp_name = json_data['name']
        dualbackchk = json_data['dualbackchk']
        dualpath = json_data['dualpath']
        dualsizechk = json_data['dualsizechk']
        dualsize = json_data['dualsize']
        bp_account = json_data['account_id']
        policydata = json_data['policydata']

        policyfile = json_data['policyfiles']
        policyfolder = json_data['policyfolderfiles']
        policycoldfiles = json_data['policycoldfiles']
        policycoldfolder = json_data['policycoldfolder']
        ocrfile = json_data['ocrfile']
        ocrfolder = json_data['ocrfolder']
        extensionfile = json_data['extensionfile']
        extensionfolder = json_data['extensionfolder']
        policyextension = json_data['policyextension']
        policysetting = json_data['policysetting']
        policypermission = json_data['policypermission']

        # dnf = [k for k, v in policyfile.items() if v > 0]
        sumfile = policyfile
        sumfile += policyfolder
        sumfile += policycoldfiles
        sumfile += policycoldfolder
        sumfile += ocrfile
        sumfile += ocrfolder
        sumfile += extensionfile
        sumfile += extensionfolder

        policy_insert = Policy(
            # bp_id=bp_id,
            bp_name=bp_name,
            bp_resellerid=int(bp_account)
        )
        policy_insert.save()
        msg = '정책이 생성 되었습니다.'
        bp_idx = policy_insert.pk

        for pd in policydata:
            policynomal_insert = BoxPolicydata(
                # bp_id=bp_id,
                pd_div=pd['div'],
                pd_emailchk=pd['emailchk'],
                pd_wallpaperchk=pd['wallpaperchk'],
                pd_documentchk=pd['documentchk'],
                pd_officechk=pd['officechk'],
                pd_acntnfilechk=pd['acntnfilechk'],
                pd_bookmarkchk=pd['bookmarkchk'],
                pd_imagechk=pd['imagechk'],
                pd_musicchk=pd['musicchk'],
                pd_videochk=pd['videochk'],
                pd_ebookchk=pd['ebookchk'],
                pd_createdate=timezone.now(),
                pd_modifydate=timezone.now(),
                pd_policyid=bp_idx
            )
            policynomal_insert.save()

        for pf in sumfile:
            policyfile_insert = BoxPolicyfiles(
                # bf_id=bf_id,
                bf_type=pf['bf_type'],
                bf_filepath=pf['bf_filepath'],
                bf_folderpath=pf['bf_folderpath'],
                bf_createdate=timezone.now(),
                bf_extensionchk=pf['bf_extensionchk'],
                bf_filetypechk=pf['bf_filetypechk'],
                bf_regexchk=pf['bf_regexchk'],
                bf_expression=pf['bf_expression'],
                bf_filebackchk=pf['bf_filebackchk'],
                bf_size=pf['bf_size'],
                bf_volumechk=pf['bf_volumechk'],
                bf_datebackchk=pf['bf_datebackchk'],
                bf_dateback=pf['bf_dateback'],
                bf_div=pf['bf_div'],
                bf_policyid=bp_idx
            )
            policyfile_insert.save()

        policyextension_insert = BoxPolicyextension(
            # bf_id=bf_id,
            ex_shadowcopy=policyextension['shadowcopy'],
            ex_blocklevel=policyextension['blocklevel'],
            ex_ebook=policyextension['ebook'],
            ex_office=policyextension['office'],
            ex_account=policyextension['account'],
            ex_exclusion=policyextension['exclusion'],
            ex_policyid=bp_idx,
        )
        policyextension_insert.save()

        policysetting_insert = BoxPolicysetting(
            # bf_id=bf_id,
            ps_hidefile=policysetting['hidefile'],
            ps_battery=policysetting['battery'],
            ps_presentation=policysetting['presentation'],
            ps_policysetting=policysetting['policysetting'],
            ps_multithread=policysetting['multithread'],
            ps_lan=policysetting['lan'],
            ps_wifi=policysetting['wifi'],
            ps_lte=policysetting['lte'],
            ps_schedulediv=policysetting['schedulediv'],
            ps_stime=policysetting['stime'],
            ps_itime=policysetting['itime'],
            ps_backtime=policysetting['backtime'],
            ps_starttime=policysetting['starttime'],
            ps_endtime=policysetting['endtime'],
            ps_endtimechk=policysetting['endtimechk'],
            ps_netdiv=policysetting['netdiv'],
            ps_upspeed=policysetting['upspeed'],
            ps_banddiv=policysetting['banddiv'],
            ps_bandstarttime=policysetting['bandstarttime'],
            ps_bandendtime=policysetting['bandendtime'],
            ps_weekday=policysetting['weekday'],
            ps_policyid=bp_idx,
        )
        policysetting_insert.save()

        policypermission_insert = BoxPolicypermission(
            # bf_id=bf_id,
            pp_deletechk=policypermission['pp_deletechk'],
            pp_sharingchk=policypermission['pp_sharingchk'],
            pp_editchk=policypermission['pp_editchk'],
            pp_pwchk=policypermission['pp_pwchk'],
            pp_changechk=policypermission['pp_changechk'],
            pp_clientdiv=policypermission['pp_clientdiv'],
            pp_pluspw=policypermission['pp_pluspw'],
            pp_backupchk=policypermission['pp_backupchk'],
            pp_pausechk=policypermission['pp_pausechk'],
            pp_terminate=policypermission['pp_terminate'],
            pp_remove=policypermission['pp_remove'],
            pp_policyid=bp_idx,
        )
        policypermission_insert.save()

    return Response("등록완료")


##일반스토리지 폴더필터##
class policy_generalfilter(views.APIView):
    def get(self, request):
        bf_id = request.GET.get('bfId')

        generalfilter_list = BoxPolicyfiles.objects.filter(bf_id=bf_id)
        todolist = list(generalfilter_list)
        response_data = policyGeneralfilterSerializer(todolist, many=True).data

        return Response(response_data)


# 정책수정##
@api_view(['GET', 'PUT', 'DELETE'])
def policy_generalchk(request):
    jtopy = json.dumps(request.data)
    json_data = json.loads(jtopy)
    policyname = json_data['name']
    policyid = json_data['id']
    policydata = json_data['policydata']

    print("POLICYname=============================", json_data['name'])
    try:
        Policy_update = Policy.objects.get(bp_id=json_data['id'])
        Policy_update.bp_name = json_data['name']
        Policy_update.bp_modifydate = timezone.now()
        Policy_update.save()
        msg = '정책이 수정 되었습니다.'
    except Policy.DoesNotExist:
        pass

    for pd in policydata:
        # print("pd=============================", pd['id'])
        # 콜드스토리지 작업시 삭제 if pd['div'] == 'G':
        # if pd['div'] == 'G':
        policydata_update = BoxPolicydata.objects.get(pd_id=pd['id'])
        policydata_update.pd_div = pd['div']
        policydata_update.pd_emailchk = pd['emailchk']
        policydata_update.pd_wallpaperchk = pd['wallpaperchk']
        policydata_update.pd_documentchk = pd['documentchk']
        policydata_update.pd_officechk = pd['officechk']
        policydata_update.pd_acntnfilechk = pd['acntnfilechk']
        policydata_update.pd_bookmarkchk = pd['bookmarkchk']
        policydata_update.pd_imagechk = pd['imagechk']
        policydata_update.pd_musicchk = pd['musicchk']
        policydata_update.pd_videochk = pd['videochk']
        policydata_update.pd_ebookchk = pd['ebookchk']
        policydata_update.pd_createdate = timezone.now()
        policydata_update.pd_modifydate = timezone.now()
        policydata_update.save()

    msg = '정책이 수정 되었습니다.'

    data = {
        'result': msg,
    }

    response = JsonResponse(data)

    return response


# 파일수정##
@api_view(['GET', 'PUT', 'DELETE'])
def policy_edit(request):
    # global policyfile
    jtopy = json.dumps(request.data)
    json_data = json.loads(jtopy)
    policy_id = request.data.get('id')
    policyfile = json_data['policyfiles']

    file_delete = []
    raw_id = []
    file_id = []
    # print("policyfileGGGGGGGGGGG=============================", policyfile)
    try:
        file_list = BoxPolicyfiles.objects.filter(bf_policyid=policy_id, bf_div=1, bf_type='G')

        for raw in policyfile:
            raw_id.append(raw['bf_id'])

        for fl in file_list:
            file_id.append(fl.bf_id)

        for raw in file_id:
            if raw not in raw_id:
                file_delete.append(raw)

        # print("file_deleteGGGGGGGG=============================", file_delete)

        for pf in policyfile:
            bf_id = pf['bf_id']
            if bf_id == '':
                bf_id = None

            if bf_id == None:
                # print("insertGGGGGGGGGGG=============================", pf)
                policyfile_insert = BoxPolicyfiles(
                    bf_type=pf['bf_type'],
                    bf_filepath=pf['bf_filepath'],
                    bf_folderpath=pf['bf_type'],
                    bf_createdate=timezone.now(),
                    bf_extensionchk=pf['bf_extensionchk'],
                    bf_filetypechk=pf['bf_filetypechk'],
                    bf_regexchk=pf['bf_regexchk'],
                    bf_expression=pf['bf_expression'],
                    bf_filebackchk=pf['bf_filebackchk'],
                    bf_size=pf['bf_size'],
                    bf_volumechk=pf['bf_volumechk'],
                    bf_datebackchk=pf['bf_datebackchk'],
                    bf_dateback=pf['bf_dateback'],
                    bf_div=pf['bf_div'],
                    bf_policyid=policy_id
                )
                policyfile_insert.save()
                msg = '정책이 수정 되었습니다.'
            else:
                if len(file_delete) is not 0:
                    for fd in file_delete:
                        try:
                            gfile_delete = BoxPolicyfiles.objects.get(bf_id=fd)
                            gfile_delete.delete()
                        except BoxPolicyfiles.DoesNotExist:
                            pass
                else:
                    policyfile_update = BoxPolicyfiles.objects.get(bf_id=bf_id)
                    policyfile_update.bf_filepath = pf['bf_filepath']
                    policyfile_update.save()
                msg = '정책이 수정 되었습니다.'
    except (ValueError, IndexError) as ex:
        pass
    except BoxPolicyfiles.DoesNotExist:
        pass

    try:
        Policy_update = Policy.objects.get(bp_id=policy_id)
        Policy_update.bp_modifydate = timezone.now()
        Policy_update.save()
    except Policy.DoesNotExist:
        pass

    msg = '정책이 수정 되었습니다.'

    data = {
        'result': msg,
    }

    response = JsonResponse(data)

    return response


# 정책수정##
@api_view(['GET', 'PUT', 'DELETE'])
def policy_generalfolderedit(request):
    # global policyfile
    jtopy = json.dumps(request.data)
    json_data = json.loads(jtopy)
    policy_id = request.data.get('id')
    policyfile = json_data['policyfolderfiles']

    file_delete = []
    raw_id = []
    file_id = []
    print("policy_generalfolderedit=============================", policyfile)
    try:
        file_list = BoxPolicyfiles.objects.filter(bf_policyid=policy_id, bf_div=2, bf_type='G')

        for raw in policyfile:
            raw_id.append(raw['bf_id'])

        for fl in file_list:
            file_id.append(fl.bf_id)

        for raw in file_id:
            if raw not in raw_id:
                file_delete.append(raw)

        for pf in policyfile:
            bf_id = pf['bf_id']
            if bf_id == '' or bf_id == 0:
                bf_id = None

            # print("folderedit=bf_id============================", bf_id)

            if bf_id == None:
                # print("insert=============================", pf['bf_expression'])
                policyfolder_insert = BoxPolicyfolderfiles(
                    bf_type=pf['bf_type'],
                    bf_filepath=pf['bf_filepath'],
                    bf_folderpath=pf['bf_folderpath'],
                    bf_createdate=timezone.now(),
                    bf_extensionchk=pf['bf_extensionchk'],
                    bf_filetypechk=pf['bf_filetypechk'],
                    bf_regexchk=pf['bf_regexchk'],
                    bf_expression=pf['bf_expression'],
                    bf_filebackchk=pf['bf_filebackchk'],
                    bf_size=pf['bf_size'],
                    bf_volumechk=pf['bf_volumechk'],
                    bf_datebackchk=pf['bf_datebackchk'],
                    bf_dateback=pf['bf_dateback'],
                    bf_div=pf['bf_div'],
                    bf_policyid=policy_id
                )
                policyfolder_insert.save()
                msg = '정책이 수정 되었습니다.'
            else:
                if len(file_delete) is not 0:
                    for fd in file_delete:
                        try:
                            gfile_delete = BoxPolicyfiles.objects.get(bf_id=fd)
                            gfile_delete.delete()
                        except BoxPolicyfiles.DoesNotExist:
                            pass
                else:
                    policyfile_update = BoxPolicyfiles.objects.get(bf_id=bf_id)
                    policyfile_update.bf_folderpath = pf['bf_folderpath']
                    policyfile_update.bf_extensionchk = pf['bf_extensionchk']
                    policyfile_update.bf_filetypechk = pf['bf_filetypechk']
                    policyfile_update.bf_regexchk = pf['bf_regexchk']
                    policyfile_update.bf_expression = pf['bf_expression']
                    policyfile_update.bf_filebackchk = pf['bf_filebackchk']
                    policyfile_update.bf_size = pf['bf_size']
                    policyfile_update.bf_volumechk = pf['bf_volumechk']
                    policyfile_update.bf_datebackchk = pf['bf_datebackchk']
                    policyfile_update.bf_dateback = pf['bf_dateback']
                    policyfile_update.bf_policyid = pf['bf_policyid']
                    policyfile_update.bf_div = pf['bf_div']
                    policyfile_update.save()
                msg = '정책이 수정 되었습니다.'
    except (ValueError, IndexError) as ex:
        pass
    except BoxPolicyfiles.DoesNotExist:
        pass

    try:
        Policy_update = Policy.objects.get(bp_id=policy_id)
        Policy_update.bp_modifydate = timezone.now()
        Policy_update.save()
    except Policy.DoesNotExist:
        pass

    msg = '정책이 수정 되었습니다.'

    data = {
        'result': msg,
    }

    response = JsonResponse(data)

    return response


# 정책수정##
@api_view(['GET', 'PUT', 'DELETE'])
def policy_editcoldfile(request):
    # global policyfile
    jtopy = json.dumps(request.data)
    json_data = json.loads(jtopy)
    policy_id = request.data.get('id')
    policyfile = json_data['policycoldfiles']

    file_delete = []
    raw_id = []
    file_id = []
    # print("policyfilesssssss=============================", policyfile)
    try:
        file_list = BoxPolicyfiles.objects.filter(bf_policyid=policy_id, bf_div=1, bf_type='C')

        for raw in policyfile:
            raw_id.append(raw['bf_id'])

        for fl in file_list:
            file_id.append(fl.bf_id)

        for raw in file_id:
            if raw not in raw_id:
                file_delete.append(raw)

        # print("file_deletesssssss=============================", file_delete)

        for pf in policyfile:
            bf_id = pf['bf_id']
            if bf_id == '':
                bf_id = None

            if bf_id == None:
                print("insertsssssss=============================", pf)
                policyfile_insert = BoxPolicyfiles(
                    bf_type=pf['bf_type'],
                    bf_filepath=pf['bf_filepath'],
                    bf_folderpath=pf['bf_type'],
                    bf_createdate=timezone.now(),
                    bf_extensionchk=pf['bf_extensionchk'],
                    bf_filetypechk=pf['bf_filetypechk'],
                    bf_regexchk=pf['bf_regexchk'],
                    bf_expression=pf['bf_expression'],
                    bf_filebackchk=pf['bf_filebackchk'],
                    bf_size=pf['bf_size'],
                    bf_volumechk=pf['bf_volumechk'],
                    bf_datebackchk=pf['bf_datebackchk'],
                    bf_dateback=pf['bf_dateback'],
                    bf_div=pf['bf_div'],
                    bf_policyid=policy_id
                )
                policyfile_insert.save()
                msg = '정책이 수정 되었습니다.'
            else:
                if len(file_delete) is not 0:
                    for fd in file_delete:
                        # print("file_deletesssss=============================", fd)
                        try:
                            gfile_delete = BoxPolicyfiles.objects.get(bf_id=fd)
                            gfile_delete.delete()
                        except BoxPolicyfiles.DoesNotExist:
                            pass
                else:
                    policyfile_update = BoxPolicyfiles.objects.get(bf_id=bf_id)
                    policyfile_update.bf_filepath = pf['bf_filepath']
                    policyfile_update.save()
                msg = '정책이 수정 되었습니다.'
    except (ValueError, IndexError) as ex:
        pass
    except BoxPolicyfiles.DoesNotExist:
        pass

    try:
        Policy_update = Policy.objects.get(bp_id=policy_id)
        Policy_update.bp_modifydate = timezone.now()
        Policy_update.save()
    except Policy.DoesNotExist:
        pass

    msg = '정책이 수정 되었습니다.'

    data = {
        'result': msg,
    }

    response = JsonResponse(data)

    return response


# 정책수정##
@api_view(['GET', 'PUT', 'DELETE'])
def policy_coldfolderedit(request):
    # global policyfile
    jtopy = json.dumps(request.data)
    json_data = json.loads(jtopy)
    policy_id = request.data.get('id')
    policyfile = json_data['coldfolderfiles']

    file_delete = []
    raw_id = []
    file_id = []
    # print("policy_coldfolderedit=============================", policyfile)
    try:
        file_list = BoxPolicyfiles.objects.filter(bf_policyid=policy_id, bf_div=2, bf_type='C')

        for raw in policyfile:
            raw_id.append(raw['bf_id'])

        for fl in file_list:
            file_id.append(fl.bf_id)

        for raw in file_id:
            if raw not in raw_id:
                file_delete.append(raw)

        for pf in policyfile:
            bf_id = pf['bf_id']
            if bf_id == '' or bf_id == 0:
                bf_id = None

            # print("folderedit=bf_id============================", bf_id)

            if bf_id == None:
                print("insert=============================", pf['bf_expression'])
                policyfolder_insert = BoxPolicyfolderfiles(
                    bf_type=pf['bf_type'],
                    bf_filepath=pf['bf_filepath'],
                    bf_folderpath=pf['bf_folderpath'],
                    bf_createdate=timezone.now(),
                    bf_extensionchk=pf['bf_extensionchk'],
                    bf_filetypechk=pf['bf_filetypechk'],
                    bf_regexchk=pf['bf_regexchk'],
                    bf_expression=pf['bf_expression'],
                    bf_filebackchk=pf['bf_filebackchk'],
                    bf_size=pf['bf_size'],
                    bf_volumechk=pf['bf_volumechk'],
                    bf_datebackchk=pf['bf_datebackchk'],
                    bf_dateback=pf['bf_dateback'],
                    bf_div=pf['bf_div'],
                    bf_policyid=policy_id
                )
                policyfolder_insert.save()
                msg = '정책이 수정 되었습니다.'
            else:
                if len(file_delete) is not 0:
                    for fd in file_delete:
                        try:
                            gfile_delete = BoxPolicyfiles.objects.get(bf_id=fd)
                            gfile_delete.delete()
                        except BoxPolicyfiles.DoesNotExist:
                            pass
                else:
                    policyfile_update = BoxPolicyfiles.objects.get(bf_id=bf_id)
                    policyfile_update.bf_folderpath = pf['bf_folderpath']
                    policyfile_update.bf_extensionchk = pf['bf_extensionchk']
                    policyfile_update.bf_filetypechk = pf['bf_filetypechk']
                    policyfile_update.bf_regexchk = pf['bf_regexchk']
                    policyfile_update.bf_expression = pf['bf_expression']
                    policyfile_update.bf_filebackchk = pf['bf_filebackchk']
                    policyfile_update.bf_size = pf['bf_size']
                    policyfile_update.bf_volumechk = pf['bf_volumechk']
                    policyfile_update.bf_datebackchk = pf['bf_datebackchk']
                    policyfile_update.bf_dateback = pf['bf_dateback']
                    policyfile_update.bf_policyid = pf['bf_policyid']
                    policyfile_update.bf_div = pf['bf_div']
                    policyfile_update.save()
                msg = '정책이 수정 되었습니다.'
    except (ValueError, IndexError) as ex:
        pass
    except BoxPolicyfiles.DoesNotExist:
        pass

    try:
        Policy_update = Policy.objects.get(bp_id=policy_id)
        Policy_update.bp_modifydate = timezone.now()
        Policy_update.save()
    except Policy.DoesNotExist:
        pass

    msg = '정책이 수정 되었습니다.'

    data = {
        'result': msg,
    }

    response = JsonResponse(data)

    return response


# OCR 파일수정##
@api_view(['GET', 'PUT', 'DELETE'])
def policy_editocrfile(request):
    # global policyfile
    jtopy = json.dumps(request.data)
    json_data = json.loads(jtopy)
    policy_id = request.data.get('id')
    policyfile = json_data['ocrfiles']

    file_delete = []
    raw_id = []
    file_id = []
    print("policyfilesssssss=============================", policyfile)
    try:
        file_list = BoxPolicyfiles.objects.filter(bf_policyid=policy_id, bf_div=1, bf_type='O')

        for raw in policyfile:
            raw_id.append(raw['bf_id'])

        for fl in file_list:
            file_id.append(fl.bf_id)

        for raw in file_id:
            if raw not in raw_id:
                file_delete.append(raw)

        print("file_deletesssssss=============================", file_delete)

        for pf in policyfile:
            bf_id = pf['bf_id']
            if bf_id == '':
                bf_id = None

            if bf_id == None:
                print("insertsssssss=============================", pf)
                policyfile_insert = BoxPolicyfiles(
                    bf_type=pf['bf_type'],
                    bf_filepath=pf['bf_filepath'],
                    bf_folderpath=pf['bf_type'],
                    bf_createdate=timezone.now(),
                    bf_extensionchk=pf['bf_extensionchk'],
                    bf_filetypechk=pf['bf_filetypechk'],
                    bf_regexchk=pf['bf_regexchk'],
                    bf_expression=pf['bf_expression'],
                    bf_filebackchk=pf['bf_filebackchk'],
                    bf_size=pf['bf_size'],
                    bf_volumechk=pf['bf_volumechk'],
                    bf_datebackchk=pf['bf_datebackchk'],
                    bf_dateback=pf['bf_dateback'],
                    bf_div=pf['bf_div'],
                    bf_policyid=policy_id
                )
                policyfile_insert.save()
                msg = '정책이 수정 되었습니다.'
            else:
                if len(file_delete) is not 0:
                    for fd in file_delete:
                        print("file_deletesssss=============================", fd)
                        try:
                            gfile_delete = BoxPolicyfiles.objects.get(bf_id=fd)
                            gfile_delete.delete()
                        except BoxPolicyfiles.DoesNotExist:
                            pass
                else:
                    policyfile_update = BoxPolicyfiles.objects.get(bf_id=bf_id)
                    policyfile_update.bf_filepath = pf['bf_filepath']
                    policyfile_update.save()
                msg = '정책이 수정 되었습니다.'
    except (ValueError, IndexError) as ex:
        pass
    except BoxPolicyfiles.DoesNotExist:
        pass

    try:
        Policy_update = Policy.objects.get(bp_id=policy_id)
        Policy_update.bp_modifydate = timezone.now()
        Policy_update.save()
    except Policy.DoesNotExist:
        pass

    msg = '정책이 수정 되었습니다.'

    data = {
        'result': msg,
    }

    response = JsonResponse(data)

    return response


# 정책수정##
@api_view(['GET', 'PUT', 'DELETE'])
def policy_ocrfolderedit(request):
    # global policyfile
    jtopy = json.dumps(request.data)
    json_data = json.loads(jtopy)
    policy_id = request.data.get('id')
    policyfile = json_data['ocrfolder']

    file_delete = []
    raw_id = []
    file_id = []
    # print("policy_coldfolderedit=============================", policyfile)
    try:
        file_list = BoxPolicyfiles.objects.filter(bf_policyid=policy_id, bf_div=2, bf_type='O')

        for raw in policyfile:
            raw_id.append(raw['bf_id'])

        for fl in file_list:
            file_id.append(fl.bf_id)

        for raw in file_id:
            if raw not in raw_id:
                file_delete.append(raw)

        for pf in policyfile:
            bf_id = pf['bf_id']
            if bf_id == '' or bf_id == 0:
                bf_id = None

            # print("folderedit=bf_id============================", bf_id)

            if bf_id == None:
                # print("insert=============================", pf['bf_expression'])
                policyfolder_insert = BoxPolicyfolderfiles(
                    bf_type=pf['bf_type'],
                    bf_filepath=pf['bf_filepath'],
                    bf_folderpath=pf['bf_folderpath'],
                    bf_createdate=timezone.now(),
                    bf_extensionchk=pf['bf_extensionchk'],
                    bf_filetypechk=pf['bf_filetypechk'],
                    bf_regexchk=pf['bf_regexchk'],
                    bf_expression=pf['bf_expression'],
                    bf_filebackchk=pf['bf_filebackchk'],
                    bf_size=pf['bf_size'],
                    bf_volumechk=pf['bf_volumechk'],
                    bf_datebackchk=pf['bf_datebackchk'],
                    bf_dateback=pf['bf_dateback'],
                    bf_div=pf['bf_div'],
                    bf_policyid=policy_id
                )
                policyfolder_insert.save()
                msg = '정책이 수정 되었습니다.'
            else:
                if len(file_delete) is not 0:
                    for fd in file_delete:
                        try:
                            gfile_delete = BoxPolicyfiles.objects.get(bf_id=fd)
                            gfile_delete.delete()
                        except BoxPolicyfiles.DoesNotExist:
                            pass
                else:
                    policyfile_update = BoxPolicyfiles.objects.get(bf_id=bf_id)
                    policyfile_update.bf_folderpath = pf['bf_folderpath']
                    policyfile_update.bf_extensionchk = pf['bf_extensionchk']
                    policyfile_update.bf_filetypechk = pf['bf_filetypechk']
                    policyfile_update.bf_regexchk = pf['bf_regexchk']
                    policyfile_update.bf_expression = pf['bf_expression']
                    policyfile_update.bf_filebackchk = pf['bf_filebackchk']
                    policyfile_update.bf_size = pf['bf_size']
                    policyfile_update.bf_volumechk = pf['bf_volumechk']
                    policyfile_update.bf_datebackchk = pf['bf_datebackchk']
                    policyfile_update.bf_dateback = pf['bf_dateback']
                    policyfile_update.bf_policyid = pf['bf_policyid']
                    policyfile_update.bf_div = pf['bf_div']
                    policyfile_update.save()
                msg = '정책이 수정 되었습니다.'
    except (ValueError, IndexError) as ex:
        pass
    except BoxPolicyfiles.DoesNotExist:
        pass

    try:
        Policy_update = Policy.objects.get(bp_id=policy_id)
        Policy_update.bp_modifydate = timezone.now()
        Policy_update.save()
    except Policy.DoesNotExist:
        pass

    msg = '정책이 수정 되었습니다.'

    data = {
        'result': msg,
    }

    response = JsonResponse(data)

    return response


# 확장자수정##
@api_view(['GET', 'PUT', 'DELETE'])
def policy_extension(request):
    jtopy = json.dumps(request.data)
    json_data = json.loads(jtopy)
    policydata = json_data['policyextension']

    print("BoxPolicyextension=============================", policydata)
    print("pd['ex_id']=============================", policydata['ex_id'])

    for pd in policydata:
        policydata_update = BoxPolicyextension.objects.get(ex_id=policydata['ex_id'])
        policydata_update.ex_shadowcopy = policydata['shadowcopy']
        policydata_update.ex_blocklevel = policydata['blocklevel']
        policydata_update.ex_ebook = policydata['ebook']
        policydata_update.ex_office = policydata['office']
        policydata_update.ex_account = policydata['account']
        policydata_update.ex_exclusion = policydata['exclusion']
        policydata_update.ex_policyid = policydata['policyid']
        policydata_update.save()

    try:
        Policy_update = Policy.objects.get(bp_id=policydata['policyid'])
        Policy_update.bp_modifydate = timezone.now()
        Policy_update.save()
    except Policy.DoesNotExist:
        pass

    msg = '정책이 수정 되었습니다.'

    data = {
        'result': msg,
    }

    response = JsonResponse(data)

    return response


# OCR 파일수정##
@api_view(['GET', 'PUT', 'DELETE'])
def policy_extensionfolder(request):
    # global policyfile
    jtopy = json.dumps(request.data)
    json_data = json.loads(jtopy)
    policy_id = request.data.get('id')
    policyfile = json_data['extensionfolder']

    file_delete = []
    raw_id = []
    file_id = []
    print("policyfilesssssss=============================", policyfile)
    try:
        file_list = BoxPolicyfiles.objects.filter(bf_policyid=policy_id, bf_div=2, bf_type='E')

        for raw in policyfile:
            raw_id.append(raw['bf_id'])

        for fl in file_list:
            file_id.append(fl.bf_id)

        for raw in file_id:
            if raw not in raw_id:
                file_delete.append(raw)

        print("file_deletesssssss=============================", file_delete)

        for pf in policyfile:
            bf_id = pf['bf_id']
            if bf_id == '':
                bf_id = None

            if bf_id == None:
                print("insertsssssss=============================", pf)
                policyfile_insert = BoxPolicyfiles(
                    bf_type=pf['bf_type'],
                    bf_filepath=pf['bf_filepath'],
                    bf_folderpath=pf['bf_folderpath'],
                    bf_createdate=timezone.now(),
                    bf_extensionchk=pf['bf_extensionchk'],
                    bf_filetypechk=pf['bf_filetypechk'],
                    bf_regexchk=pf['bf_regexchk'],
                    bf_expression=pf['bf_expression'],
                    bf_filebackchk=pf['bf_filebackchk'],
                    bf_size=pf['bf_size'],
                    bf_volumechk=pf['bf_volumechk'],
                    bf_datebackchk=pf['bf_datebackchk'],
                    bf_dateback=pf['bf_dateback'],
                    bf_div=pf['bf_div'],
                    bf_policyid=policy_id
                )
                policyfile_insert.save()
                msg = '정책이 수정 되었습니다.'
            else:
                if len(file_delete) is not 0:
                    for fd in file_delete:
                        print("file_deletesssss=============================", fd)
                        try:
                            gfile_delete = BoxPolicyfiles.objects.get(bf_id=fd)
                            gfile_delete.delete()
                        except BoxPolicyfiles.DoesNotExist:
                            pass
                else:
                    policyfile_update = BoxPolicyfiles.objects.get(bf_id=bf_id)
                    policyfile_update.bf_folderpath = pf['bf_folderpath']
                    policyfile_update.save()
                msg = '정책이 수정 되었습니다.'
    except (ValueError, IndexError) as ex:
        pass
    except BoxPolicyfiles.DoesNotExist:
        pass

    try:
        Policy_update = Policy.objects.get(bp_id=policy_id)
        Policy_update.bp_modifydate = timezone.now()
        Policy_update.save()
    except Policy.DoesNotExist:
        pass

    msg = '정책이 수정 되었습니다.'

    data = {
        'result': msg,
    }

    response = JsonResponse(data)

    return response


# OCR 파일수정##
@api_view(['GET', 'PUT', 'DELETE'])
def policy_extensionfiles(request):
    # global policyfile
    jtopy = json.dumps(request.data)
    json_data = json.loads(jtopy)
    policy_id = request.data.get('id')
    policyfile = json_data['extensionfiles']

    file_delete = []
    raw_id = []
    file_id = []
    print("policyfilesssssss=============================", policyfile)
    try:
        file_list = BoxPolicyfiles.objects.filter(bf_policyid=policy_id, bf_div=1, bf_type='E')

        for raw in policyfile:
            raw_id.append(raw['bf_id'])

        for fl in file_list:
            file_id.append(fl.bf_id)

        for raw in file_id:
            if raw not in raw_id:
                file_delete.append(raw)

        print("file_deletesssssss=============================", file_delete)

        for pf in policyfile:
            bf_id = pf['bf_id']
            if bf_id == '':
                bf_id = None

            if bf_id == None:
                print("insertsssssss=============================", pf)
                policyfile_insert = BoxPolicyfiles(
                    bf_type=pf['bf_type'],
                    bf_filepath=pf['bf_filepath'],
                    bf_folderpath=pf['bf_folderpath'],
                    bf_createdate=timezone.now(),
                    bf_extensionchk=pf['bf_extensionchk'],
                    bf_filetypechk=pf['bf_filetypechk'],
                    bf_regexchk=pf['bf_regexchk'],
                    bf_expression=pf['bf_expression'],
                    bf_filebackchk=pf['bf_filebackchk'],
                    bf_size=pf['bf_size'],
                    bf_volumechk=pf['bf_volumechk'],
                    bf_datebackchk=pf['bf_datebackchk'],
                    bf_dateback=pf['bf_dateback'],
                    bf_div=pf['bf_div'],
                    bf_policyid=policy_id
                )
                policyfile_insert.save()
                msg = '정책이 수정 되었습니다.'
            else:
                if len(file_delete) is not 0:
                    for fd in file_delete:
                        print("file_deletesssss=============================", fd)
                        try:
                            gfile_delete = BoxPolicyfiles.objects.get(bf_id=fd)
                            gfile_delete.delete()
                        except BoxPolicyfiles.DoesNotExist:
                            pass
                else:
                    policyfile_update = BoxPolicyfiles.objects.get(bf_id=bf_id)
                    policyfile_update.bf_filepath = pf['bf_filepath']
                    policyfile_update.save()
                msg = '정책이 수정 되었습니다.'
    except (ValueError, IndexError) as ex:
        pass
    except BoxPolicyfiles.DoesNotExist:
        pass

    try:
        Policy_update = Policy.objects.get(bp_id=policy_id)
        Policy_update.bp_modifydate = timezone.now()
        Policy_update.save()
    except Policy.DoesNotExist:
        pass

    msg = '정책이 수정 되었습니다.'

    data = {
        'result': msg,
    }

    response = JsonResponse(data)

    return response


# 설정수정##
@api_view(['GET', 'PUT', 'DELETE'])
def policy_settings(request):
    jtopy = json.dumps(request.data)
    json_data = json.loads(jtopy)
    policydata = json_data['policysetting']

    print("policysetting=============================", policydata)
    print("pd['ex_id']=============================", policydata['id'])

    for pd in policydata:
        policydata_update = BoxPolicysetting.objects.get(ps_id=policydata['id'])
        policydata_update.ps_hidefile = policydata['hidefile']
        policydata_update.ps_battery = policydata['battery']
        policydata_update.ps_presentation = policydata['presentation']
        policydata_update.ps_policysetting = policydata['policysetting']
        policydata_update.ps_multithread = policydata['multithread']
        policydata_update.ps_lan = policydata['lan']
        policydata_update.ps_wifi = policydata['wifi']
        policydata_update.ps_lte = policydata['lte']
        policydata_update.ps_schedulediv = policydata['schedulediv']
        policydata_update.ps_stime = policydata['stime']
        policydata_update.ps_itime = policydata['itime']
        policydata_update.ps_backtime = policydata['backtime']
        policydata_update.ps_starttime = policydata['starttime']
        policydata_update.ps_endtime = policydata['endtime']
        policydata_update.ps_netdiv = policydata['netdiv']
        policydata_update.ps_upspeed = policydata['upspeed']
        policydata_update.ps_banddiv = policydata['banddiv']
        policydata_update.ps_bandstarttime = policydata['bandstarttime']
        policydata_update.ps_bandendtime = policydata['bandendtime']
        policydata_update.ps_policyid = policydata['policyid']
        policydata_update.ps_endtimechk = policydata['endtimechk']
        policydata_update.ps_weekday = policydata['weekday']
        policydata_update.save()

    try:
        Policy_update = Policy.objects.get(bp_id=policydata['policyid'])
        Policy_update.bp_modifydate = timezone.now()
        Policy_update.save()
    except Policy.DoesNotExist:
        pass

    msg = '정책이 수정 되었습니다.'

    data = {
        'result': msg,
    }

    response = JsonResponse(data)

    return response


##권한수정##
@api_view(['GET', 'PUT', 'DELETE'])
def policy_permission(request):
    jtopy = json.dumps(request.data)
    json_data = json.loads(jtopy)
    policydata = json_data['policypermission']

    for pd in policydata:
        policydata_update = BoxPolicypermission.objects.get(pp_id=policydata['id'])
        policydata_update.pp_deletechk = policydata['deletechk']
        policydata_update.pp_sharingchk = policydata['sharingchk']
        policydata_update.pp_editchk = policydata['editchk']
        policydata_update.pp_pwchk = policydata['pwchk']
        policydata_update.pp_changechk = policydata['changechk']
        policydata_update.pp_clientdiv = policydata['clientdiv']
        policydata_update.pp_pluspw = policydata['pluspw']
        policydata_update.pp_backupchk = policydata['backupchk']
        policydata_update.pp_pausechk = policydata['pausechk']
        policydata_update.pp_terminate = policydata['terminate']
        policydata_update.pp_remove = policydata['remove']
        policydata_update.pp_policyid = policydata['policyid']
        policydata_update.save()

    try:
        Policy_update = Policy.objects.get(bp_id=policydata['policyid'])
        Policy_update.bp_modifydate = timezone.now()
        Policy_update.save()
    except Policy.DoesNotExist:
        pass

    msg = '정책이 수정 되었습니다.'

    data = {
        'result': msg,
    }

    response = JsonResponse(data)

    return response


@api_view(['GET', 'PUT', 'DELETE'])
def policy_delete(request, pk):
    """
    Retrieve, update or delete a product instance.
    """
    print("pk=============================", pk)
    global policyfiledelete
    global policydatadelete
    global policyextensiondelete
    global policysettingdelete
    global policypermissiondelete

    try:
        policyfiledelete = BoxPolicyfiles.objects.filter(bf_policyid=pk)
    except policyfiledelete.DoesNotExist:
        pass

    try:
        policydatadelete = BoxPolicydata.objects.filter(pd_policyid=pk)
    except policydatadelete.DoesNotExist:
        pass

    try:
        policyextensiondelete = BoxPolicyextension.objects.get(ex_policyid=pk)
    except policyextensiondelete.DoesNotExist:
        pass

    try:
        policysettingdelete = BoxPolicysetting.objects.get(ps_policyid=pk)
    except policysettingdelete.DoesNotExist:
        pass

    try:
        policypermissiondelete = BoxPolicypermission.objects.get(pp_policyid=pk)
    except policypermissiondelete.DoesNotExist:
        pass

    try:
        policy = Policy.objects.get(pk=pk)
    except policy.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = policyEditListSerializer(policy, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = policyEditListSerializer(policy, partial=True, data=request.data,
                                              context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        policyfiledelete.delete()
        policydatadelete.delete()
        # policyextensiondelete.delete()
        # policysettingdelete.delete()
        # policypermissiondelete.delete()
        policy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
