"""
API Views for RBAC (Role-Based Access Control)
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.db import transaction
import json

from .models import Permission, Role, UserRole
from .permissions import require_permission, has_permission, get_user_permissions, clear_user_permission_cache

UserProfile = get_user_model()


# ==================== Permission Views ====================

@require_http_methods(["GET"])
def list_permissions(request):
    """List all permissions, optionally filtered by category"""
    category = request.GET.get('category')
    
    permissions = Permission.objects.all()
    if category:
        permissions = permissions.filter(category=category)
    
    # Group by category
    categories = {}
    for perm in permissions:
        if perm.category not in categories:
            categories[perm.category] = []
        categories[perm.category].append({
            'id': perm.id,
            'code': perm.code,
            'name': perm.name,
            'description': perm.description
        })
    
    return JsonResponse({
        'permissions': list(permissions.values()),
        'categories': categories,
        'total': permissions.count()
    })


@require_http_methods(["GET"])
def list_permission_categories(request):
    """Get list of all permission categories"""
    categories = Permission.objects.values_list('category', flat=True).distinct()
    
    category_data = []
    for cat in categories:
        count = Permission.objects.filter(category=cat).count()
        category_data.append({
            'name': cat,
            'count': count
        })
    
    return JsonResponse({'categories': category_data})


# ==================== Role Views ====================

@require_permission('role.view')
@require_http_methods(["GET"])
def list_roles(request):
    """List all roles with their permissions"""
    roles = Role.objects.all().prefetch_related('permissions')
    
    role_data = []
    for role in roles:
        # Count users with this role
        user_count = UserRole.objects.filter(role=role).count()
        
        role_data.append({
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'level': role.level,
            'is_system_role': role.is_system_role,
            'permission_count': role.permissions.count(),
            'user_count': user_count,
            'permissions': list(role.permissions.values('id', 'code', 'name')),
            'created_at': role.created_at,
            'updated_at': role.updated_at
        })
    
    return JsonResponse({'roles': role_data, 'total': len(role_data)})


@require_permission('role.view')
@require_http_methods(["GET"])
def get_role(request, role_id):
    """Get single role details"""
    try:
        role = Role.objects.prefetch_related('permissions').get(id=role_id)
        
        # Get users with this role
        user_roles = UserRole.objects.filter(role=role).select_related('user')
        users = [{
            'id': ur.user.id,
            'username': ur.user.username,
            'email': ur.user.email,
            'assigned_at': ur.assigned_at
        } for ur in user_roles]
        
        return JsonResponse({
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'level': role.level,
            'is_system_role': role.is_system_role,
            'permissions': list(role.permissions.values()),
            'users': users,
            'created_at': role.created_at,
            'updated_at': role.updated_at
        })
    except Role.DoesNotExist:
        return JsonResponse({'error': 'Role not found'}, status=404)


@require_permission('role.create')
@require_http_methods(["POST"])
@csrf_exempt
def create_role(request):
    """Create a new role"""
    try:
        data = json.loads(request.body)
        name = data.get('name')
        description = data.get('description', '')
        level = data.get('level', 5)
        permission_ids = data.get('permissions', [])
        
        if not name:
            return JsonResponse({'error': 'Role name is required'}, status=400)
        
        # Check if role already exists
        if Role.objects.filter(name=name).exists():
            return JsonResponse({'error': 'Role with this name already exists'}, status=400)
        
        with transaction.atomic():
            # Create role
            role = Role.objects.create(
                name=name,
                description=description,
                level=level,
                is_system_role=False
            )
            
            # Assign permissions
            if permission_ids:
                permissions = Permission.objects.filter(id__in=permission_ids)
                role.permissions.set(permissions)
        
        return JsonResponse({
            'message': 'Role created successfully',
            'role': {
                'id': role.id,
                'name': role.name,
                'description': role.description,
                'level': role.level
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_permission('role.edit')
@require_http_methods(["PUT"])
@csrf_exempt
def update_role(request, role_id):
    """Update an existing role"""
    try:
        role = Role.objects.get(id=role_id)
        
        # Prevent editing system roles
        if role.is_system_role:
            return JsonResponse({'error': 'Cannot edit system roles'}, status=403)
        
        data = json.loads(request.body)
        
        with transaction.atomic():
            # Update fields
            if 'name' in data:
                role.name = data['name']
            if 'description' in data:
                role.description = data['description']
            if 'level' in data:
                role.level = data['level']
            
            role.save()
            
            # Update permissions
            if 'permissions' in data:
                permissions = Permission.objects.filter(id__in=data['permissions'])
                role.permissions.set(permissions)
                
                # Clear cache for all users with this role
                user_roles = UserRole.objects.filter(role=role).select_related('user')
                for ur in user_roles:
                    clear_user_permission_cache(ur.user)
        
        return JsonResponse({
            'message': 'Role updated successfully',
            'role': {
                'id': role.id,
                'name': role.name,
                'description': role.description
            }
        })
        
    except Role.DoesNotExist:
        return JsonResponse({'error': 'Role not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_permission('role.delete')
@require_http_methods(["DELETE"])
def delete_role(request, role_id):
    """Delete a role"""
    try:
        role = Role.objects.get(id=role_id)
        
        # Prevent deleting system roles
        if role.is_system_role:
            return JsonResponse({'error': 'Cannot delete system roles'}, status=403)
        
        # Check if role is assigned to users
        user_count = UserRole.objects.filter(role=role).count()
        if user_count > 0:
            return JsonResponse({
                'error': f'Cannot delete role. It is assigned to {user_count} user(s)'
            }, status=400)
        
        role.delete()
        
        return JsonResponse({'message': 'Role deleted successfully'})
        
    except Role.DoesNotExist:
        return JsonResponse({'error': 'Role not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==================== User Role Assignment Views ====================

@require_permission('user.view')
@require_http_methods(["GET"])
def get_user_roles(request, user_id):
    """Get roles assigned to a user"""
    try:
        user = UserProfile.objects.get(id=user_id)
        user_roles = UserRole.objects.filter(user=user).select_related('role', 'assigned_by')
        
        roles_data = [{
            'id': ur.role.id,
            'name': ur.role.name,
            'description': ur.role.description,
            'level': ur.role.level,
            'assigned_at': ur.assigned_at,
            'assigned_by': ur.assigned_by.username if ur.assigned_by else None
        } for ur in user_roles]
        
        return JsonResponse({
            'user_id': user.id,
            'username': user.username,
            'roles': roles_data,
            'permissions': get_user_permissions(user)
        })
        
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)


@require_permission('user.manage_roles')
@require_http_methods(["POST"])
@csrf_exempt
def assign_role_to_user(request, user_id):
    """Assign a role to a user"""
    try:
        user = UserProfile.objects.get(id=user_id)
        data = json.loads(request.body)
        role_id = data.get('role_id')
        
        if not role_id:
            return JsonResponse({'error': 'role_id is required'}, status=400)
        
        role = Role.objects.get(id=role_id)
        
        # Create user role assignment
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={'assigned_by': request.user}
        )
        
        # Clear permission cache
        clear_user_permission_cache(user)
        
        if created:
            return JsonResponse({
                'message': f'Role "{role.name}" assigned to user successfully'
            }, status=201)
        else:
            return JsonResponse({
                'message': f'User already has role "{role.name}"'
            })
            
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Role.DoesNotExist:
        return JsonResponse({'error': 'Role not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_permission('user.manage_roles')
@require_http_methods(["DELETE"])
def remove_role_from_user(request, user_id, role_id):
    """Remove a role from a user"""
    try:
        user = UserProfile.objects.get(id=user_id)
        role = Role.objects.get(id=role_id)
        
        user_role = UserRole.objects.filter(user=user, role=role).first()
        
        if user_role:
            user_role.delete()
            clear_user_permission_cache(user)
            return JsonResponse({'message': f'Role "{role.name}" removed from user'})
        else:
            return JsonResponse({'error': 'User does not have this role'}, status=404)
            
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Role.DoesNotExist:
        return JsonResponse({'error': 'Role not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==================== Permission Check Views ====================

@require_http_methods(["POST"])
@csrf_exempt
def check_permission(request):
    """Check if current user has a specific permission"""
    try:
        data = json.loads(request.body)
        permission_code = data.get('permission')
        
        if not permission_code:
            return JsonResponse({'error': 'permission code is required'}, status=400)
        
        has_perm = has_permission(request.user, permission_code)
        
        return JsonResponse({
            'has_permission': has_perm,
            'permission': permission_code,
            'user': request.user.username
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@require_http_methods(["GET"])
def get_my_permissions(request):
    """Get all permissions for current user"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    permissions = get_user_permissions(request.user)
    
    # Get roles
    user_roles = UserRole.objects.filter(user=request.user).select_related('role')
    roles = [{
        'id': ur.role.id,
        'name': ur.role.name,
        'level': ur.role.level
    } for ur in user_roles]
    
    return JsonResponse({
        'user': request.user.username,
        'roles': roles,
        'permissions': permissions,
        'is_superuser': request.user.is_superuser
    })


