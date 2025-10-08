"""
URL patterns for RBAC API endpoints
"""
from django.urls import path
from . import views_rbac

urlpatterns = [
    # Permission endpoints
    path('permissions/', views_rbac.list_permissions, name='list_permissions'),
    path('permissions/categories/', views_rbac.list_permission_categories, name='list_permission_categories'),
    
    # Role endpoints
    path('roles/', views_rbac.list_roles, name='list_roles'),
    path('roles/<int:role_id>/', views_rbac.get_role, name='get_role'),
    path('roles/create/', views_rbac.create_role, name='create_role'),
    path('roles/<int:role_id>/update/', views_rbac.update_role, name='update_role'),
    path('roles/<int:role_id>/delete/', views_rbac.delete_role, name='delete_role'),
    
    # User role assignment endpoints
    path('users/<int:user_id>/roles/', views_rbac.get_user_roles, name='get_user_roles'),
    path('users/<int:user_id>/roles/assign/', views_rbac.assign_role_to_user, name='assign_role_to_user'),
    path('users/<int:user_id>/roles/<int:role_id>/remove/', views_rbac.remove_role_from_user, name='remove_role_from_user'),
    
    # Permission check endpoints
    path('check-permission/', views_rbac.check_permission, name='check_permission'),
    path('my-permissions/', views_rbac.get_my_permissions, name='get_my_permissions'),
]
