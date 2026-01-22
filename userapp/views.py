"""
User App Views
Handles general user functionality - hospital search, comparison, ambulance directory
Updated to use Django ORM instead of MongoDB
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from core.views import require_login
from core.models import Hospital, AmbulanceProvider, Ambulance, Booking
from django.db.models import Q
from datetime import datetime, timedelta
from django.http import JsonResponse


@require_login
def home(request):
    """User home page with enhanced search"""
    # Check if user has 'user' role (general user)
    if request.user.role != 'user':
        messages.error(request, 'Access denied. This page is for general users only.')
        return redirect('core:landing')
    
    # Get all cities for dropdown
    cities = Hospital.objects.values_list('city', flat=True).distinct().order_by('city')
    
    context = {
        'cities': list(cities),
        'username': request.user.email or request.user.username
    }
    return render(request, 'userapp/home.html', context)


def _get_status(available, total):
    """Helper function to determine availability status"""
    if total == 0:
        return 'none'
    percentage = (available / total) * 100
    if percentage >= 50:
        return 'good'
    elif percentage >= 20:
        return 'limited'
    elif percentage > 0:
        return 'very_limited'
    else:
        return 'full'


@require_login
def search_hospitals(request):
    """Search hospitals with advanced filters"""
    # Get search parameters
    search_type = request.GET.get('search_type', 'location')
    hospital_name = request.GET.get('hospital_name', '').strip()
    location = request.GET.get('location', '').strip()
    hospital_type = request.GET.get('hospital_type', 'all')
    facilities = request.GET.getlist('facility')  # Multiple facilities
    
    # Build query
    query = Q()
    
    # Search by hospital name OR location/filters
    if search_type == 'name' and hospital_name:
        # Search by hospital name only
        query &= Q(name__icontains=hospital_name)
    else:
        # Search by location and filters
        if location:
            query &= (
                Q(city__icontains=location) |
                Q(address__icontains=location) |
                Q(name__icontains=location)
            )
        
        # Hospital type filter
        if hospital_type and hospital_type != 'all':
            query &= Q(type=hospital_type)
    
    # Get hospitals from database
    hospitals = Hospital.objects.filter(query).select_related('owner')
    
    # Filter by facilities if specified (only for location-based search)
    if facilities and search_type != 'name':
        for facility in facilities:
            if facility == 'icu':
                hospitals = hospitals.filter(beds_icu__gt=0)
            elif facility == 'oxygen':
                hospitals = hospitals.filter(beds_oxygen__gt=0)
            elif facility == 'ventilator':
                hospitals = hospitals.filter(beds_ventilator__gt=0)
            elif facility == 'isolation':
                hospitals = hospitals.filter(beds_isolation__gt=0)
    
    # Convert to list and add computed fields
    hospitals_list = []
    for hospital in hospitals:
        # Use the exact values stored in the Hospital model for both
        # "available" and "total" counts so the user dashboard always
        # reflects real-time data entered by hospital admins / Django admin.
        # Denominators come from stored capacity fields (right column in hospital dashboard)
        # Fallback to available if capacity isn't set yet.
        icu_total = hospital.beds_icu_capacity or hospital.beds_icu
        oxygen_total = hospital.beds_oxygen_capacity or hospital.beds_oxygen
        ventilator_total = hospital.beds_ventilator_capacity or hospital.beds_ventilator
        isolation_total = hospital.beds_isolation_capacity or hospital.beds_isolation
        
        # Add facility availability details with capacity
        hospital_dict = {
            'id': hospital.id,
            'id_str': str(hospital.id),
            'name': hospital.name,
            'address': hospital.address,
            'city': hospital.city,
            'type': hospital.type,
            'email': hospital.email,
            'phone': hospital.phone,
            'facilities_detail': {
                'icu': {
                    'available': hospital.beds_icu,
                    'total': icu_total,
                    'status': _get_status(hospital.beds_icu, icu_total)
                },
                'oxygen': {
                    'available': hospital.beds_oxygen,
                    'total': oxygen_total,
                    'status': _get_status(hospital.beds_oxygen, oxygen_total)
                },
                'ventilator': {
                    'available': hospital.beds_ventilator,
                    'total': ventilator_total,
                    'status': _get_status(hospital.beds_ventilator, ventilator_total)
                },
                'isolation': {
                    'available': hospital.beds_isolation,
                    'total': isolation_total,
                    'status': _get_status(hospital.beds_isolation, isolation_total)
                }
            }
        }
        
        # Calculate last updated time
        updated_at = hospital.updated_at
        if updated_at:
            time_diff = datetime.now(updated_at.tzinfo) - updated_at
            if time_diff < timedelta(minutes=1):
                hospital_dict['last_updated'] = "just now"
            elif time_diff < timedelta(hours=1):
                minutes = int(time_diff.total_seconds() / 60)
                hospital_dict['last_updated'] = f"{minutes} minutes ago" if minutes > 1 else "1 minute ago"
            elif time_diff < timedelta(days=1):
                hours = int(time_diff.total_seconds() / 3600)
                hospital_dict['last_updated'] = f"{hours} hour{'s' if hours > 1 else ''} ago"
            else:
                days = time_diff.days
                hospital_dict['last_updated'] = f"{days} day{'s' if days > 1 else ''} ago"
        else:
            hospital_dict['last_updated'] = "just now"
        
        # Mock distance (in real app, would calculate based on user location)
        hospital_dict['distance'] = round(2.0 + (hash(str(hospital.id)) % 50) / 10, 1)
        
        # Add coordinates if available, otherwise use city-based defaults
        if hospital.latitude and hospital.longitude:
            hospital_dict['latitude'] = float(hospital.latitude)
            hospital_dict['longitude'] = float(hospital.longitude)
        else:
            # Generate approximate coordinates based on city (fallback)
            # This is a simple hash-based approach for demo - in production, use proper geocoding
            city_hash = hash(hospital.city) % 1000
            # Default to Mumbai area coordinates if no city match
            hospital_dict['latitude'] = 19.0760 + (city_hash / 10000.0)
            hospital_dict['longitude'] = 72.8777 + (city_hash / 10000.0)
        
        hospitals_list.append(hospital_dict)
    
    # Sort by distance (closest first) or name (for name search)
    if search_type == 'name':
        hospitals_list.sort(key=lambda h: h.get('name', ''))
    else:
        hospitals_list.sort(key=lambda h: h.get('distance', 999))
    
    context = {
        'hospitals': hospitals_list,
        'search_type': search_type,
        'search_hospital_name': hospital_name,
        'search_location': location,
        'search_hospital_type': hospital_type,
        'search_facilities': facilities,
        'total_results': len(hospitals_list),
        'username': request.user.email or request.user.username
    }
    return render(request, 'userapp/results.html', context)


@require_login
def results(request):
    """Results page - shows all hospitals or uses search parameters"""
    # Check if there are search parameters, if not show all hospitals
    search_type = request.GET.get('search_type', 'location')
    hospital_name = request.GET.get('hospital_name', '').strip()
    location = request.GET.get('location', '').strip()
    hospital_type = request.GET.get('hospital_type', 'all')
    facilities = request.GET.getlist('facility')
    
    # If no search params, show all hospitals
    if search_type == 'name' and not hospital_name:
        if not location and hospital_type == 'all' and not facilities:
            # Show all hospitals without filters
            search_type = 'location'
            location = ''
            hospital_type = 'all'
            facilities = []
    elif search_type == 'location' and not location:
        if hospital_type == 'all' and not facilities:
            # Show all hospitals without filters
            location = ''
            hospital_type = 'all'
            facilities = []
    
    # Use the same logic as search_hospitals
    return search_hospitals(request)


@require_login
def compare_hospitals(request):
    """Compare multiple hospitals"""
    # Get hospital IDs from query string
    ids_param = request.GET.get('ids', '')
    
    if not ids_param:
        messages.info(request, 'Please select hospitals to compare')
        return redirect('userapp:home')
    
    # Split comma-separated IDs
    hospital_ids = [hid.strip() for hid in ids_param.split(',') if hid.strip()]
    
    # Limit to 4 hospitals
    hospital_ids = hospital_ids[:4]
    
    # If only 1 hospital, redirect to ambulance booking
    if len(hospital_ids) == 1:
        return redirect(f'{reverse("userapp:ambulances")}?hospital_id={hospital_ids[0]}')
    
    # Get hospitals from database
    hospitals_list = []
    for hid in hospital_ids:
        try:
            hospital = Hospital.objects.get(id=int(hid.strip()))
            
            # Use exact values stored in the Hospital model so comparison
            # view matches hospital admin dashboard and Django admin.
            icu_total = hospital.beds_icu_capacity or hospital.beds_icu
            oxygen_total = hospital.beds_oxygen_capacity or hospital.beds_oxygen
            ventilator_total = hospital.beds_ventilator_capacity or hospital.beds_ventilator
            isolation_total = hospital.beds_isolation_capacity or hospital.beds_isolation
            
            # Calculate last updated time
            updated_at = hospital.updated_at
            if updated_at:
                time_diff = datetime.now(updated_at.tzinfo) - updated_at
                if time_diff < timedelta(minutes=1):
                    last_updated = "just now"
                elif time_diff < timedelta(hours=1):
                    minutes = int(time_diff.total_seconds() / 60)
                    last_updated = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
                elif time_diff < timedelta(days=1):
                    hours = int(time_diff.total_seconds() / 3600)
                    last_updated = f"{hours} hour{'s' if hours > 1 else ''} ago"
                else:
                    days = time_diff.days
                    last_updated = f"{days} day{'s' if days > 1 else ''} ago"
            else:
                last_updated = "recently"
            
            # Mock distance (in real app, would calculate based on user location)
            distance = round(2.0 + (hash(str(hospital.id)) % 50) / 10, 1)
            
            # Calculate availability percentages for status determination
            icu_percentage = (hospital.beds_icu / icu_total * 100) if icu_total > 0 else 0
            oxygen_percentage = (hospital.beds_oxygen / oxygen_total * 100) if oxygen_total > 0 else 0
            ventilator_percentage = (hospital.beds_ventilator / ventilator_total * 100) if ventilator_total > 0 else 0
            isolation_percentage = (hospital.beds_isolation / isolation_total * 100) if isolation_total > 0 else 0
            
            # Add facility details with real-time bed data
            hospital_dict = {
                'id': hospital.id,
                'name': hospital.name,
                'address': hospital.address,
                'city': hospital.city,
                'type': hospital.type,
                'email': hospital.email,
                'phone': hospital.phone,
                'distance': distance,
                'updated_at': last_updated,
                'beds': {
                    'icu': hospital.beds_icu,
                    'icu_total': icu_total,
                    'icu_percentage': icu_percentage,
                    'oxygen': hospital.beds_oxygen,
                    'oxygen_total': oxygen_total,
                    'oxygen_percentage': oxygen_percentage,
                    'ventilator': hospital.beds_ventilator,
                    'ventilator_total': ventilator_total,
                    'ventilator_percentage': ventilator_percentage,
                    'isolation': hospital.beds_isolation,
                    'isolation_total': isolation_total,
                    'isolation_percentage': isolation_percentage,
                },
                'facilities_detail': {
                    'icu': {
                        'available': hospital.beds_icu > 0,
                        'count': hospital.beds_icu
                    },
                    'oxygen': {
                        'available': hospital.beds_oxygen > 0,
                        'count': hospital.beds_oxygen
                    },
                    'ventilator': {
                        'available': hospital.beds_ventilator > 0,
                        'count': hospital.beds_ventilator
                    },
                    'isolation': {
                        'available': hospital.beds_isolation > 0,
                        'count': hospital.beds_isolation
                    }
                },
                'pricing': hospital.pricing_info if hospital.pricing_info else {},
                'insurance_providers': {
                    'accepted': hospital.insurance_providers.get('accepted', []) if hospital.insurance_providers else []
                }
            }
            hospitals_list.append(hospital_dict)
        except (Hospital.DoesNotExist, ValueError) as e:
            print(f"Error fetching hospital {hid}: {e}")
            continue
    
    if not hospitals_list:
        messages.error(request, 'No hospitals found for comparison')
        return redirect('userapp:home')
    
    context = {
        'hospitals': hospitals_list,
        'username': request.user.email or request.user.username
    }
    return render(request, 'userapp/compare.html', context)


@require_login
def ambulances(request):
    """Ambulance directory and booking"""
    city = request.GET.get('city', '')
    ambulance_type = request.GET.get('type', '')
    hospital_id = request.GET.get('hospital_id', '')
    
    # Get selected hospital if hospital_id is provided
    selected_hospital = None
    if hospital_id:
        try:
            selected_hospital = Hospital.objects.get(id=int(hospital_id))
        except (Hospital.DoesNotExist, ValueError):
            pass
    
    # Get all providers with prefetch
    providers_queryset = AmbulanceProvider.objects.prefetch_related('ambulances').all()
    
    # Get ambulances with active bookings (not completed or cancelled)
    active_booking_ambulance_ids = Booking.objects.filter(
        status__in=['pending', 'confirmed', 'in_progress']
    ).exclude(ambulance__isnull=True).values_list('ambulance_id', flat=True)
    
    # Filter by city - check if city is in service_area_list (exact match)
    # If hospital is selected, use hospital's city
    if selected_hospital and not city:
        city = selected_hospital.city.strip()
    
    providers_list = []
    for provider in providers_queryset:
        service_cities = [c.lower() for c in provider.get_service_area_list()]
        # If city filter is specified, check if it's in the service area
        if city:
            if city.lower() in service_cities:
                providers_list.append(provider)
        else:
            # No city filter, include all providers
            providers_list.append(provider)
    
    # Filter by ambulance type if specified and filter out ambulances with active bookings
    if ambulance_type:
        filtered_providers = []
        for provider in providers_list:
            # Check if provider has at least one available ambulance of the specified type
            # that doesn't have an active booking
            available_ambulances = provider.ambulances.filter(
                type=ambulance_type,
                is_available=True
            ).exclude(id__in=active_booking_ambulance_ids)
            if available_ambulances.exists():
                filtered_providers.append(provider)
        providers_list = filtered_providers
    else:
        # Filter providers to only show those with available ambulances (no active bookings)
        filtered_providers = []
        for provider in providers_list:
            available_ambulances = provider.ambulances.filter(
                is_available=True
            ).exclude(id__in=active_booking_ambulance_ids)
            if available_ambulances.exists():
                filtered_providers.append(provider)
        providers_list = filtered_providers
    
    # Get all cities for filter
    all_cities = set()
    for provider in AmbulanceProvider.objects.all():
        all_cities.update(provider.get_service_area_list())
    cities = sorted(list(all_cities))
    
    context = {
        'providers': providers_list,
        'cities': cities,
        'search_city': city,
        'search_type': ambulance_type,
        'total_results': len(providers_list),
        'username': request.user.email or request.user.username,
        'selected_hospital': selected_hospital,
        'active_booking_ambulance_ids': list(active_booking_ambulance_ids)
    }
    return render(request, 'userapp/ambulances.html', context)


@require_login
def live_hospital_availability(request):
    """
    Lightweight polling endpoint for user dashboard to fetch latest bed availability.
    Returns only the fields needed to update the UI in near real-time.
    """
    ids_param = request.GET.get('ids', '').strip()
    ids = []
    if ids_param:
        try:
            ids = [int(x) for x in ids_param.split(',') if x.strip().isdigit()]
        except Exception:
            ids = []

    qs = Hospital.objects.all()
    if ids:
        qs = qs.filter(id__in=ids)

    payload = []
    for h in qs:
        icu_total = h.beds_icu_capacity or h.beds_icu
        oxygen_total = h.beds_oxygen_capacity or h.beds_oxygen
        ventilator_total = h.beds_ventilator_capacity or h.beds_ventilator
        isolation_total = h.beds_isolation_capacity or h.beds_isolation

        payload.append({
            'id': str(h.id),
            'beds': {
                'icu': {'available': h.beds_icu, 'total': icu_total, 'status': _get_status(h.beds_icu, icu_total)},
                'oxygen': {'available': h.beds_oxygen, 'total': oxygen_total, 'status': _get_status(h.beds_oxygen, oxygen_total)},
                'ventilator': {'available': h.beds_ventilator, 'total': ventilator_total, 'status': _get_status(h.beds_ventilator, ventilator_total)},
                'isolation': {'available': h.beds_isolation, 'total': isolation_total, 'status': _get_status(h.beds_isolation, isolation_total)},
            },
            'updated_at': h.updated_at.isoformat() if h.updated_at else None,
        })

    return JsonResponse({'hospitals': payload})


@require_login
def book_ambulance(request):
    """Book ambulance service"""
    if request.method == 'POST':
        hospital_id = request.POST.get('hospital_id')
        provider_id = request.POST.get('provider_id')
        ambulance_id = request.POST.get('ambulance_id')
        
        # Extract all form fields from POST data
        pickup_location = request.POST.get('pickup_location', '').strip()
        drop_location = request.POST.get('drop_location', '').strip()
        pickup_date = request.POST.get('pickup_date', '').strip()
        pickup_time = request.POST.get('pickup_time', '').strip()
        patient_name = request.POST.get('patient_name', '').strip()
        patient_phone = request.POST.get('patient_phone', '').strip()
        contact_person = request.POST.get('contact_person', '').strip()
        contact_phone = request.POST.get('contact_phone', '').strip()
        emergency_type = request.POST.get('emergency_type', '').strip()
        notes = request.POST.get('notes', '').strip()
        
        # Validate required fields
        if not all([hospital_id, provider_id, pickup_location, pickup_date, pickup_time, patient_name, patient_phone]):
            messages.error(request, 'Please fill all required fields')
            if hospital_id:
                return redirect(f'{reverse("userapp:ambulances")}?hospital_id={hospital_id}')
            return redirect('userapp:ambulances')
        
        try:
            hospital = Hospital.objects.get(id=int(hospital_id))
            provider = AmbulanceProvider.objects.get(id=int(provider_id))
            
            # Get ambulance if provided
            ambulance = None
            if ambulance_id:
                try:
                    ambulance = Ambulance.objects.get(id=int(ambulance_id))
                except (ValueError, Ambulance.DoesNotExist):
                    pass
            
            # Use hospital address as drop location if not provided
            if not drop_location:
                drop_location = f"{hospital.name}, {hospital.address}, {hospital.city}"
            
            # Parse date and time
            from datetime import datetime
            pickup_datetime = datetime.strptime(f"{pickup_date} {pickup_time}", "%Y-%m-%d %H:%M")
            
            # Create booking record
            booking = Booking.objects.create(
                user=request.user,
                provider=provider,
                hospital=hospital,
                ambulance=ambulance,  # Save the selected ambulance
                patient_name=patient_name,
                patient_phone=patient_phone,
                contact_person=contact_person or patient_name,
                contact_phone=contact_phone or patient_phone,
                pickup_location=pickup_location,
                drop_location=drop_location,
                pickup_date=pickup_date,
                pickup_time=pickup_time,
                emergency_type=emergency_type,
                notes=notes,
                status='pending'
            )
            
            messages.success(request, f'Ambulance booking request submitted successfully! Booking ID: #{booking.id}. Provider: {provider.name} will contact you at {patient_phone}.')
            
            # Log the booking
            from core.models import ActivityLog
            ActivityLog.objects.create(
                user=request.user,
                user_role='user',
                action='book_ambulance',
                details=f'Booked ambulance from {provider.name} to {hospital.name}. Pickup: {pickup_location} on {pickup_date} at {pickup_time}. Patient: {patient_name}'
            )
            
            return redirect(f'{reverse("userapp:ambulances")}?hospital_id={hospital_id}')
        except (Hospital.DoesNotExist, AmbulanceProvider.DoesNotExist, ValueError) as e:
            messages.error(request, 'Invalid hospital or provider selected')
            return redirect('userapp:ambulances')
        except Exception as e:
            messages.error(request, f'Error creating booking: {str(e)}')
            if hospital_id:
                return redirect(f'{reverse("userapp:ambulances")}?hospital_id={hospital_id}')
            return redirect('userapp:ambulances')
    
    return redirect('userapp:ambulances')