# ==================== User Management Views ====================

@require_permission('user.view')
@require_http_methods(["GET"])
def list_users(request):
    """List all users with their roles and permissions"""
    search = request.GET.get('search', '')
    role_filter = request.GET.get('role')
    
    users = UserProfile.objects.all()
    
    # Apply search filter
    if search:
        users = users.filter(
            username__icontains=search
        ) | users.filter(
            email__icontains=search
        )
    
    # Apply role filter
    if role_filter and role_filter != 'all':
        users = users.filter(user_roles__role__name=role_filter).distinct()
    
    user_data = []
    for user in users:
        # Get user roles
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        roles = [{
            'id': ur.role.id,
            'name': ur.role.name,
            'level': ur.role.level
        } for ur in user_roles]
        
        # Get permissions
        permissions = get_user_permissions(user)
        
        user_data.append({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_superuser': user.is_superuser,
            'last_login': user.last_login,
            'created_at': user.created_at,
            'roles': roles,
            'permissions': permissions[:10],  # First 10 permissions for list view
            'permission_count': len(permissions)
        })
    
    return JsonResponse({
        'users': user_data,
        'total': len(user_data)
    })


@require_permission('user.view')
@require_http_methods(["GET"])
def get_user_detail(request, user_id):
    """Get detailed information about a specific user"""
    try:
        user = UserProfile.objects.get(id=user_id)
        
        # Get user roles
        user_roles = UserRole.objects.filter(user=user).select_related('role', 'assigned_by')
        roles = [{
            'id': ur.role.id,
            'name': ur.role.name,
            'description': ur.role.description,
            'level': ur.role.level,
            'assigned_at': ur.assigned_at,
            'assigned_by': ur.assigned_by.username if ur.assigned_by else None
        } for ur in user_roles]
        
        # Get all permissions
        permissions = get_user_permissions(user)
        
        return JsonResponse({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_superuser': user.is_superuser,
            'last_login': user.last_login,
            'created_at': user.created_at,
            'updated_at': user.updated_at,
            'roles': roles,
            'permissions': permissions
        })
        
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)


