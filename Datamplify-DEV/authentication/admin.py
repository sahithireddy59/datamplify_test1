from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, Permission, Role, UserRole, Account_Activation, Reset_Password


# Custom UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'created_at')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')


# Permission Admin
@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('code', 'name', 'category', 'description')
    ordering = ('category', 'code')
    
    fieldsets = (
        (None, {'fields': ('code', 'name', 'category')}),
        ('Details', {'fields': ('description',)}),
        ('Metadata', {'fields': ('created_at',)}),
    )
    
    readonly_fields = ('created_at',)


# Role Admin
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'is_system_role', 'permission_count', 'created_at')
    list_filter = ('is_system_role', 'level', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('level', 'name')
    filter_horizontal = ('permissions',)
    
    fieldsets = (
        (None, {'fields': ('name', 'description')}),
        ('Settings', {'fields': ('level', 'is_system_role')}),
        ('Permissions', {'fields': ('permissions',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def permission_count(self, obj):
        return obj.permissions.count()
    permission_count.short_description = 'Permissions'


# UserRole Admin
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'assigned_by', 'assigned_at')
    list_filter = ('role', 'assigned_at')
    search_fields = ('user__username', 'user__email', 'role__name')
    ordering = ('-assigned_at',)
    
    fieldsets = (
        (None, {'fields': ('user', 'role')}),
        ('Assignment Info', {'fields': ('assigned_by', 'assigned_at')}),
    )
    
    readonly_fields = ('assigned_at',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return self.readonly_fields + ('user', 'role')
        return self.readonly_fields


# Account Activation Admin
@admin.register(Account_Activation)
class AccountActivationAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'otp', 'expiry_date', 'created_at')
    list_filter = ('created_at', 'expiry_date')
    search_fields = ('user__username', 'email', 'key')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


# Reset Password Admin
@admin.register(Reset_Password)
class ResetPasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user', 'key')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
