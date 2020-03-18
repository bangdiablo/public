from django.urls import path
from django.conf.urls import url

from . import views
from . import views_user
from . import views_setting

urlpatterns = [
    # 관리 - 사용자 또는 기기
    path('user_server/list/<str:list_type>/', views_user.UserServerList.as_view()),         # 목록 조회 (사용자, 컴퓨터, 서버)
    path('user_server/detail/user/<int:user_id>/list/<str:list_type>/', views_user.UserDetailList.as_view()),   # 상세의 목록 조회
    path('user_server/detail/user/<int:user_id>/', views_user.UserDetail.as_view()),        # 상세 조회 (사용자)

    path('downloadCSV/list/<str:list_type>/', views_user.DownloadCSV.as_view()),            # CSV 내보내기
    path('registMember/', views_user.RegistMember.as_view()),                               # 수동으로 사용자 등록
    path('registMembers/', views_user.RegistMembers.as_view()),                             # CSV로 사용자 등록
    # 이메일로 사용자 등록은 로그인 없이 진행하므로 before_login에 있음

    path('sendEmail/', views_user.SendEmail.as_view()),                                     # 초대 메일 발송
    path('getPolicyList/', views_user.GetPolicyList.as_view()),                             # 정책 목록 조회
    path('updateUserActive/', views_user.UpdateUserActive.as_view()),                       # 사용자 활성화/비활성화 수정
    path('updateUserLimit/', views_user.UpdateUserLimit.as_view()),                         # 사용자 제한 수정
    path('changeAdminAuth/', views_user.ChangeAdminAuth.as_view()),                         # 사용자 관리자 권한 수정
    path('changeUserInfo/', views_user.ChangeUserInfo.as_view()),                           # 사용자 정보 수정
    path('changeUserStorage/', views_user.ChangeUserStorage.as_view()),                     # 사용자 스토리지 수정
    path('checkEmailKey/', views_user.CheckEmailKey.as_view()),                             # 회원가입 화면 key 확인

    path('policy_list/', views.policy_list.as_view()),
    path('policy_list_usercnt/', views.policy_list_usercnt.as_view()),
    path('policy_editlist/', views.policy_editlist.as_view()),
    path('policy_variablelist/', views.policy_variablelist.as_view()),
    path('policy_variablelist/', views.policy_variablelist.as_view()),
    path('policy_coldFilelist/', views.policy_coldFilelist.as_view()),
    path('policy_ocrFilelist/', views.policy_ocrFilelist.as_view()),
    path('policy_exFilelist/', views.policy_exFilelist.as_view()),
    path('policy_extensionlist/', views.policy_extensionlist.as_view()),
    path('policy_settinglist/', views.policy_settinglist.as_view()),
    path('policy_permissionlist/', views.policy_permissionlist.as_view()),
    path('policy_create/', views.policy_create),
    path('policy_generalfilter/', views.policy_generalfilter.as_view()),
    path('policy_edit/', views.policy_edit),
    path('policy_generalchk/', views.policy_generalchk),
    path('policy_generalfolderedit/', views.policy_generalfolderedit),
    path('policy_search/', views.policy_search.as_view()),
    path('policy_editcoldfile/', views.policy_editcoldfile),
    path('policy_coldfolderedit/', views.policy_coldfolderedit),
    path('policy_editocrfile/', views.policy_editocrfile),
    path('policy_ocrfolderedit/', views.policy_ocrfolderedit),
    path('policy_extension/', views.policy_extension),
    path('policy_extensionfolder/', views.policy_extensionfolder),
    path('policy_extensionfiles/', views.policy_extensionfiles),
    path('policy_settings/', views.policy_settings),
    path('policy_permission/', views.policy_permission),
    url(r'^policy_delete/(?P<pk>[0-9]+)$', views.policy_delete),

    # 관리 - 설정
    path('setting/possessionSetting/', views_setting.PossessionSetting.as_view()),
    path('setting/getCategory/', views_setting.GetCategory.as_view()),
    path('setting/save/', views_setting.SaveSetting.as_view()),
    path('setting/getList/', views_setting.GetList.as_view()),
    path('setting/createPossessionDetailSetting/', views_setting.CreatePossessionDetailSetting.as_view()),
    path('setting/updatePossessionDetailSetting/', views_setting.UpdatePossessionDetailSetting.as_view()),
    path('setting/deletePossessionDetailSetting/', views_setting.DeletePossessionDetailSetting.as_view()),
    path('setting/getGroupUserList/', views_setting.GetGroupUserList.as_view()),
    path('setting/getStorageList/', views_setting.GetStorageList.as_view()),
    path('setting/createPossessionDetailSetting/', views_setting.CreatePossessionDetailSetting.as_view()),
    path('setting/updatePossessionDetailSetting/', views_setting.UpdatePossessionDetailSetting.as_view()),
]
