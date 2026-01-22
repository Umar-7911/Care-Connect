"""
Core app views - handles authentication and landing page
Updated to use Django ORM instead of MongoDB
Hospital/Ambulance admins are created through Django admin only
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from core.models import User, Hospital, AmbulanceProvider, ActivityLog, OTP
from core.utils import send_email_with_fallback
from django.http import JsonResponse
import random
import re
from datetime import timedelta
import json


def landing(request):
    """Landing page"""
    if request.user.is_authenticated:
        # Redirect to appropriate dashboard based on role
        role = request.user.role
        if role == 'hospital':
            return redirect('hospital:dashboard')
        elif role == 'ambulance':
            return redirect('ambulance:dashboard')
        else:
            return redirect('userapp:home')
    return render(request, 'core/landing.html')


def check_username(request):
    """Check if username is available"""
    username = request.GET.get('username', '').strip()
    
    if len(username) < 3:
        return JsonResponse({'available': False, 'message': 'Username must be at least 3 characters'})
    
    if User.objects.filter(username=username).exists():
        return JsonResponse({'available': False, 'message': 'Username already taken'})
    
    return JsonResponse({'available': True, 'message': 'Username is available'})


def send_email_otp(request):
    """Send OTP to email"""
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        # Validate email format
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_regex.match(email):
            return JsonResponse({'success': False, 'message': 'Invalid email format'})
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Email already registered'})
        
        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        
        # Delete old OTPs for this email
        OTP.objects.filter(email=email, otp_type='email', is_verified=False).delete()
        
        # Create new OTP (expires in 10 minutes)
        otp = OTP.objects.create(
            email=email,
            otp_code=otp_code,
            otp_type='email',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        # Send OTP via email (SMTP or console fallback)
        email_sent = send_email_with_fallback(email, otp_code, purpose='email_verification')
        
        if email_sent:
            return JsonResponse({'success': True, 'message': 'OTP sent to your email', 'otp': otp_code})
        else:
            return JsonResponse({'success': False, 'message': 'Failed to send OTP. Please try again.'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def verify_email_otp(request):
    """Verify email OTP"""
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        otp = data.get('otp', '').strip()
        
        # Get latest unverified OTP for this email
        otp_obj = OTP.objects.filter(
            email=email,
            otp_type='email',
            otp_code=otp,
            is_verified=False
        ).order_by('-created_at').first()
        
        if not otp_obj:
            return JsonResponse({'success': False, 'message': 'Invalid OTP'})
        
        if otp_obj.is_expired():
            return JsonResponse({'success': False, 'message': 'OTP has expired. Please request a new one.'})
        
        # Mark OTP as verified
        otp_obj.is_verified = True
        otp_obj.save()
        
        return JsonResponse({'success': True, 'message': 'Email verified successfully'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def send_phone_otp(request):
    """Send OTP to phone"""
    if request.method == 'POST':
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()
        country_code = data.get('country_code', '+91')
        
        # Validate phone number
        if country_code == '+91':
            if not phone or len(phone) != 10 or not phone.isdigit():
                return JsonResponse({'success': False, 'message': 'Phone number must be exactly 10 digits for India'})
        else:
            if not phone or len(phone) < 10 or not phone.isdigit():
                return JsonResponse({'success': False, 'message': 'Please enter a valid phone number'})
        
        full_phone = f"{country_code}{phone}"
        
        # Check if phone already exists
        if User.objects.filter(phone=full_phone).exists():
            return JsonResponse({'success': False, 'message': 'Phone number already registered'})
        
        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        
        # Delete old OTPs for this phone
        OTP.objects.filter(phone=full_phone, otp_type='phone', is_verified=False).delete()
        
        # Create new OTP (expires in 10 minutes)
        otp = OTP.objects.create(
            phone=full_phone,
            otp_code=otp_code,
            otp_type='phone',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        # In production, send OTP via SMS service (Twilio, AWS SNS, etc.)
        # For now, we'll store it and return it (for testing purposes)
        print(f"OTP for {full_phone}: {otp_code}")  # Remove in production
        
        return JsonResponse({'success': True, 'message': 'OTP sent to your phone', 'otp': otp_code})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def verify_phone_otp(request):
    """Verify phone OTP"""
    if request.method == 'POST':
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()
        country_code = data.get('country_code', '+91')
        otp = data.get('otp', '').strip()
        
        full_phone = f"{country_code}{phone}"
        
        # Get latest unverified OTP for this phone
        otp_obj = OTP.objects.filter(
            phone=full_phone,
            otp_type='phone',
            otp_code=otp,
            is_verified=False
        ).order_by('-created_at').first()
        
        if not otp_obj:
            return JsonResponse({'success': False, 'message': 'Invalid OTP'})
        
        if otp_obj.is_expired():
            return JsonResponse({'success': False, 'message': 'OTP has expired. Please request a new one.'})
        
        # Mark OTP as verified
        otp_obj.is_verified = True
        otp_obj.save()
        
        return JsonResponse({'success': True, 'message': 'Phone verified successfully'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@require_http_methods(["GET", "POST"])
def signup(request):
    """User signup with role selection
    
    Note: Hospital and Ambulance admins are created through Django admin.
    During signup, only basic user account is created.
    Superadmin will then assign them to a hospital/ambulance provider.
    """
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        country_code = request.POST.get('countryCode', '+91')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        country = request.POST.get('country', '')
        role = request.POST.get('role', 'user')  # user, hospital, ambulance
        
        # Validation
        errors = []
        
        # Username validation
        if len(username) < 3:
            errors.append('Username must be at least 3 characters')
        if User.objects.filter(username=username).exists():
            errors.append('Username already taken')
        
        # Email validation
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_regex.match(email):
            errors.append('Please enter a valid email address')
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered')
        
        # Phone validation
        if country_code == '+91':
            if not phone or len(phone) != 10 or not phone.isdigit():
                errors.append('Phone number must be exactly 10 digits for India')
        else:
            if not phone or len(phone) < 10:
                errors.append('Please enter a valid phone number')
        
        full_phone = f"{country_code}{phone}"
        if User.objects.filter(phone=full_phone).exists():
            errors.append('Phone number already registered')
        
        # Password validation
        if len(password) < 8:
            errors.append('Password must be at least 8 characters')
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'core/signup.html', {
                'username': username,
                'email': email,
                'phone': phone,
                'country': country,
                'role': role
            })
        
        # Create user account only
        try:
            user = User(
                username=username,
                email=email,
                phone=full_phone,
                country=country,
                role=role,
                is_active=True
            )
            user.set_password(password)
            user.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=user,
                user_role=role,
                action='signup',
                details=f'New {role} account created'
            )
            
            # Different messages based on role
            if role in ['hospital', 'ambulance']:
                messages.success(request, 
                    'Account created successfully! Please contact the administrator to assign you to a hospital/ambulance provider.')
            else:
                messages.success(request, 'Account created successfully! Please login.')
            
            return redirect('core:login')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'core/signup.html')
    
    return render(request, 'core/signup.html')


@require_http_methods(["GET", "POST"])
def login(request):
    """User login with role-based redirect"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        
        # Validation
        if not email or not password:
            messages.error(request, 'Please enter both email and password')
            return render(request, 'core/login.html', {'email': email})
        
        # Get user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'core/login.html', {'email': email})
        
        # Authenticate
        authenticated_user = authenticate(request, username=user.username, password=password)
        
        if not authenticated_user:
            messages.error(request, 'Invalid email or password')
            return render(request, 'core/login.html', {'email': email})
        
        # Check if user is active
        if not user.is_active:
            messages.error(request, 'Your account has been deactivated')
            return render(request, 'core/login.html', {'email': email})
        
        # Log in the user
        auth_login(request, authenticated_user)
        
        # Log activity
        ActivityLog.objects.create(
            user=user,
            user_role=user.role,
            action='login',
            details='User logged in'
        )
        
        # Redirect based on role
        if user.role == 'hospital':
            # Check if user is assigned to a hospital
            hospital = Hospital.objects.filter(owner=user).first()
            if hospital:
                messages.success(request, f"Welcome back, {hospital.name}!")
                return redirect('hospital:dashboard')
            else:
                messages.warning(request, "You are not assigned to any hospital yet. Please contact the administrator.")
                auth_logout(request)
                return redirect('core:login')
                
        elif user.role == 'ambulance':
            # Check if user is assigned to an ambulance provider
            provider = AmbulanceProvider.objects.filter(owner=user).first()
            if provider:
                messages.success(request, f"Welcome back, {provider.name}!")
                return redirect('ambulance:dashboard')
            else:
                messages.warning(request, "You are not assigned to any ambulance provider yet. Please contact the administrator.")
                auth_logout(request)
                return redirect('core:login')
        else:
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('userapp:home')
    
    return render(request, 'core/login.html')


