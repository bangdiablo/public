from django.db import transaction
from django.db.models import F, Q, Value, Count
from rest_framework.views import APIView
from rest_framework.response import Response

from common.type.exception import Code
from reseller.models import Reseller, ResellerRoles, ResellerRoleMapping, Plan
from reseller.serializers import ResellerSerializer


class Resellers(APIView):
    @transaction.atomic
    def post(self, request):

        data_list, total_count = get_reseller_list(request)
        serialized_data_list = ResellerSerializer(data_list, many=True).data

        data = {
            'code': Code.SUCCESS.value,
            'list': serialized_data_list,
            'totalListCount': total_count,
        }

        return Response(data)


def get_reseller_list(request):

    reseller_list = []
    total_count = 0

    search_text = request.data['searchText']
    current_page = int(request.data['currentPage'])
    data_per_page = int(request.data['dataPerPage'])
    order_name = request.data['orderName']
    order_type = request.data['orderType']

    search_text = search_text.strip()
    start_index = (current_page - 1) * data_per_page
    end_index = current_page * data_per_page

    my_id = request.session['LOGGED_IN_RESELLER_ID']

    super_admin_user_id = 1

    # 활성화 상태이면서, 본인 포함 본인을 parent로 하는 reseller 목록
    reseller_list = Reseller.objects.filter(Q(rs_status='A') & (Q(rs_id=my_id) | Q(rs_tenantid=my_id))).annotate(
                        rs_license_cnt=Count('boxlicensekey', filter=Q(boxlicensekey__reseller__rs_id=F('rs_id'))),
                        rs_plan_cnt=Count('plan', filter=Q(plan__reseller__rs_id=F('rs_id'))),
                        rs_account_cnt=Count('boxusers',
                                             filter=Q(boxusers__reseller__rs_id=F('rs_id')) &
                                                    Q(boxusers__boxRoles__br_id=super_admin_user_id)),
                    )

    # 검색어 입력 시
    if search_text != '':
        reseller_list = reseller_list.filter(Q(rs_companyname__contains=search_text) | Q(rs_email__contains=search_text))

    # 리스트 총 수
    total_count = len(reseller_list)

    # order by
    if order_name == '':
        data_list = reseller_list.order_by('-rs_createdate')
    else:
        if order_type == 'asc':
            order_type = ''
        else:
            order_type = '-'

        if order_name == 'id':
            order_name = 'rs_id'
        elif order_name == 'companyname':
            order_name = 'rs_companyname'
        elif order_name == 'createdate':
            order_name = 'rs_createdate'
        elif order_name == 'license_cnt':
            order_name = 'rs_license_cnt'
        elif order_name == 'plan_cnt':
            order_name = 'rs_plan_cnt'
        elif order_name == 'account_cnt':
            order_name = 'rs_account_cnt'
        elif order_name == 'status':
            order_name = 'rs_status'

        reseller_list = reseller_list.order_by(f'{order_type}{order_name}')

    # 리스트 갯수 제한
    reseller_list = reseller_list[start_index:end_index]

    for reseller in reseller_list:
        reseller.rs_pw = ""

    return reseller_list, total_count
