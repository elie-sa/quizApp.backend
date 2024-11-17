from django.urls import path
from . import views, views_auth, admin
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication APIs
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup', views_auth.signup, name="signup"),
    path('login', views_auth.login, name="login"),
    path('user/confirmEmail', views_auth.confirm_email_view, name="confirm_email_view"),
    path('user/sendConfirmationEmail', views_auth.create_email_token, name = "send_confirmation_email"),
    # Forgot Password APIs
    path('user/forgotPassword', views_auth.forgot_password, name="check_email"),
    path('user/verifyOtp', views_auth.verify_otp, name="verify_otp"),
    path('user/changeForgottenPassword', views_auth.change_forgotten_password, name="change_forgotten_password"),

    # GET APIs
    path('majors', views.get_majors, name="get_majors"),
    path('courses', views.get_courses, name="get_courses"),
]
