"""
Ambulance Admin App Views
Handles all ambulance provider administrator functionality
Updated to use Django ORM instead of MongoDB
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.http import JsonResponse
from core.views import require_role
from core.models import AmbulanceProvider, Ambulance, ActivityLog, User, Booking
from datetime import datetime


def log_activity(user_id, user_role, action, details):
    """Helper function to log user activities"""
    try:
        user = User.objects.get(id=user_id)
        ActivityLog.objects.create(
            user=user,
            user_role=user_role,
            action=action,
            details=details
        )
    except User.DoesNotExist:
        pass


@require_role('ambulance')
def dashboard(request):
    """Ambulance admin dashboard overview"""
    user = request.user
    
    # Get provider for this user
    try:
        provider = AmbulanceProvider.objects.get(owner=user)
    except AmbulanceProvider.DoesNotExist:
        messages.error(request, 'Provider information not found')
        return redirect('core:login')
    
    # Calculate stats
    ambulances = provider.ambulances.all()
    total_ambulances = ambulances.count()
    available_ambulances = ambulances.filter(is_available=True).count()
    
    # Count by type
    als_count = ambulances.filter(type='ALS').count()
    bls_count = ambulances.filter(type='BLS').count()
    non_emergency_count = ambulances.filter(type='Non-Emergency').count()
    
    context = {
        'provider': provider,
        'total_ambulances': total_ambulances,
        'available_ambulances': available_ambulances,
        'als_count': als_count,
        'bls_count': bls_count,
        'non_emergency_count': non_emergency_count,
        'last_updated': provider.updated_at,
    }
    
    return render(request, 'ambulance/dashboard.html', context)


@require_role('ambulance')
@require_http_methods(["GET", "POST"])
def manage_ambulances(request):
    """Manage ambulances - add, edit, delete"""
    user = request.user
    provider = get_object_or_404(AmbulanceProvider, owner=user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            # Add new ambulance
            ambulance_number = request.POST.get('ambulance_number', '').strip()[:50]  # Truncate to max length
            ambulance_type = request.POST.get('ambulance_type')
            facilities = request.POST.getlist('facilities')
            is_available = request.POST.get('is_available') == 'on'
            driver_name = request.POST.get('driver_name', '').strip()[:255]  # Truncate to max length
            driver_phone = request.POST.get('driver_phone', '').strip()[:20]  # Truncate to max length
            
            if not ambulance_number or not ambulance_type:
                messages.error(request, 'Ambulance number and type are required')
                return redirect('ambulance:manage_ambulances')
            
            # Check if ambulance number already exists (case-insensitive check for better UX)
            if Ambulance.objects.filter(vehicle_number__iexact=ambulance_number).exists():
                messages.error(request, f'Ambulance {ambulance_number} already exists')
                return redirect('ambulance:manage_ambulances')
            
            try:
                # Create new ambulance
                ambulance = Ambulance.objects.create(
                    vehicle_number=ambulance_number,
                    type=ambulance_type,
                    driver_name=driver_name or 'Not Assigned',
                    driver_phone=driver_phone or 'N/A',
                    facilities=', '.join(facilities),
                    is_available=is_available,
                    provider=provider
                )
                
                log_activity(
                    user.id,
                    'ambulance',
                    'add_ambulance',
                    f'Added ambulance {ambulance_number} ({ambulance_type})'
                )
                
                messages.success(request, f'Ambulance {ambulance_number} added successfully!')
            except Exception as e:
                messages.error(request, f'Error adding ambulance: {str(e)}')
            
        elif action == 'edit':
            # Edit existing ambulance
            ambulance_number = request.POST.get('ambulance_number')
            ambulance_type = request.POST.get('ambulance_type')
            facilities = request.POST.getlist('facilities')
            driver_name = request.POST.get('driver_name', '').strip()
            driver_phone = request.POST.get('driver_phone', '').strip()
            
            try:
                ambulance = Ambulance.objects.get(
                    vehicle_number=ambulance_number,
                    provider=provider
                )
                ambulance.type = ambulance_type
                ambulance.driver_name = driver_name or 'Not Assigned'
                ambulance.driver_phone = driver_phone or 'N/A'
                ambulance.facilities = ', '.join(facilities)
                ambulance.save()
                
                log_activity(
                    user.id,
                    'ambulance',
                    'edit_ambulance',
                    f'Updated ambulance {ambulance_number}'
                )
                
                messages.success(request, f'Ambulance {ambulance_number} updated successfully!')
            except Ambulance.DoesNotExist:
                messages.error(request, 'Ambulance not found')
            
        elif action == 'delete':
            # Delete ambulance
            ambulance_number = request.POST.get('ambulance_number')
            
            try:
                ambulance = Ambulance.objects.get(
                    vehicle_number=ambulance_number,
                    provider=provider
                )
                ambulance.delete()
                
                log_activity(
                    user.id,
                    'ambulance',
                    'delete_ambulance',
                    f'Deleted ambulance {ambulance_number}'
                )
                
                messages.success(request, 'Ambulance deleted successfully!')
            except Ambulance.DoesNotExist:
                messages.error(request, 'Ambulance not found')
            
        elif action == 'toggle_availability':
            # Toggle ambulance availability
            ambulance_number = request.POST.get('ambulance_number')
            is_available = request.POST.get('is_available') == 'true'
            
            try:
                ambulance = Ambulance.objects.get(
                    vehicle_number=ambulance_number,
                    provider=provider
                )
                ambulance.is_available = is_available
                ambulance.save()
                
                status = 'available' if is_available else 'unavailable'
                log_activity(
                    user.id,
                    'ambulance',
                    'toggle_availability',
                    f'Set ambulance {ambulance_number} to {status}'
                )
                
                messages.success(request, f'Ambulance availability updated!')
            except Ambulance.DoesNotExist:
                messages.error(request, 'Ambulance not found')
        
        return redirect('ambulance:manage_ambulances')
    
    # Available facilities
    available_facilities = [
        'Oxygen Support',
        'Basic Monitoring',
        'Paramedic',
        'Attendant',
        'Stretcher',
        'First Aid Kit',
        'Defibrillator',
        'Ventilator',
    ]
    
    # Get all ambulances for this provider
    all_ambulances = provider.ambulances.all()
    
    # Calculate statistics
    available_count = all_ambulances.filter(is_available=True).count()
    als_count = all_ambulances.filter(type='ALS').count()
    bls_count = all_ambulances.filter(type='BLS').count()
    
    # Get ambulances with their data
    ambulances_list = []
    for ambulance in all_ambulances:
        ambulances_list.append({
            'number': ambulance.vehicle_number,
            'type': ambulance.type,
            'driver_name': ambulance.driver_name,
            'driver_phone': ambulance.driver_phone,
            'facilities': ambulance.facilities.split(', ') if ambulance.facilities else [],
            'is_available': ambulance.is_available,
            'added_at': ambulance.created_at
        })
    
    context = {
        'provider': provider,
        'ambulances': ambulances_list,
        'available_facilities': available_facilities,
        'available_count': available_count,
        'als_count': als_count,
        'bls_count': bls_count,
    }
    return render(request, 'ambulance/manage_ambulances.html', context)


@require_role('ambulance')
@require_http_methods(["GET", "POST"])
def update_pricing(request):
    """Update ambulance pricing"""
    user = request.user
    provider = get_object_or_404(AmbulanceProvider, owner=user)
    
    if request.method == 'POST':
        # Get form data
        base_fare = float(request.POST.get('base_fare', 0))
        per_km = float(request.POST.get('per_km', 0))
        oxygen_charge = float(request.POST.get('oxygen_charge', 0))
        attendant_charge = float(request.POST.get('attendant_charge', 0))
        
        # Validate
        if base_fare < 0 or per_km < 0 or oxygen_charge < 0 or attendant_charge < 0:
            messages.error(request, 'Prices cannot be negative')
            return redirect('ambulance:update_pricing')
        
        # Update database
        provider.pricing_info = {
            'base_fare': base_fare,
            'per_km': per_km,
            'oxygen_charge': oxygen_charge,
            'attendant_charge': attendant_charge
        }
        provider.save()
        
        # Log activity
        log_activity(
            user.id,
            'ambulance',
            'update_pricing',
            f'Updated pricing - Base: ₹{base_fare}, Per KM: ₹{per_km}, Oxygen: ₹{oxygen_charge}, Attendant: ₹{attendant_charge}'
        )
        
        messages.success(request, 'Pricing updated successfully!')
        return redirect('ambulance:dashboard')
    
    context = {
        'provider': provider,
        'pricing': provider.pricing_info
    }
    return render(request, 'ambulance/update_pricing.html', context)


@require_role('ambulance')
@require_http_methods(["GET", "POST"])
def service_area(request):
    """Manage service area"""
    user = request.user
    provider = get_object_or_404(AmbulanceProvider, owner=user)
    
    if request.method == 'POST':
        # Get selected cities/zones
        service_areas = request.POST.getlist('service_areas')
        
        # Update database using the helper method
        provider.set_service_area_list(service_areas)
        provider.save()
        
        # Log activity
        log_activity(
            user.id,
            'ambulance',
            'update_service_area',
            f'Updated service areas: {", ".join(service_areas)}'
        )
        
        messages.success(request, 'Service area updated successfully!')
        return redirect('ambulance:dashboard')
    
    # Available cities/zones
    available_cities = [
        'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai',
        'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur', 'Surat',
        'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Thane',
        'Bhopal', 'Visakhapatnam', 'Pimpri-Chinchwad', 'Patna', 'Vadodara'
    ]
    
    context = {
        'provider': provider,
        'available_cities': available_cities,
        'current_service_area': provider.get_service_area_list()
    }
    return render(request, 'ambulance/service_area.html', context)


@require_role('ambulance')
def activity_logs(request):
    """View activity logs"""
    user = request.user
    
    # Get logs for this ambulance admin
    logs = ActivityLog.objects.filter(
        user=user
    ).order_by('-timestamp')[:50]
    
    context = {
        'logs': logs
    }
    return render(request, 'ambulance/activity_logs.html', context)


@require_role('ambulance')
def bookings(request):
    """View and manage booking requests"""
    user = request.user
    provider = get_object_or_404(AmbulanceProvider, owner=user)
    
    # Handle booking actions
    if request.method == 'POST':
        action = request.POST.get('action')
        booking_id = request.POST.get('booking_id')
        
        try:
            booking = Booking.objects.get(id=booking_id, provider=provider)
            
            if action == 'accept':
                # Get available ambulance for this provider
                ambulance_id = request.POST.get('ambulance_id')
                if not ambulance_id:
                    messages.error(request, 'Please select an ambulance to assign')
                    return redirect('ambulance:bookings')
                
                try:
                    ambulance = Ambulance.objects.get(id=ambulance_id, provider=provider)
                    if not ambulance.is_available:
                        messages.error(request, 'Selected ambulance is not available. Please select another ambulance.')
                        return redirect('ambulance:bookings')
                    
                    # Check if ambulance has any active bookings (excluding current booking)
                    active_bookings = Booking.objects.filter(
                        ambulance=ambulance,
                        status__in=['pending', 'confirmed', 'in_progress']
                    ).exclude(id=booking.id).exists()
                    
                    if active_bookings:
                        messages.error(request, 'Selected ambulance already has an active booking. Please select another ambulance.')
                        return redirect('ambulance:bookings')
                    
                    # Assign ambulance and update booking status
                    booking.ambulance = ambulance
                    booking.status = 'confirmed'
                    booking.save()
                    
                    # Mark ambulance as unavailable
                    ambulance.is_available = False
                    ambulance.save()
                    
                    log_activity(
                        user.id,
                        'ambulance',
                        'accept_booking',
                        f'Accepted booking #{booking.id} and assigned ambulance {ambulance.vehicle_number}'
                    )
                    
                    messages.success(request, f'Booking #{booking.id} accepted and ambulance {ambulance.vehicle_number} assigned!')
                except Ambulance.DoesNotExist:
                    messages.error(request, 'Selected ambulance not found')
                    return redirect('ambulance:bookings')
                    
            elif action == 'reject':
                booking.status = 'cancelled'
                booking.save()
                
                log_activity(
                    user.id,
                    'ambulance',
                    'reject_booking',
                    f'Rejected booking #{booking.id}'
                )
                
                messages.success(request, f'Booking #{booking.id} rejected')
                
            elif action == 'mark_completed':
                booking.status = 'completed'
                booking.save()
                
                # Mark ambulance as available again
                if booking.ambulance:
                    booking.ambulance.is_available = True
                    booking.ambulance.save()
                
                log_activity(
                    user.id,
                    'ambulance',
                    'complete_booking',
                    f'Marked booking #{booking.id} as completed'
                )
                
                messages.success(request, f'Booking #{booking.id} marked as completed!')
            
            return redirect('ambulance:bookings')
            
        except Booking.DoesNotExist:
            messages.error(request, 'Booking not found')
        except Ambulance.DoesNotExist:
            messages.error(request, 'Ambulance not found')
        except Exception as e:
            messages.error(request, f'Error processing request: {str(e)}')
        
        return redirect('ambulance:bookings')
    
    # Get filter status
    status_filter = request.GET.get('status', 'all')
    
    # Get bookings for this provider
    bookings_query = Booking.objects.filter(provider=provider).select_related('user', 'hospital', 'ambulance')
    
    if status_filter != 'all':
        bookings_query = bookings_query.filter(status=status_filter)
    
    bookings_list = bookings_query.order_by('-created_at')
    
    # Get available ambulances for assignment (exclude those with active bookings)
    active_booking_ambulance_ids = Booking.objects.filter(
        status__in=['pending', 'confirmed', 'in_progress']
    ).exclude(ambulance__isnull=True).values_list('ambulance_id', flat=True)
    
    available_ambulances = provider.ambulances.filter(
        is_available=True
    ).exclude(id__in=active_booking_ambulance_ids)
    
    context = {
        'provider': provider,
        'bookings': bookings_list,
        'status_filter': status_filter,
        'available_ambulances': available_ambulances,
    }
    return render(request, 'ambulance/bookings.html', context)


@require_role('ambulance')
def help_support(request):
    """Help and support page"""
    user = request.user
    provider = get_object_or_404(AmbulanceProvider, owner=user)
    
    context = {
        'provider': provider
    }
    return render(request, 'ambulance/help_support.html', context)


@require_role('ambulance')
def dashboard_stats_api(request):
    """API endpoint for dashboard stats real-time update"""
    user = request.user
    
    # Get provider for this user
    try:
        provider = AmbulanceProvider.objects.get(owner=user)
    except AmbulanceProvider.DoesNotExist:
        return JsonResponse({'error': 'Provider information not found'}, status=404)
    
    # Calculate stats
    ambulances = provider.ambulances.all()
    total_ambulances = ambulances.count()
    available_ambulances = ambulances.filter(is_available=True).count()
    
    # Count by type
    als_count = ambulances.filter(type='ALS').count()
    bls_count = ambulances.filter(type='BLS').count()
    non_emergency_count = ambulances.filter(type='Non-Emergency').count()
    
    data = {
        'total_ambulances': total_ambulances,
        'available_ambulances': available_ambulances,
        'als_count': als_count,
        'bls_count': bls_count,
        'non_emergency_count': non_emergency_count,
        'last_updated': provider.updated_at.strftime("%I:%M %p, %b %d, %Y")
    }
    
    return JsonResponse(data)
