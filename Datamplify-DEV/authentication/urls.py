from django.urls import path,include
from oauth2_provider.views import AuthorizationView, TokenView
from authentication.utils import get_access_token
from oauth2_provider import urls as oauth2_urls
from authentication.views import SignUp,AccountActivate,Login,user_info_view,ForgotPasswordView,ConfirmPasswordView
from authentication import views_rbac


urlpatterns = [
    path('o/',include(oauth2_urls)),

    path('signup/',SignUp.as_view(),name='Registeration'),

    path('activate_account/<str:token>',AccountActivate.as_view(),name='Account_Activation'),

    path('reset_password/',ForgotPasswordView.as_view(),name='reset Password'),

    path('reset_password/confirm/<token>',ConfirmPasswordView.as_view(), name='Forgot Password Confirm'),

    path('login/',Login.as_view(),name = 'User Login'),

    path('me/', user_info_view), #airflow user data

    # RBAC - User Management
    path('users/', views_rbac.list_users, name='list_users'),
    path('users/<str:user_id>/', views_rbac.get_user_detail, name='get_user_detail'),
    path('users/invite/', views_rbac.invite_user, name='invite_user'),
    path('users/<str:user_id>/status/', views_rbac.update_user_status, name='update_user_status'),
    path('users/<str:user_id>/delete/', views_rbac.delete_user, name='delete_user'),
    
    # RBAC - Role Management
    path('roles/', views_rbac.list_roles, name='list_roles'),
    path('roles/<int:role_id>/', views_rbac.get_role, name='get_role'),
    path('roles/create/', views_rbac.create_role, name='create_role'),
    path('roles/<int:role_id>/update/', views_rbac.update_role, name='update_role'),
    path('roles/<int:role_id>/delete/', views_rbac.delete_role, name='delete_role'),
    
    # RBAC - User Role Assignment
    path('users/<str:user_id>/roles/', views_rbac.get_user_roles, name='get_user_roles'),
    path('users/<str:user_id>/roles/assign/', views_rbac.assign_role_to_user, name='assign_role'),
    path('users/<str:user_id>/roles/<int:role_id>/remove/', views_rbac.remove_role_from_user, name='remove_role'),
    
    # RBAC - Permissions
    path('permissions/', views_rbac.list_permissions, name='list_permissions'),
    path('permissions/categories/', views_rbac.list_permission_categories, name='list_permission_categories'),
    path('permissions/check/', views_rbac.check_permission, name='check_permission'),
    path('permissions/my/', views_rbac.get_my_permissions, name='get_my_permissions'),

]