def logout(request):
    """User logout"""
    if request.user.is_authenticated:
        ActivityLog.objects.create(
            user=request.user,
            user_role=request.user.role,
            action='logout',
            details='User logged out'
        )
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('core:landing')


@require_http_methods(["GET", "POST"])
def forgot_password(request):
    """Request password reset - sends OTP to user's email"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        # Validate email format
        email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_regex.match(email):
            messages.error(request, 'Please enter a valid email address')
            return render(request, 'core/forgot_password.html', {'email': email})
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists for security
            messages.success(request, 'If an account with that email exists, we have sent a password reset OTP.')
            return render(request, 'core/forgot_password.html')
        
        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        
        # Delete old password reset OTPs for this email
        OTP.objects.filter(email=email, otp_type='email', purpose='password_reset', is_verified=False).delete()
        
        # Create new OTP (expires in 15 minutes)
        otp = OTP.objects.create(
            email=email,
            otp_code=otp_code,
            otp_type='email',
            purpose='password_reset',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        # Send OTP via email (SMTP or console fallback)
        email_sent = send_email_with_fallback(email, otp_code, purpose='password_reset')
        
        if not email_sent:
            messages.error(request, 'Failed to send OTP. Please try again later.')
            return render(request, 'core/forgot_password.html', {'email': email})
        
        # Store email in session for next step
        request.session['password_reset_email'] = email
        
        messages.success(request, 'Password reset OTP has been sent to your email address.')
        return redirect('core:verify_password_reset_otp')
    
    return render(request, 'core/forgot_password.html')


@require_http_methods(["GET", "POST"])
def verify_password_reset_otp(request):
    """Verify password reset OTP and show password reset form"""
    # Check if email is in session
    email = request.session.get('password_reset_email')
    if not email:
        messages.error(request, 'Please request a password reset first.')
        return redirect('core:forgot_password')
    
    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()
        
        if not otp:
            messages.error(request, 'Please enter the OTP')
            return render(request, 'core/reset_password.html', {'email': email})
        
        # Get latest unverified password reset OTP for this email
        otp_obj = OTP.objects.filter(
            email=email,
            otp_type='email',
            purpose='password_reset',
            otp_code=otp,
            is_verified=False
        ).order_by('-created_at').first()
        
        if not otp_obj:
            messages.error(request, 'Invalid OTP. Please check and try again.')
            return render(request, 'core/reset_password.html', {'email': email})
        
        if otp_obj.is_expired():
            messages.error(request, 'OTP has expired. Please request a new one.')
            del request.session['password_reset_email']
            return redirect('core:forgot_password')
        
        # Mark OTP as verified
        otp_obj.is_verified = True
        otp_obj.save()
        
        # Store verified OTP ID in session for password reset
        request.session['verified_otp_id'] = otp_obj.id
        request.session['password_reset_verified'] = True
        
        # Show password reset form (reuse the same template but in reset mode)
        return render(request, 'core/reset_password.html', {
            'email': email,
            'otp_verified': True
        })
    
    # GET request - show OTP verification form
    return render(request, 'core/reset_password.html', {'email': email, 'otp_verified': False})


@require_http_methods(["POST"])
def reset_password(request):
    """Reset user password after OTP verification"""
    # Check if OTP is verified
    if not request.session.get('password_reset_verified'):
        messages.error(request, 'Please verify your OTP first.')
        return redirect('core:forgot_password')
    
    email = request.session.get('password_reset_email')
    if not email:
        messages.error(request, 'Session expired. Please request a new password reset.')
        return redirect('core:forgot_password')
    
    # Get new password
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')
    
    # Validate password
    if len(password) < 8:
        messages.error(request, 'Password must be at least 8 characters')
        return render(request, 'core/reset_password.html', {
            'email': email,
            'otp_verified': True
        })
    
    if password != confirm_password:
        messages.error(request, 'Passwords do not match')
        return render(request, 'core/reset_password.html', {
            'email': email,
            'otp_verified': True
        })
    
    # Get user
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        # Clear session
        del request.session['password_reset_email']
        del request.session['password_reset_verified']
        if 'verified_otp_id' in request.session:
            del request.session['verified_otp_id']
        return redirect('core:forgot_password')
    
    # Update password
    user.set_password(password)
    user.save()
    
    # Log activity
    ActivityLog.objects.create(
        user=user,
        user_role=user.role,
        action='password_reset',
        details='Password reset successfully'
    )
    
    # Clear session
    del request.session['password_reset_email']
    del request.session['password_reset_verified']
    if 'verified_otp_id' in request.session:
        del request.session['verified_otp_id']
    
    messages.success(request, 'Your password has been reset successfully. Please login with your new password.')
    return redirect('core:login')


def require_login(view_func):
    """Decorator to require login"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to continue')
            return redirect('core:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def require_role(role):
    """Decorator to require specific role"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to continue')
                return redirect('core:login')
            if request.user.role != role:
                messages.error(request, 'You do not have permission to access this page')
                return redirect('core:landing')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
