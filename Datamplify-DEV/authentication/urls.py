from django.urls import path,include
from oauth2_provider.views import AuthorizationView, TokenView
from authentication.utils import get_access_token
from oauth2_provider import urls as oauth2_urls
from authentication.views import SignUp,AccountActivate,Login,user_info_view,ForgotPasswordView,ConfirmPasswordView


urlpatterns = [
    path('o/',include(oauth2_urls)),

    path('signup/',SignUp.as_view(),name='Registeration'),

    path('activate_account/<str:token>',AccountActivate.as_view(),name='Account_Activation'),

    path('reset_password/',ForgotPasswordView.as_view(),name='reset Password'),

    path('reset_password/confirm/<token>',ConfirmPasswordView.as_view(), name='Forgot Password Confirm'),

    path('login/',Login.as_view(),name = 'User Login'),

    path('me/', user_info_view), #airflow user data

]
