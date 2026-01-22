"""
Core app models - User and authentication related models
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    Supports multiple user roles: user, hospital, ambulance, superuser
    """
    ROLE_CHOICES = [
        ('user', 'General User'),
        ('hospital', 'Hospital Admin'),
        ('ambulance', 'Ambulance Provider'),
        ('superuser', 'System Administrator'),
    ]
    
    # Additional fields
    phone = models.CharField(max_length=20)
    country = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    
    # Hospital-specific fields (only used when role='hospital')
    hospital_name = models.CharField(max_length=255, blank=True)
    hospital_address = models.TextField(blank=True)
    hospital_city = models.CharField(max_length=100, blank=True)
    
    # Ambulance-specific fields (only used when role='ambulance')
    company_name = models.CharField(max_length=255, blank=True)
    company_address = models.TextField(blank=True)
    company_city = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class OTP(models.Model):
    """
    OTP model for email and phone verification during signup and password reset
    """
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    otp_code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=10, choices=[('email', 'Email'), ('phone', 'Phone')])
    purpose = models.CharField(max_length=20, choices=[('email_verification', 'Email Verification'), ('password_reset', 'Password Reset')], default='email_verification')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'otps'
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.otp_type} OTP for {self.email or self.phone}"
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if OTP is valid and not expired"""
        return not self.is_expired() and not self.is_verified


class Hospital(models.Model):
    """
    Hospital model for storing hospital information and bed availability
    """
    TYPE_CHOICES = [
        ('government', 'Government'),
        ('private', 'Private'),
    ]
    
    # Basic information
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100, db_index=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='private')
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Bed availability (stored as JSON for flexibility)
    beds_icu = models.IntegerField(default=0, verbose_name='ICU Beds')
    beds_oxygen = models.IntegerField(default=0, verbose_name='Oxygen Beds')
    beds_ventilator = models.IntegerField(default=0, verbose_name='Ventilators')
    beds_isolation = models.IntegerField(default=0, verbose_name='Isolation Beds')
    beds_total = models.IntegerField(default=0, verbose_name='Total Beds')

    # Bed capacity (totals) - used for displaying available/total on user dashboard
    beds_icu_capacity = models.IntegerField(default=0, verbose_name='ICU Beds (Total Capacity)')
    beds_oxygen_capacity = models.IntegerField(default=0, verbose_name='Oxygen Beds (Total Capacity)')
    beds_ventilator_capacity = models.IntegerField(default=0, verbose_name='Ventilators (Total Capacity)')
    beds_isolation_capacity = models.IntegerField(default=0, verbose_name='Isolation Beds (Total Capacity)')
    beds_total_capacity = models.IntegerField(default=0, verbose_name='Total Beds (Total Capacity)')
    
    # Facilities (stored as comma-separated values or use ManyToMany if needed)
    facilities = models.TextField(blank=True, help_text='Comma-separated list of facilities')
    
    # Pricing information (JSON field for flexibility)
    pricing_info = models.JSONField(default=dict, blank=True)
    
    # Insurance providers (JSON field for accepted insurance providers)
    insurance_providers = models.JSONField(default=dict, blank=True, help_text='Accepted insurance providers')
    
    # Location coordinates (for mapping)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text='Latitude coordinate')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text='Longitude coordinate')
    
    # Relationship to user (hospital admin)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hospitals')
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hospitals'
        verbose_name = 'Hospital'
        verbose_name_plural = 'Hospitals'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.city}"
    
    def get_facilities_list(self):
        """Return facilities as a list"""
        return [f.strip() for f in self.facilities.split(',') if f.strip()]
    
    def set_facilities_list(self, facilities_list):
        """Set facilities from a list"""
        self.facilities = ', '.join(facilities_list)


class AmbulanceProvider(models.Model):
    """
    Ambulance Provider model for companies providing ambulance services
    """
    # Basic information
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100, db_index=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Service area (stored as comma-separated cities)
    service_area = models.TextField(help_text='Comma-separated list of cities served')
    
    # Pricing information
    pricing_info = models.JSONField(default=dict, blank=True)
    
    # Relationship to user (ambulance provider admin)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ambulance_providers')
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ambulance_providers'
        verbose_name = 'Ambulance Provider'
        verbose_name_plural = 'Ambulance Providers'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_service_area_list(self):
        """Return service area as a list"""
        return [city.strip() for city in self.service_area.split(',') if city.strip()]
    
    def set_service_area_list(self, cities_list):
        """Set service area from a list"""
        self.service_area = ', '.join(cities_list)


class Ambulance(models.Model):
    """
    Individual Ambulance model
    """
    TYPE_CHOICES = [
        ('ALS', 'Advanced Life Support'),
        ('BLS', 'Basic Life Support'),
        ('Non-Emergency', 'Non-Emergency'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('maintenance', 'Under Maintenance'),
        ('offline', 'Offline'),
    ]
    
    # Basic information
    vehicle_number = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    driver_name = models.CharField(max_length=255)
    driver_phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Facilities (stored as comma-separated values)
    facilities = models.TextField(blank=True, help_text='Comma-separated list of facilities')
    is_available = models.BooleanField(default=True, verbose_name='Currently Available')
    
    # Relationship to provider
    provider = models.ForeignKey(AmbulanceProvider, on_delete=models.CASCADE, related_name='ambulances')
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ambulances'
        verbose_name = 'Ambulance'
        verbose_name_plural = 'Ambulances'
        ordering = ['vehicle_number']
    
    def __str__(self):
        return f"{self.vehicle_number} - {self.get_type_display()}"


class Booking(models.Model):
    """
    Booking model for ambulance service bookings
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # User and provider information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    provider = models.ForeignKey(AmbulanceProvider, on_delete=models.CASCADE, related_name='bookings')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='bookings')
    ambulance = models.ForeignKey(Ambulance, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    
    # Patient information
    patient_name = models.CharField(max_length=255)
    patient_phone = models.CharField(max_length=20)
    contact_person = models.CharField(max_length=255, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Location information
    pickup_location = models.TextField()
    drop_location = models.TextField()
    
    # Schedule information
    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    emergency_type = models.CharField(max_length=50, default='non-emergency')
    notes = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking #{self.id} - {self.patient_name} ({self.status})"


class ActivityLog(models.Model):
    """
    Activity log for tracking user actions
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    user_role = models.CharField(max_length=20)
    action = models.CharField(max_length=100)
    details = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        db_table = 'activity_logs'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user_role} - {self.action} at {self.timestamp}"
