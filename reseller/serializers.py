from rest_framework.serializers import ModelSerializer, IntegerField
from .models import Reseller, ResellerRoleMapping, ResellerRoles, Plan


# 리셀러
class ResellerSerializer(ModelSerializer):
    rs_license_cnt = IntegerField()
    rs_plan_cnt = IntegerField()
    rs_account_cnt = IntegerField()

    class Meta:
        model = Reseller
        fields = '__all__'


# 리셀러-롤 맵핑
class ResellerRoleMappingSerializer(ModelSerializer):

    class Meta:
        model = ResellerRoleMapping
        fields = '__all__'


# 리셀러 롤
class ResellerRolesSerializer(ModelSerializer):

    class Meta:
        model = ResellerRoles
        fields = '__all__'


# 플랜
class PlanSerializer(ModelSerializer):

    class Meta:
        model = Plan
        fields = '__all__'
