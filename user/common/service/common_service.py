from user.models import BoxUsers, BoxGroupmember
from user.main.models import BoxUserrole
from user.management.models import Policy


# user 구하기
def get_user(user_id):
    try:
        user = BoxUsers.objects.get(pk=user_id)
    except BoxUsers.DoesNotExist:
        return None

    return user


# account_user 구하기
def get_my_account_user(user_id):
    account_user = None

    try:
        user = get_user(user_id)
        box_groupmember = BoxGroupmember.objects.get(boxUser=user)
        box_groupmembers = BoxGroupmember.objects.filter(boxGroup=box_groupmember.boxGroup)

        for box_groupmember in box_groupmembers:
            box_user = box_groupmember.boxUser
            box_userroles = BoxUserrole.objects.filter(boxUsers=box_user)
            for box_userrole in box_userroles:
                if box_userrole.boxRoles.br_id == 1:
                    account_user = box_user
                    break;

            if account_user is not None:
                break;

    except BoxGroupmember.DoesNotExist:
        return None

    return account_user


# 내 그룹의 유저 목록 구하기
def get_my_group_user_list(user_id):
    try:
        user = get_user(user_id)
        box_group = user.boxgroupmember_set.all()[0].boxGroup
        box_groupmembers = BoxGroupmember.objects.filter(boxGroup=box_group)
        group_user_list = BoxUsers.objects.filter(boxgroupmember__in=box_groupmembers)
    except BoxUsers.DoesNotExist:
        return None

    return group_user_list


# 내 그룹의 정책 구하기
def get_my_group_policy_list(user_id):
    user = get_user(user_id)
    box_group = user.boxgroupmember_set.all()[0].boxGroup
    policy_list = Policy.objects.filter(bp_accountid=box_group.bg_id)

    return policy_list
