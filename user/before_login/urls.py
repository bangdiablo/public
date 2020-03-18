from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.Login.as_view()),
    path('sendEmailToResetPassword/', views.SendEmailToResetPassword.as_view()),        # 패스워드 변경 이메일 보내기
    path('resetPassword/', views.ResetPassword.as_view()),                              # 패스워드 변경
    path('secondCertification/', views.SecondCertification.as_view()),                  # 2단계 인증
    path('checkValidKey/', views.CheckValidKey.as_view()),                              # 메일 링크의 유효한 key인지 확인
    path('checkExistEmail/', views.CheckExistEmail.as_view()),                          # 이메일 중복 조회
    path('checkLicenseKey/', views.CheckLicenseKey.as_view()),                          # 라이센스 키 검증
    path('checkRecaptcha/', views.CheckRecaptcha.as_view()),                            # Recaptcha 확인
    path('registMemberWithLicenseKey/', views.RegistMemberWithLicenseKey.as_view()),    # 이메일로 사용자 등록
]
