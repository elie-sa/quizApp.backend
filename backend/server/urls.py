from django.urls import path
from . import views, views_auth, admin
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication APIs
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup', views_auth.signup, name="signup"),
    path('majors', views.get_majors, name="get_majors"),
    path('courses', views.get_courses, name="get_courses"),
]
