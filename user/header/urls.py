from django.urls import path
from . import views

urlpatterns = [
    path('updateUserInfo/', views.UpdateUserInfo.as_view()),                # 사용자 정보 수정
    path('sendFaq/', views.SendFaq.as_view()),                              # 문의, 문제보고
    path('getOTPKey/', views.GetOTPKey.as_view()),                          # OTP키 조회
    path('getQrcode/', views.GetQrcode.as_view()),                          # QR코드 조회
    path('checkVerificationCode/', views.CheckVerificationCode.as_view()),  # 검증 코드 체크
    path('removeCertify/', views.RemoveCertify.as_view()),                  # 2단계 인증 제거
    path('changeLanguage/', views.ChangeLanguage.as_view()),                # 언어 변경
    path('changePermitfile/', views.ChangePermitfile.as_view()),            # 관리자 파일 검색 허용
]