@require_permission('user.create')
@require_http_methods(["POST"])
@csrf_exempt
def invite_user(request):
    """Invite a new user (create user account)"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password', 'TempPassword123!')
        role_id = data.get('role_id')
        
        if not username or not email:
            return JsonResponse({'error': 'Username and email are required'}, status=400)
        
        # Check if user exists
        if UserProfile.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        
        if UserProfile.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)
        
        with transaction.atomic():
            # Create user
            user = UserProfile.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Assign role if provided
            if role_id:
                role = Role.objects.get(id=role_id)
                UserRole.objects.create(
                    user=user,
                    role=role,
                    assigned_by=request.user
                )
        
        return JsonResponse({
            'message': 'User invited successfully',
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email
            }
        }, status=201)
        
    except Role.DoesNotExist:
        return JsonResponse({'error': 'Role not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_permission('user.edit')
@require_http_methods(["PUT"])
@csrf_exempt
def update_user_status(request, user_id):
    """Update user active status"""
    try:
        user = UserProfile.objects.get(id=user_id)
        data = json.loads(request.body)
        
        if 'is_active' in data:
            user.is_active = data['is_active']
            user.save()
        
        return JsonResponse({
            'message': 'User status updated successfully',
            'is_active': user.is_active
        })
        
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_permission('user.delete')
@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    """Delete a user"""
    try:
        user = UserProfile.objects.get(id=user_id)
        
        # Prevent deleting yourself
        if user.id == request.user.id:
            return JsonResponse({'error': 'Cannot delete your own account'}, status=400)
        
        # Prevent deleting superusers
        if user.is_superuser:
            return JsonResponse({'error': 'Cannot delete superuser accounts'}, status=403)
        
        user.delete()
        
        return JsonResponse({'message': 'User deleted successfully'})
        
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
