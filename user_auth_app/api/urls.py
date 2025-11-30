from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserProfileList_View, UserProfileDetail_View, UserRegister_View, UserLogin_View, UserLogout_View

urlpatterns = [
    path('register/', UserRegister_View.as_view(), name='user-register'),
    path('login/', UserLogin_View.as_view(), name='user-login'),
    path('logout/', UserLogout_View.as_view(), name='user-logout'),
    path('contacts/', UserProfileList_View.as_view(), name='user-contacts'),
    path('contacts/<int:userprofile_id>/',
         UserProfileDetail_View.as_view(), name='user-contact-detail'),
]
