"""
Database utilities for CareConnect
This file is deprecated - Django ORM is now used instead of MongoDB
Keeping minimal functions for backward compatibility during migration
"""
from django.contrib.auth.hashers import make_password, check_password
from core.models import User, ActivityLog
from django.utils import timezone


def hash_password(password):
    """Hash a password using Django's password hasher"""
    return make_password(password)


def verify_password(password, hashed):
    """Verify a password against its hash"""
    return check_password(password, hashed)


def get_user_by_email(email):
    """Get user by email"""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


def create_user(password, **kwargs):
    """Create a new user"""
    email = kwargs.get('email')
    role = kwargs.get('role', 'user')
    
    user = User(
        username=kwargs.get('username'),
        email=email,
        phone=kwargs.get('phone', ''),
        country=kwargs.get('country', ''),
        role=role,
        is_active=kwargs.get('is_active', True),
    )
    
    # Set password properly
    user.set_password(password)
    
    # Add role-specific fields
    if role == 'hospital':
        user.hospital_name = kwargs.get('hospital_name', '')
        user.hospital_address = kwargs.get('hospital_address', '')
        user.hospital_city = kwargs.get('hospital_city', '')
    elif role == 'ambulance':
        user.company_name = kwargs.get('company_name', '')
        user.company_address = kwargs.get('company_address', '')
        user.company_city = kwargs.get('company_city', '')
    
    user.save()
    return user.id


def log_activity(user_id, user_role, action, details):
    """Log user activity"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user = None
    
    ActivityLog.objects.create(
        user=user,
        user_role=user_role,
        action=action,
        details=details,
        timestamp=timezone.now()
    )


# Backward compatibility - db object
class DBCompat:
    """Compatibility layer for old MongoDB code"""
    @property
    def users(self):
        return User.objects
    
    @property
    def hospitals(self):
        from core.models import Hospital
        return Hospital.objects
    
    @property
    def ambulance_providers(self):
        from core.models import AmbulanceProvider
        return AmbulanceProvider.objects
    
    @property
    def activity_logs(self):
        return ActivityLog.objects


db = DBCompat()
