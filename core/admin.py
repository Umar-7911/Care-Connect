"""
Django Admin configuration for Core app models
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Hospital, AmbulanceProvider, Ambulance, ActivityLog, OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""
    list_display = ('username', 'email', 'role', 'phone', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'country')}),
        ('Role & Type', {'fields': ('role',)}),
        ('Hospital Info', {
            'fields': ('hospital_name', 'hospital_address', 'hospital_city'),
            'classes': ('collapse',),
        }),
        ('Ambulance Provider Info', {
            'fields': ('company_name', 'company_address', 'company_city'),
            'classes': ('collapse',),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at')}),
    )
    
    readonly_fields = ('created_at', 'date_joined', 'last_login')


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    """Hospital Admin"""
    list_display = (
        'name', 'city', 'type',
        'beds_total', 'beds_total_capacity',
        'beds_icu', 'beds_icu_capacity',
        'owner', 'updated_at'
    )
    list_filter = ('type', 'city')
    search_fields = ('name', 'city', 'email', 'phone')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'type', 'address', 'city', 'email', 'phone')
        }),
        ('Bed Availability', {
            'fields': (
                ('beds_total', 'beds_total_capacity'),
                ('beds_icu', 'beds_icu_capacity'),
                ('beds_oxygen', 'beds_oxygen_capacity'),
                ('beds_ventilator', 'beds_ventilator_capacity'),
                ('beds_isolation', 'beds_isolation_capacity'),
            )
        }),
        ('Additional Info', {
            'fields': ('facilities', 'pricing_info', 'insurance_providers')
        }),
        ('Management', {
            'fields': ('owner',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AmbulanceProvider)
class AmbulanceProviderAdmin(admin.ModelAdmin):
    """Ambulance Provider Admin"""
    list_display = ('name', 'city', 'phone', 'ambulance_count', 'owner', 'updated_at')
    list_filter = ('city',)
    search_fields = ('name', 'city', 'email', 'phone')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'address', 'city', 'email', 'phone')
        }),
        ('Service Details', {
            'fields': ('service_area', 'pricing_info')
        }),
        ('Management', {
            'fields': ('owner',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def ambulance_count(self, obj):
        """Display number of ambulances"""
        return obj.ambulances.count()
    ambulance_count.short_description = 'Ambulances'


class AmbulanceInline(admin.TabularInline):
    """Inline Ambulance for Provider Admin"""
    model = Ambulance
    extra = 1
    fields = ('vehicle_number', 'type', 'driver_name', 'driver_phone', 'status')


# Add inline to AmbulanceProviderAdmin
AmbulanceProviderAdmin.inlines = [AmbulanceInline]


@admin.register(Ambulance)
class AmbulanceAdmin(admin.ModelAdmin):
    """Ambulance Admin"""
    list_display = ('vehicle_number', 'type', 'provider', 'driver_name', 'status', 'updated_at')
    list_filter = ('type', 'status')
    search_fields = ('vehicle_number', 'driver_name', 'driver_phone')
    ordering = ('vehicle_number',)
    
    fieldsets = (
        ('Vehicle Information', {
            'fields': ('vehicle_number', 'type', 'status')
        }),
        ('Driver Information', {
            'fields': ('driver_name', 'driver_phone')
        }),
        ('Provider', {
            'fields': ('provider',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    """OTP Admin"""
    list_display = (
        'email', 'phone', 'otp_type',
        'otp_code', 'is_verified',
        'created_at', 'expires_at'
    )
    list_filter = ('otp_type', 'is_verified', 'created_at')
    search_fields = ('email', 'phone', 'otp_code')
    readonly_fields = ('created_at', 'expires_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('OTP Information', {
            'fields': ('email', 'phone', 'otp_type', 'otp_code', 'is_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at'),
        }),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Activity Log Admin (Read-only)"""
    list_display = ('user', 'user_role', 'action', 'timestamp')
    list_filter = ('user_role', 'action', 'timestamp')
    search_fields = ('user__username', 'action', 'details')
    ordering = ('-timestamp',)

    fieldsets = (
        ('Log Information', {
            'fields': ('user', 'user_role', 'action', 'details', 'timestamp')
        }),
    )

    readonly_fields = (
        'user', 'user_role',
        'action', 'details',
        'timestamp'
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False