# import xlwt
import math

# from django.utils import timezone
# from django.http.response import HttpResponse

from user.main.models import BoxUsers
# from dataRoom.models import RoomHistory, Room
# from common.type.fieldType import Status, AdminType, Language, AdminLinkType
# from common.type.admin_log import SiteAdminHistoryCode, EnvRoomAdminHistoryCode
# from common.utils.validate_data_utils import *
# from dateutil.parser import parse


# def reg_admin_history(admin_type=AdminType, eid=None, rid=None, actor_email='', model={}):
#     if str_is_empty(model['l_code']):
#         return
#
#     l_desc = ''
#
#     for key in model.keys():
#         if key == 'l_desc':
#             l_desc = str_default_if_empty(model['l_desc'], '')
#             break
#
#     if admin_type == AdminType.SITE:
#         code = 'SA_' + model['l_code']
#         reg_site_history(1, SiteAdminHistoryCode[code], actor_email, l_desc)
#     elif admin_type == AdminType.ENV:
#         code = 'EA_' + model['l_code']
#         reg_env_room_history(env_id=eid, room_id=rid, code=EnvRoomAdminHistoryCode[code], email=actor_email, l_desc=l_desc)
#     elif admin_type == AdminType.ENV_ROOM:
#         code = 'MA_' + model['l_code']
#         reg_env_room_history(env_id=eid, room_id=rid, code=EnvRoomAdminHistoryCode[code], email=actor_email, l_desc=l_desc)
#     else:
#         code = 'RA_' + model['l_code']
#         reg_env_room_history(env_id=eid, room_id=rid, code=EnvRoomAdminHistoryCode[code], email=actor_email, l_desc=l_desc)


# def reg_login_admin_history(admin=Admin, code='', content=''):
#     if admin['admin_type'] == AdminType.SITE.name:
#         code = 'SA_' + code
#
#         reg_site_history(1, SiteAdminHistoryCode[code], admin['email'], content)
#     elif admin['admin_type'] == AdminType.ENV.name:
#         code = 'EA_' + code
#
#         reg_env_room_history(env_id=admin['env_id'], code=EnvRoomAdminHistoryCode[code], email=admin['email'], l_desc=content)
#
#     elif admin['admin_type'] == AdminType.ENV_ROOM.name:
#         code = 'MA_' + code
#
#         reg_env_room_history(env_id=admin['env_id'], code=EnvRoomAdminHistoryCode[code], email=admin['email'], l_desc=content)
#     else:
#         code = 'RA_' + code
#         reg_env_room_history(env_id=admin['env_id'], code=EnvRoomAdminHistoryCode[code], email=admin['email'], l_desc=content)


# def reg_site_history(site_id, code, email, content=''):
#     result = False
#
#     try:
#         site_history = SiteHistory()
#         site_history.site_id = str(site_id)
#         site_history.created_date = timezone.now()
#         site_history.log_type = code.name
#         site_history.contents = content
#         site_history.email = email
#         site_history.save()
#
#         result = True
#     except Exception as exception:
#         print(exception)
#
#     return result


# def reg_env_room_history(env_id=None, room_id=None, code=EnvRoomAdminHistoryCode, email='', l_desc=''):
#     result = False
#
#     try:
#         room_history = RoomHistory()
#
#         if num_is_not_empty(env_id):
#             room_history.env_id_id =  env_id
#
#         if num_is_not_empty(room_id):
#             room_history.room_id_id = room_id
#             try:
#                 room_model = Room.objects.get(pk=room_id)
#                 room_history.env_id_id = room_model.env_id_id
#             except Exception as ex:
#                 print(ex)
#
#         room_history.created_date = timezone.now()
#         room_history.history_type = code.name
#         room_history.contents = l_desc
#         room_history.email = email
#         room_history.save()
#
#         result = True
#     except Exception as exception:
#         print(exception)
#
#     return result


