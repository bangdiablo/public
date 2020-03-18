# from common.type.admin_code import AdminCode
from common.type.exception import Code
from common.utils.validate_data_utils import *
# import boto3
# from conf import settings
import logging
import traceback

logger = logging.getLogger(__name__)


def response_model(data=dict):
    if data['result'] is True:
        if not 'code' in data.keys() or num_is_empty(data['code']):
            data['code'] = Code.SUCCESS.value
            data['message'] = Code.SUCCESS.name
        else:
            data['message'] = Code.get_value(data['code']).name
    else:
        if not 'code' in data.keys() or num_is_empty(data['code']):
            data['code'] = Code.INTERNAL_SERVER_ERROR.value
            data['message'] = Code.INTERNAL_SERVER_ERROR.name
        else:
            data['message'] = Code.get_value(data['code']).name

    return data


def has_exception(proc_result=object, exception=Exception):
    traceback.print_exc()
    logger.error(str(exception))
    proc_result['exception_message'] = str(exception)
    proc_result['result'] = False

    for key in proc_result.keys():
        if key == 'l_error_code':
            proc_result['l_code'] = str_default_if_empty(proc_result['l_error_code'], '')
            break


def get_client_ip(request):
    # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    #
    # if x_forwarded_for:
    #     ip = x_forwarded_for.split(',')[0]
    # else:
    ip = request.META.get('REMOTE_ADDR')

    return ip


# def del_s3_files(del_files=[]):
#     s3 = boto3.client('s3')
#
#     per_page_num = 500
#     total_page = int(len(del_files) / 500)
#
#     if len(del_files) % per_page_num:
#         total_page += 1
#
#     if len(del_files) <= per_page_num:
#         s3.delete_objects(
#             Bucket=settings.S3_BUCKET_NAME,
#             Delete={
#                 'Objects': del_files
#             }
#         )
#     else:
#         current_page = 0
#
#         for num in range(0, total_page):
#             current_page += 1
#             page_value = (current_page - 1) * per_page_num
#             per_page_num_value = current_page * per_page_num
#
#             del_rows = del_files[page_value:per_page_num_value]
#
#             s3.delete_objects(
#                 Bucket=settings.S3_BUCKET_NAME,
#                 Delete={
#                     'Objects': del_rows
#                 }
#             )
