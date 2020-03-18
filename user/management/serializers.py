
from .models import Policy, BoxPolicydata, BoxPolicyfiles, BoxVariable, BoxPolicyextension, \
    BoxPolicysetting, BoxPolicypermission
from user.main.models import BoxUsers
from user.models import BoxUserstorage, BoxSetting, BoxSettingadvance, BoxCode
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField


class policyListSerializer(serializers.ModelSerializer):
    usercnt = serializers.IntegerField()
    servercnt = serializers.IntegerField()
    class Meta:
        model = Policy
        fields = '__all__'


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxUsers
        fields = '__all__'


class BoxUsersSerializer(serializers.ModelSerializer):
    bu_fullname = serializers.CharField()
    bu_policyname = serializers.CharField()
    bu_admin_yn = serializers.CharField()
    bu_roleid = serializers.IntegerField()
    bu_gnrlsto = serializers.IntegerField()
    bu_coldsto = serializers.IntegerField()
    bu_ocr = serializers.IntegerField()
    bu_permitname = serializers.CharField()
    bu_new = serializers.CharField()

    class Meta:
        model = BoxUsers
        fields = '__all__'


class userStorageListSerializer(serializers.ModelSerializer):

    class Meta:
        model = BoxUserstorage
        fields = '__all__'


class ExtendedUserStorageSerializer(serializers.ModelSerializer):
    bs_user_fullname = serializers.CharField()
    bs_policyname = serializers.CharField()
    bs_user_computer = serializers.CharField()
    bs_new = serializers.CharField()

    class Meta:
        model = BoxUserstorage
        fields = '__all__'


class policyEditListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = '__all__'

class general_policydataEditListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxPolicydata
        fields = '__all__'

class policyFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxPolicyfiles
        fields = '__all__'

class policyVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxVariable
        fields = '__all__'

class policyExtensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxPolicyextension
        fields = '__all__'

class policySettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxPolicysetting
        fields = '__all__'

class policyPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxPolicypermission
        fields = '__all__'

class policyGeneralfilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxPolicyfiles
        fields = '__all__'


class CodeSerializer(serializers.ModelSerializer):
    pcode = SerializerMethodField()

    class Meta:
        model = BoxCode
        fields = '__all__'

    def get_pcode(self, obj):
        if obj.pcode is not None:
            return CodeSerializer(obj.pcode).data
        else:
            return None


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoxSetting
        fields = '__all__'


class SettingadvanceSerializer(serializers.ModelSerializer):
    sa_user_name = serializers.CharField()
    sa_sto_name = serializers.CharField()
    sa_div_name = serializers.CharField()
    sa_settingval_name = serializers.CharField()
    sa_modifydate_name = serializers.CharField()

    class Meta:
        model = BoxSettingadvance
        fields = '__all__'