# def export_excel(lang_type="kr", columns=[], rows=[], file_name="default.xlsx", is_sys_log=bool):
#     response = HttpResponse(content_type='application/ms-excel')
#     response['Content-Disposition'] = 'attachment; filename="' + file_name + '"'
#
#     wb = xlwt.Workbook(encoding='utf-8')
#
#     ws = wb.add_sheet("sheet1")
#     font_style = xlwt.XFStyle()
#     font_style.font.bold = True
#
#     row_num = 0
#
#     col_styles = xlwt.easyxf("font: bold on; align: horiz center, vert center; pattern: pattern solid_fill, fore_color gray25;")
#
#     for col_num in range(len(columns)):
#         ws.col(col_num).width = columns[col_num]['width']
#         ws.write(
#             row_num, col_num, columns[col_num][lang_type],
#             col_styles
#         )
#
#     row_style = xlwt.easyxf("align: horiz left, vert center, shri true")
#
#     for idx, row in enumerate(rows):
#         row_num = row_num + 1
#
#         for index, col in enumerate(columns):
#             ws.col(index).alignment = 'left'
#
#             if col['field'].find('date') > -1:
#                 if str_is_not_empty(row[col['field']]):
#                     dt = parse(row[col['field']])
#
#                     row[col['field']] = dt.strftime("%Y-%m-%d %H:%M:%S")
#                 else:
#                     row[col['field']] = ' '
#             elif is_sys_log is True and col['field'].find('status') > -1:
#                 row[col['field']] = convert_status_type(row[col['field']], lang_type)
#             elif is_sys_log is True and col['field'].find('process_type') > -1:
#                 row[col['field']] = convert_process_type(row[col['field']], lang_type)
#
#             ws.write(row_num, index, row[col['field']], row_style)
#
#     wb.save(response)
#
#     return response


# def replace_admin_type(lang_type='', value=str):
#     if value.find('{SITE}') > -1:
#         if lang_type == 'KR':
#             return value.replace('{SITE}', '마스터 관리자')
#         elif lang_type == 'JP':
#             return value.replace('{SITE}', 'サイト管理者')
#         else:
#             return value.replace('{SITE}', 'Site administrator')
#     elif value.find('{ENV}') > -1:
#         if lang_type == 'KR':
#             return value.replace('{ENV}', '스페이스 관리자')
#         elif lang_type == 'JP':
#             return value.replace('{ENV}', 'スペース管理者')
#         else:
#             return value.replace('{ENV}', 'Space administrator')
#     elif value.find('{ROOM}') > - 1:
#         if lang_type == 'KR':
#             return value.replace('{ROOM}', '룸 관리자')
#         elif lang_type == 'JP':
#             return value.replace('{ROOM}', 'ルーム管理者')
#         else:
#             return value.replace('{ROOM}', 'Room administrator')
#     else:
#         if lang_type == 'KR':
#             return value.replace('{ENV_ROOM}', '스페이스&룸 관리자')
#         elif lang_type == 'JP':
#             return value.replace('{ENV_ROOM}', 'スペース＆ルーム管理者')
#         else:
#             return value.replace('{ENV_ROOM}', 'Space&Room administrator')
#
#
# def convert_file_size(size_bytes):
#     if size_bytes == 0:
#         return "0B"
#     size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
#     i = int(math.floor(math.log(size_bytes, 1024)))
#     power = math.pow(1024, i)
#     size = round(size_bytes / power, 2)
#
#     return "{} {}".format(size, size_name[i])
#
#
# def convert_status_type(value, lang_type):
#     if value == 'COMPLETE':
#         if lang_type == 'KR':
#             result = '완료'
#         elif lang_type == 'JP':
#             result = '完了'
#         else:
#             result = 'COMPLETE'
#     elif value == 'PROCESS':
#         if lang_type == 'KR':
#             result = '진행'
#         elif lang_type == 'JP':
#             result = '進行'
#         else:
#             result = 'PROCESS'
#     else:
#         if lang_type == 'KR':
#             result = '실패'
#         elif lang_type == 'JP':
#             result = '失敗'
#         else:
#             result = 'FAIL'
#
#     return result
#
#
# def convert_process_type(value, lang_type):
#     result = ''
#
#     if value == 'CONVERT_FILE':
#         if lang_type == 'KR':
#             result = '문서변환'
#         elif lang_type == 'JP':
#             result = '文書変換'
#         else:
#             result = 'Convert document'
#     elif value == 'OCR':
#         if lang_type == 'KR':
#             result = 'OCR'
#         elif lang_type == 'JP':
#             result = 'OCR'
#         else:
#             result = 'OCR'
#     elif value == 'S3_FILE_DOWNLOAD':
#         if lang_type == 'KR':
#             result = '다운로드'
#         elif lang_type == 'JP':
#             result = 'ダウンロード'
#         else:
#             result = 'Download'
#     elif value == 'SYSTEM':
#         if lang_type == 'KR':
#             result = '시스템'
#         elif lang_type == 'JP':
#             result = 'システム'
#         else:
#             result = 'System'
#     else:
#         if lang_type == 'KR':
#             result = '추출'
#         elif lang_type == 'JP':
#             result = '抽出'
#         else:
#             result = 'Extract'
#     return result


def get_request_params(request):
    params = '%s %s [' % (request.method, request.path)
    index = 0

    if len(request.data) > 0:
        for key, value in request.data.items():
            if index > 0:
                params += ', '

            params += '%s: %s' % (key, value)
            index += 1

    params += ']'

    return params
