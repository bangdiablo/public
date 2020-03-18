import json
from datetime import datetime
import re

from dateutil.relativedelta import relativedelta
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import Q, F, Subquery, OuterRef, Count, Sum
from django.template.loader import get_template
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template
from django.utils import timezone
from django.utils.safestring import mark_safe

from common.utils.AESCipher import AESCipher
from urllib import parse

# from common.utils.admin_mail_utils import *
from common.utils.admin_utils import *
from common.type.fieldType import *
from conf import settings
from user.main.models import BoxUsers


class MailService:

    # @classmethod
    # def send_admin_mail(cls, params, payload):
    #     proc_result = {
    #         'result': True,
    #         'l_code': None,
    #         'exception_message': None,
    #     }
    #
    #     admin_email = payload['email']
    #     emails = params.get('emails')
    #     title = params.get('title')
    #     description = params.get('description')
    #
    #     email_sender = None
    #
    #     try:
    #         adm = Admin.objects.get(email=admin_email)
    #
    #         if adm.site_id is not None and adm.site_id.email_sender is not None:
    #             email_sender = adm.site_id.email_sender
    #
    #         if str_is_empty(email_sender) :
    #             site = Site.objects.filter(pk=1)[:1]
    #             data = SiteSerializer(site, many=True).data[0]
    #             email_sender = data['email_sender']
    #
    #         email_split = emails.split(",")
    #         email_message = EmailMultiAlternatives(title, description, email_sender, to=[email_split[0]])
    #         email_message.send()
    #         proc_result['result'] = True
    #     except Exception as exception:
    #         has_exception(proc_result=proc_result, exception=exception)
    #
    #     return proc_result

    @classmethod
    @transaction.atomic
    def send_email_reset_password(cls, request):
        proc_result = {
            'result': True,
            'l_code': None,
            'not_exist_email': False,
            'exception_message': None,
        }

        email = request.data['email']
        lang_type = request.data['langType']

        language = lang_type.lower()
        translation.activate(language)

        sid = transaction.savepoint()

        try:
            # check existed Email
            check = BoxUsers.objects.filter(bu_email=email).count()

            if check < 1:
                proc_result['not_exist_email'] = True
                proc_result['result'] = False

                return proc_result

            user = BoxUsers.objects.get(bu_email=email)


            # save the history of Email send
            query = {
                'email': email,
                'langType': lang_type
            }

            json_str = json.dumps(query)

            # TODO : 이메일 발송 내역 테이블 만들어서 model 등록 후, 이용
            # box_email_link = BoxEmailLink()
            #
            # if user.site_id is not None:
            #     box_email_link.site_id = user.site_id.id
            #
            # if user.env_id is not None:
            #     box_email_link.env_id = user.env_id.id
            #
            # box_email_link.admin_id = user.id
            # box_email_link.link_type = AdminLinkType.PW_RESET
            # box_email_link.link = json_str
            # box_email_link.created_date = timezone.now()
            # box_email_link.expired_date = timezone.now()
            #
            # box_email_link.save()

            if 'reseller' in request.path:
                server_url = settings.RESELLER_MAIL_TEMPLATE_SERVER_URL
            elif 'box' in request.path:
                server_url = settings.MAIL_TEMPLATE_SERVER_URL

            # set Email template
            template_file_name = 'ChangePasswordTemplate_' + lang_type + '.html'
            header_image_url = server_url + '/statics'

            # make a key
            cipher = AESCipher(key='AOS_BOX_EMAIL_KEY')
            key = (datetime.now() + relativedelta(days=1)).strftime('%Y%m%d%H%M%S')  # 하루 동안 유효
            key += "/" + email  # key의 최종 형태. ex) 20200101175231/test@legal.com
            link_id = cipher.encrypt(raw=key)
            link_id = link_id.decode('utf-8')
            link_id = parse.quote(link_id)

            link_url = server_url + '/before_login/resetPasswordForm?k=' + str(link_id)

            html_template = get_template(template_file_name).render(
                {'serverUrl': server_url, 'headerImageUrl': header_image_url, 'email': email, 'linkUrl': link_url}
            )

            # send Email
            email_message = EmailMultiAlternatives(_('reset_password_title'), '', to=[email])
            email_message.attach_alternative(html_template, "text/html")
            email_message.send()

            proc_result['result'] = True

        except Exception as exception:
            has_exception(proc_result=proc_result, exception=exception)
            transaction.savepoint_rollback(sid)

        finally:
            return proc_result

        return proc_result


    @classmethod
    @transaction.atomic
    def send_email_join(cls, params):

        proc_result = {}

        email_list = params.get('emailList')
        subject = params.get('subject')
        message = params.get('message')
        template_title = '이메일 가입'

        sid = transaction.savepoint()

        try:
            # save the history of Email send
            query = params

            json_str = json.dumps(query)

            # TODO : 이메일 발송 내역 테이블 만들어서 model 등록 후, 이용
            # box_email_link = BoxEmailLink()
            #
            # if user.site_id is not None:
            #     box_email_link.site_id = user.site_id.id
            #
            # if user.env_id is not None:
            #     box_email_link.env_id = user.env_id.id
            #
            # box_email_link.admin_id = user.id
            # box_email_link.link_type = AdminLinkType.PW_RESET
            # box_email_link.link = json_str
            # box_email_link.created_date = timezone.now()
            # box_email_link.expired_date = timezone.now()
            #
            # box_email_link.save()

            # set email template
            template_file_name = 'MemberJoinTemplate.html'
            header_image_url = settings.MAIL_TEMPLATE_SERVER_URL + '/statics'

            # make a key
            cipher = AESCipher(key='AOS_BOX_EMAIL_KEY')
            key = (datetime.now() + relativedelta(months=1)).strftime('%Y%m%d') # 한달 뒤 날짜까지 유효
            link_id = cipher.encrypt(raw=key)
            link_id = link_id.decode('utf-8')
            link_id = parse.quote(link_id)

            link_url = settings.MAIL_TEMPLATE_SERVER_URL + '/before_login/memberJoinForm?k=' + str(link_id)
            server_url = settings.MAIL_TEMPLATE_SERVER_URL

            html_template = get_template(template_file_name).render(
                {'serverUrl': server_url, 'templateTitle': template_title, 'message': message, 'linkUrl': link_url}
            )

            # send email
            email_message = EmailMultiAlternatives(subject, '', to=email_list)
            email_message.attach_alternative(html_template, "text/html")
            email_message.send()

            proc_result['result'] = True

        except Exception as exception:
            proc_result['result'] = False
            has_exception(proc_result=proc_result, exception=exception)
            transaction.savepoint_rollback(sid)

        return proc_result

    # @classmethod
    # @transaction.atomic
    # def resend_email_invite_admin(cls, params):
    #     proc_result = {
    #         'result': True,
    #         'l_code': None,
    #         'exception_message': None,
    #         'urls' : []
    #     }
    #
    #     email = params.get('email')
    #     r_id = params.get('rid')
    #
    #     link_url_array = []
    #
    #     sid = transaction.savepoint()
    #
    #     try:
    #         site = Site.objects.get(pk=1)
    #         email_sender = site.email_sender
    #
    #         admin = Admin.objects.get(email=email)
    #
    #         is_joined = True
    #
    #         if str_is_empty(admin.password):
    #             is_joined = False
    #
    #         ids = {
    #             'sid': 1,
    #             'eid': admin.env_id_id,
    #             'rid': r_id
    #         }
    #
    #         query = {
    #             'IT': str(timezone.now()),
    #             'AT': admin.admin_type.name,
    #             'LT': admin.language.name,
    #         }
    #
    #         if admin.admin_type == AdminType.SITE:
    #             name = ''
    #         elif admin.admin_type == AdminType.ENV or admin.admin_type == AdminType.ENV_ROOM:
    #             env = Env.objects.get(pk=admin.env_id_id)
    #             name = env.name
    #         else:
    #             if num_is_not_empty(r_id):
    #                 dup_env_room_adm_count = RoomAdmin.objects.filter(admin_id=admin.id, room_id=r_id).count()
    #
    #                 room = Room.objects.get(pk=r_id)
    #                 env = Env.objects.get(pk=room.env_id_id)
    #                 name = env.name + '>' + room.name
    #             else:
    #                 env = Env.objects.get(pk=admin.env_id_id)
    #                 name = env.name
    #
    #         json_str = json.dumps(query)
    #
    #         link_key = cls.create_invite_email_link(admin.admin_type.name, ids, admin.id, json_str)
    #         html_template = cls.create_template(is_joined, admin.language.name, name, link_key, link_url_array, 0, admin.admin_type.name)
    #
    #         email_message = EmailMultiAlternatives(invite_title(admin.language.name), '', email_sender, to=[email])
    #         email_message.attach_alternative(html_template, "text/html")
    #         email_message.send()
    #
    #         proc_result['result'] = True
    #         proc_result['urls'] = link_url_array
    #     except Exception as exception:
    #         has_exception(proc_result=proc_result, exception=exception)
    #         transaction.savepoint_rollback(sid)
    #     finally:
    #         return proc_result
    #
    #     return proc_result
    #
    # @classmethod
    # def send_email_inquiry(cls, params, payload):
    #     proc_result = {
    #         'result': True,
    #         'l_code': None,
    #         'exception_message': None,
    #     }
    #
    #     email = payload['email']
    #     env_id = payload['eid']
    #     url = params.get('url')
    #     title = params.get('title')
    #     description = params.get('description')
    #     lang_type = params.get('langType')
    #
    #     try:
    #         site = Site.objects.get(pk=1)
    #         email_sender = site.email_sender
    #         email_ask = site.email_ask
    #
    #         if num_is_not_empty(env_id):
    #             space_name = Env.objects.get(id=env_id).name
    #         else:
    #             space_name = ''
    #
    #         template_file_name = 'admin/InquiryMailTemplate_' + lang_type + '.html'
    #
    #         header_image_url = settings.MAIL_TEMPLATE_SERVER_URL + '/statics'
    #
    #         html_template = get_template(template_file_name).render(
    #             {'headerImageUrl': header_image_url, 'email': email, 'url': url, 'title': title, 'description': mark_safe(description), 'spaceName': space_name}
    #         )
    #
    #         email_message = EmailMultiAlternatives(inquiry_title(lang_type, email, title), '', email_sender, to=[email_ask])
    #         email_message.attach_alternative(html_template, "text/html")
    #         email_message.send()
    #     except Exception as exception:
    #         has_exception(proc_result=proc_result, exception=exception)
    #
    #     return proc_result
    #
    # @classmethod
    # def import_admin(cls, params, files):
    #     proc_result = {
    #         'result': True,
    #         'l_code': None,
    #         'exception_message': None,
    #         'acceptEmails': None,
    #         'invalidEmails' : None
    #     }
    #
    #     try:
    #         admin_type = params.get('adminType')
    #
    #         if admin_type == 'SITE':
    #             site_id = 1
    #         elif admin_type == 'ENV':
    #             env_id = params.get('key')
    #         else:
    #             room_id = params.get('key')
    #
    #         accept_emails = []
    #         invalid_emails = []
    #         valid_admin_emails = []
    #
    #         if files and files['file'].size > 0:
    #             for index, row in enumerate(files['file'].readlines()):
    #                 if index == 0: continue
    #
    #                 email = row.decode().splitlines()[0]
    #
    #                 if re.match('^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$', email) is None:
    #                     invalid_emails.append(email)
    #                     continue
    #
    #                 obj = {
    #                     'email': email,
    #                     'sid': None,
    #                     'eid': None,
    #                     'rid_row': None,
    #                     'admin_type': None,
    #                 }
    #
    #                 try:
    #                     adm = Admin.objects.get(email=email)
    #                     admin_data = AdminSerializer(adm).data
    #
    #                     obj['sid'] = admin_data['site_id']
    #                     obj['eid'] = admin_data['env_id']
    #                     obj['admin_type'] = admin_data['admin_type']
    #
    #                     if admin_type == 'ROOM' or admin_type == 'ENV' or admin_type == 'ENV_ROOM':
    #                         room_admin = RoomAdmin.objects.extra(
    #                             select={
    #                                 'e_id': 'SELECT (R0.env_id) AS e_id FROM Room R0 WHERE R0.id = RoomAdmin.room_id'
    #                             }
    #                         ).filter(admin_id=adm.id)
    #
    #                         room_admin_rows = RoomAdminSerializer(room_admin, many=True).data
    #
    #                         if room_admin_rows is not None and len(room_admin_rows) > 0:
    #                             obj['rid_row'] = room_admin_rows
    #
    #                     accept_emails.append(obj)
    #                 except Admin.DoesNotExist or Room.DoesNotExist:
    #                     accept_emails.append(obj)
    #         else:
    #             proc_result['result'] = False
    #             proc_result['code'] = AdminCode.EMPTY_FILE.value
    #             proc_result['message'] = AdminCode.EMPTY_FILE.name
    #
    #             return proc_result
    #
    #         proc_result['invalidEmails'] = invalid_emails
    #         proc_result['acceptEmails'] = accept_emails
    #         proc_result['result'] = True
    #     except Exception as exception:
    #         has_exception(proc_result=proc_result, exception=exception)
    #
    #     return proc_result
    #
    # @classmethod
    # @transaction.atomic
    # def send_email_invite_admin2(cls, params):
    #     proc_result = {
    #         'result': True,
    #         'l_code': None,
    #         'exception_message': None,
    #         'urls' : []
    #     }
    #
    #     emails = params.get('emails')
    #     lang_type = params.get('langType')
    #     admin_type = params.get('type')
    #
    #     ids = {
    #         'sid': num_default_if_empty(params.get('sid'), 1),
    #         'eid': params.get('eid'),
    #         'rid': params.get('rid')
    #     }
    #
    #     proc_result['l_code'] = '1001_01'
    #     proc_result['l_desc'] = '{' + admin_type + '} -> ' + emails
    #
    #     sid = transaction.savepoint()
    #
    #     try:
    #         site = Site.objects.get(pk=ids['sid'])
    #         email_sender = site.email_sender
    #
    #         error_mail = ''
    #
    #         if emails is not None and emails != "":
    #             email_split = emails.split(",")
    #             link_url_array = []
    #
    #             for index, row in enumerate(email_split):
    #                 query = {
    #                     'IT': str(timezone.now()),
    #                     'AT': admin_type,
    #                     'LT': lang_type,
    #                 }
    #
    #                 error_mail = row
    #                 dup_check = Admin.objects.filter(email=row).count()
    #
    #                 is_joined = False
    #
    #                 if dup_check == 0:
    #                     is_joined = False
    #                     admin = Admin()
    #                     admin.status_type = Status.INVITATION
    #
    #                     lang_type_value = Language.get_value(lang_type)
    #
    #                     admin.email = row
    #                     admin.language = lang_type_value
    #                     admin.created_date = timezone.now()
    #                     admin.admin_type = AdminType.get_value(admin_type)
    #                     admin.save()
    #                 else:
    #                     is_joined = True
    #
    #                     admin = Admin.objects.get(email=row)
    #
    #                     if str_is_empty(admin.password):
    #                         is_joined = False
    #
    #                     if lang_type is None or lang_type == "":
    #                         lang_type_value = admin.language.value
    #                     else:
    #                         lang_type_value = Language.get_value(lang_type)
    #
    #                 name = ''
    #
    #                 if admin_type == 'SITE':
    #                     admin.site_id = site
    #                     admin.admin_type = AdminType.get_value(admin_type)
    #                     admin.save()
    #                 elif admin_type == 'ENV':
    #
    #                     env = Env.objects.get(pk=ids['eid'])
    #                     name = env.name
    #                     admin.env_id_id = env.id
    #
    #                     dup_env_room_adm_count = RoomAdmin.objects.filter(admin_id=admin.id).count()
    #
    #                     # 환경 관리자로 설정되어 있으나 이미 룸에 소속되어 있는 경우, 겸임 관리자로 재설정하도록 한다.
    #                     if dup_env_room_adm_count > 0:
    #                         admin.admin_type = AdminType.ENV_ROOM
    #                         query['AT'] = AdminType.ENV_ROOM.name
    #                     else:
    #                         admin.admin_type = AdminType.ENV
    #
    #                     admin.save()
    #                 elif admin_type == 'ENV_ROOM':
    #                     env = Env.objects.get(pk=ids['eid'])
    #                     name = env.name
    #                     admin.env_id_id = env.id
    #
    #                     admin.admin_type = AdminType.ENV_ROOM
    #
    #                     admin.save()
    #
    #                     if num_is_not_empty(ids['rid']):
    #                         room = Room.objects.get(pk=ids['rid'])
    #                         dup_room_adm_count = RoomAdmin.objects.filter(room_id=ids['rid'], admin_id=admin.id).count()
    #
    #                         if dup_room_adm_count < 1:
    #                             room_admin = RoomAdmin()
    #                             room_admin.room_id = room
    #                             room_admin.admin_id = admin
    #                             room_admin.created_date = timezone.now()
    #                             room_admin.save()
    #                 else:       #룸 관리자일 경우
    #                     #전달받은 룸이 등록되어 있지 않은 경우 새로 등록함.
    #
    #                     if num_is_not_empty(ids['rid']):
    #                         room = Room.objects.get(pk=ids['rid'])
    #                         dup_room_adm_count = RoomAdmin.objects.filter(room_id=ids['rid'], admin_id=admin.id).count()
    #
    #                         if dup_room_adm_count < 1:
    #                             room_admin = RoomAdmin()
    #                             room_admin.room_id_id = room.id
    #                             room_admin.admin_id_id = admin.id
    #                             room_admin.created_date = timezone.now()
    #                             room_admin.save()
    #                         else:
    #                             env = Env.objects.get(pk=room.env_id_id)
    #                             name = env.name + '>' + room.name
    #                         # 이미 등록되어 있는 경우에는 건너뛴다.
    #
    #                         if num_is_not_empty(admin.env_id_id) and num_is_not_empty(ids['rid']):
    #                             admin.admin_type = AdminType.ENV_ROOM
    #                         else:
    #                             admin.admin_type = AdminType.ROOM
    #                             admin.env_id_id = room.env_id_id
    #
    #                         admin.save()
    #                     else:
    #                         admin.env_id_id = ids['eid']
    #                         env = Env.objects.get(pk=ids['eid'])
    #                         name = env.name
    #                         admin.save()
    #                 json_str = json.dumps(query)
    #
    #                 link_key = cls.create_invite_email_link(admin_type, ids, admin.id, json_str)
    #                 html_template = cls.create_template(is_joined, lang_type, name, link_key, link_url_array, index, admin_type)
    #
    #                 email_message = EmailMultiAlternatives(invite_title(lang_type), '', email_sender, to=[row])
    #                 email_message.attach_alternative(html_template, "text/html")
    #                 email_message.send()
    #
    #             proc_result['result'] = True
    #             proc_result['urls'] = link_url_array
    #         else:
    #             proc_result['result'] = False
    #             proc_result['code'] = AdminCode.INTERNAL_SERVER_ERROR.value
    #             proc_result['message'] = AdminCode.INTERNAL_SERVER_ERROR.name
    #             has_exception(proc_result=proc_result, exception=None)
    #     except Exception as exception:
    #         proc_result['l_desc'] = error_mail
    #         has_exception(proc_result=proc_result, exception=exception)
    #         transaction.savepoint_rollback(sid)
    #     finally:
    #         return proc_result
    #
    #     return proc_result
    #
    # @classmethod
    # def create_template(cls, is_joined, lang_type, name, link_key, link_url_array, index, admin_type):
    #     template_file_name = 'admin/InviteAdminMailTemplate_' + lang_type + '.html'
    #     header_image_url = settings.MAIL_TEMPLATE_SERVER_URL + '/statics'
    #
    #     if is_joined:
    #         link_url = settings.MAIL_TEMPLATE_SERVER_URL + '?dataLink=' + link_key
    #         link_button_type = 'login'
    #     else:
    #         link_url = settings.MAIL_TEMPLATE_SERVER_URL + '/newAccount?dataLink=' + link_key
    #         link_button_type = 'create'
    #
    #     link_button_label = invite_button_name(lang_type, link_button_type)
    #
    #     message = invite_message(lang_type, name, admin_type)
    #
    #     html_template = get_template(template_file_name).render(
    #         {'headerImageUrl': header_image_url, 'linkButtonLabel': link_button_label, 'message': message, 'linkUrl': link_url}
    #     )
    #
    #     link_url_array.insert(index, link_url)
    #
    #     return html_template
    #
    # @classmethod
    # def create_invite_email_link(cls, admin_type, ids, admin_id, json_str):
    #     admin_type_value = AdminLinkType[admin_type]
    #
    #     query_object = Q(admin_id=admin_id)
    #
    #     if num_is_not_empty(ids['sid']) and admin_type_value is AdminLinkType.SITE:
    #         query_object &= Q(site_id=ids['sid'])
    #
    #     if num_is_not_empty(ids['eid']):
    #         query_object &= Q(env_id=ids['eid'])
    #
    #     if num_is_not_empty(ids['rid']):
    #         query_object &= Q(room_id=ids['rid'])
    #     else:
    #         query_object &= Q(room_id=None)
    #
    #     check = AdminEmailLink.objects.filter(query_object).count()
    #
    #     if check < 1:
    #          admin_email_link = AdminEmailLink()
    #     else:
    #         admin_email_link = AdminEmailLink.objects.filter(query_object)[:1][0]
    #
    #     if num_is_not_empty(ids['sid']) and admin_type_value is AdminLinkType.SITE:
    #         admin_email_link.site_id = ids['sid']
    #
    #     if num_is_not_empty(ids['eid']):
    #         admin_email_link.env_id = ids['eid']
    #
    #     if num_is_not_empty(ids['rid']):
    #         admin_email_link.room_id = ids['rid']
    #
    #     admin_email_link.admin_id = admin_id
    #     admin_email_link.link_type = admin_type_value
    #     admin_email_link.link = json_str
    #     admin_email_link.created_date = timezone.now()
    #     admin_email_link.expired_date = timezone.now()
    #
    #     admin_email_link.save()
    #
    #     cipher = AESCipher(key='AOS_VDR_ADMIN_MAIL_KEY')
    #     link_key = cipher.encrypt(raw=str(admin_email_link.id))
    #     link_key = link_key.decode('utf-8')
    #     link_key = parse.quote(link_key)
    #
    #     # link_key = base64.b64encode(str(admin_email_link.id).encode('UTF-8')).decode('utf-8')
    #
    #     return link_key
