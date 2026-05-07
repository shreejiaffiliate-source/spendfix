from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from account.views import ForgotPasswordView, GoogleLoginView, ResendOTPView, SendUpdateEmailOTPView, SignupView, MyTokenObtainPairView, UpdatePasswordView, UserProfileView, VerifyOTPView, VerifyResetOTPView, VerifyUpdateEmailOTPView, reset_password_direct    

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth APIs
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', MyTokenObtainPairView.as_view(), name='login'), # Naya view
    # 🎯 Isko aise change karke save karo:
    path('google-login/', GoogleLoginView.as_view(), name='google_login'),
    # 🎯 YE WALI LINE MISSING THI:
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'), # Ye line add karein
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    # account/urls.py   
    path('api/reset-password-direct/', reset_password_direct, name='reset_password_direct'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('verify-reset-otp/', VerifyResetOTPView.as_view(), name='verify_reset_otp'),
    path('update-password/', UpdatePasswordView.as_view(), name='update_password'),

    path('send-update-email-otp/', SendUpdateEmailOTPView.as_view(), name='send_update_email_otp'), # forgot passwrod otp 
    path('verify-update-email-otp/', VerifyUpdateEmailOTPView.as_view(), name='verify_update_email_otp'), # # forgot password resend otp 

]