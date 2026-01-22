"""
Hospital Admin App Views
Handles all hospital administrator functionality
Updated to use Django ORM
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from core.views import require_role
from core.models import Hospital, ActivityLog
from django.utils import timezone


@require_role('hospital')
def dashboard(request):
    """Hospital admin dashboard overview"""
    # Get hospital for this user
    try:
        hospital = Hospital.objects.get(owner=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, 'Hospital information not found. Please contact administrator.')
        return redirect('core:login')
    
    # Calculate stats
    context = {
        'hospital': hospital,
        'total_beds': hospital.beds_total,
        'icu_beds': hospital.beds_icu,
        'oxygen_beds': hospital.beds_oxygen,
        'ventilators': hospital.beds_ventilator,
        'isolation_beds': hospital.beds_isolation,
        'last_updated': hospital.updated_at,
    }
    
    return render(request, 'hospital/dashboard.html', context)


@require_role('hospital')
@require_http_methods(["GET", "POST"])
def update_beds(request):
    """Update bed availability"""
    try:
        hospital = Hospital.objects.get(owner=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, 'Hospital not found')
        return redirect('core:login')
    
    if request.method == 'POST':
        # Get form data
        total_beds = int(request.POST.get('total_beds', 0))
        icu_beds = int(request.POST.get('icu_beds', 0))
        oxygen_beds = int(request.POST.get('oxygen_beds', 0))
        ventilators = int(request.POST.get('ventilators', 0))
        isolation_beds = int(request.POST.get('isolation_beds', 0))

        # Total capacity (right column in UI)
        total_beds_capacity = int(request.POST.get('total_beds_capacity', 0) or 0)
        icu_beds_capacity = int(request.POST.get('icu_beds_capacity', 0) or 0)
        oxygen_beds_capacity = int(request.POST.get('oxygen_beds_capacity', 0) or 0)
        ventilators_capacity = int(request.POST.get('ventilators_capacity', 0) or 0)
        isolation_beds_capacity = int(request.POST.get('isolation_beds_capacity', 0) or 0)
        
        # Validate
        if (
            total_beds < 0 or icu_beds < 0 or oxygen_beds < 0 or ventilators < 0 or isolation_beds < 0 or
            total_beds_capacity < 0 or icu_beds_capacity < 0 or oxygen_beds_capacity < 0 or
            ventilators_capacity < 0 or isolation_beds_capacity < 0
        ):
            messages.error(request, 'Bed counts cannot be negative')
            return redirect('hospital:update_beds')

        # Validate availability cannot exceed capacity (when capacity is provided)
        def _validate_capacity(available, capacity, label):
            if capacity > 0 and available > capacity:
                messages.error(request, f'{label} available cannot be greater than total capacity')
                return False
            return True

        if not (
            _validate_capacity(total_beds, total_beds_capacity, 'Total beds') and
            _validate_capacity(icu_beds, icu_beds_capacity, 'ICU beds') and
            _validate_capacity(oxygen_beds, oxygen_beds_capacity, 'Oxygen beds') and
            _validate_capacity(ventilators, ventilators_capacity, 'Ventilators') and
            _validate_capacity(isolation_beds, isolation_beds_capacity, 'Isolation beds')
        ):
            return redirect('hospital:update_beds')
        
        # Update hospital
        hospital.beds_total = total_beds
        hospital.beds_icu = icu_beds
        hospital.beds_oxygen = oxygen_beds
        hospital.beds_ventilator = ventilators
        hospital.beds_isolation = isolation_beds

        hospital.beds_total_capacity = total_beds_capacity
        hospital.beds_icu_capacity = icu_beds_capacity
        hospital.beds_oxygen_capacity = oxygen_beds_capacity
        hospital.beds_ventilator_capacity = ventilators_capacity
        hospital.beds_isolation_capacity = isolation_beds_capacity
        hospital.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            user_role='hospital',
            action='update_beds',
            details=(
                f'Updated bed availability - '
                f'Total: {total_beds}/{total_beds_capacity}, '
                f'ICU: {icu_beds}/{icu_beds_capacity}, '
                f'Oxygen: {oxygen_beds}/{oxygen_beds_capacity}, '
                f'Ventilators: {ventilators}/{ventilators_capacity}, '
                f'Isolation: {isolation_beds}/{isolation_beds_capacity}'
            )
        )
        
        messages.success(request, 'Bed availability updated successfully!')
        return redirect('hospital:dashboard')
    
    context = {
        'hospital': hospital,
        'beds': {
            'total': hospital.beds_total,
            'icu': hospital.beds_icu,
            'oxygen': hospital.beds_oxygen,
            'ventilator': hospital.beds_ventilator,
            'isolation': hospital.beds_isolation,
            'total_capacity': hospital.beds_total_capacity,
            'icu_capacity': hospital.beds_icu_capacity,
            'oxygen_capacity': hospital.beds_oxygen_capacity,
            'ventilator_capacity': hospital.beds_ventilator_capacity,
            'isolation_capacity': hospital.beds_isolation_capacity,
        }
    }
    return render(request, 'hospital/update_beds.html', context)


@require_role('hospital')
@require_http_methods(["GET", "POST"])
def update_facilities(request):
    """Update hospital facilities"""
    try:
        hospital = Hospital.objects.get(owner=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, 'Hospital not found')
        return redirect('core:login')
    
    # Available facilities
    available_facilities = [
        {'id': 'icu', 'name': 'ICU (Intensive Care Unit)', 'desc': 'Critical care unit'},
        {'id': 'nicu', 'name': 'NICU (Neonatal ICU)', 'desc': 'Newborn intensive care'},
        {'id': 'emergency', 'name': 'Emergency Ward', 'desc': '24/7 emergency services'},
        {'id': 'operation_theatre', 'name': 'Operation Theatre', 'desc': 'Surgical facilities'},
        {'id': 'diagnostic_lab', 'name': 'Diagnostic Lab', 'desc': 'Blood tests, pathology'},
        {'id': 'radiology', 'name': 'Radiology (X-Ray)', 'desc': 'X-ray imaging'},
        {'id': 'ct_scan', 'name': 'CT Scan', 'desc': 'CT imaging'},
        {'id': 'mri', 'name': 'MRI', 'desc': 'MRI imaging'},
        {'id': 'pharmacy', 'name': 'Pharmacy', 'desc': '24/7 pharmacy'},
        {'id': 'blood_bank', 'name': 'Blood Bank', 'desc': 'Blood storage and transfusion'},
        {'id': 'ambulance', 'name': 'Ambulance Service', 'desc': 'Emergency transport'},
        {'id': 'cafeteria', 'name': 'Cafeteria', 'desc': 'Food services'},
    ]
    
    if request.method == 'POST':
        # Get selected facilities
        selected_facilities = []
        for facility in available_facilities:
            if request.POST.get(facility['id']):
                selected_facilities.append(facility['name'])
        
        # Update hospital
        hospital.set_facilities_list(selected_facilities)
        hospital.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            user_role='hospital',
            action='update_facilities',
            details=f'Updated facilities: {", ".join(selected_facilities)}'
        )
        
        messages.success(request, 'Facilities updated successfully!')
        return redirect('hospital:dashboard')
    
    context = {
        'hospital': hospital,
        'available_facilities': available_facilities,
        'current_facilities': hospital.get_facilities_list()
    }
    return render(request, 'hospital/update_facilities.html', context)


@require_role('hospital')
@require_http_methods(["GET", "POST"])
def update_pricing(request):
    """Update hospital pricing"""
    try:
        hospital = Hospital.objects.get(owner=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, 'Hospital not found')
        return redirect('core:login')
    
    if request.method == 'POST':
        # Get form data
        general_bed = float(request.POST.get('general_bed', 0))
        icu_bed = float(request.POST.get('icu_bed', 0))
        oxygen_bed = float(request.POST.get('oxygen_bed', 0))
        ventilator = float(request.POST.get('ventilator', 0))
        isolation_bed = float(request.POST.get('isolation_bed', 0))
        
        # Validate
        if general_bed < 0 or icu_bed < 0 or oxygen_bed < 0 or ventilator < 0 or isolation_bed < 0:
            messages.error(request, 'Prices cannot be negative')
            return redirect('hospital:update_pricing')
        
        # Update pricing
        hospital.pricing_info = {
            'general_bed': general_bed,
            'icu_bed': icu_bed,
            'oxygen_bed': oxygen_bed,
            'ventilator': ventilator,
            'isolation_bed': isolation_bed
        }
        hospital.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            user_role='hospital',
            action='update_pricing',
            details=f'Updated pricing - General: ₹{general_bed}, ICU: ₹{icu_bed}, Oxygen: ₹{oxygen_bed}, Ventilator: ₹{ventilator}, Isolation: ₹{isolation_bed}'
        )
        
        messages.success(request, 'Pricing updated successfully!')
        return redirect('hospital:dashboard')
    
    context = {
        'hospital': hospital,
        'pricing': hospital.pricing_info
    }
    return render(request, 'hospital/update_pricing.html', context)


@require_role('hospital')
@require_http_methods(["GET", "POST"])
def update_insurances(request):
    """Update accepted insurance providers"""
    try:
        hospital = Hospital.objects.get(owner=request.user)
    except Hospital.DoesNotExist:
        messages.error(request, 'Hospital not found')
        return redirect('core:login')
    
    # Common insurance providers in India
    available_insurances = [
        {'id': 'star_health', 'name': 'Star Health Insurance'},
        {'id': 'icici_lombard', 'name': 'ICICI Lombard'},
        {'id': 'hdfc_ergo', 'name': 'HDFC ERGO'},
        {'id': 'bajaj_allianz', 'name': 'Bajaj Allianz'},
        {'id': 'max_bupa', 'name': 'Max Bupa'},
        {'id': 'apollo_munich', 'name': 'Apollo Munich'},
        {'id': 'reliance_health', 'name': 'Reliance Health Insurance'},
        {'id': 'care_health', 'name': 'Care Health Insurance'},
        {'id': 'niva_bupa', 'name': 'Niva Bupa'},
        {'id': 'tata_aig', 'name': 'Tata AIG'},
        {'id': 'united_india', 'name': 'United India Insurance'},
        {'id': 'national_insurance', 'name': 'National Insurance'},
        {'id': 'new_india', 'name': 'New India Assurance'},
        {'id': 'oriental_insurance', 'name': 'Oriental Insurance'},
        {'id': 'cghs', 'name': 'CGHS (Central Government Health Scheme)'},
        {'id': 'esic', 'name': 'ESIC (Employees State Insurance)'},
    ]
    
    if request.method == 'POST':
        # Get selected insurance providers
        selected_insurances = []
        for insurance in available_insurances:
            if request.POST.get(insurance['id']):
                selected_insurances.append(insurance['name'])
        
        # Update hospital
        hospital.insurance_providers = {'accepted': selected_insurances}
        hospital.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            user_role='hospital',
            action='update_insurances',
            details=f'Updated insurance providers: {", ".join(selected_insurances) if selected_insurances else "None"}'
        )
        
        messages.success(request, 'Insurance providers updated successfully!')
        return redirect('hospital:dashboard')
    
    # Get currently accepted insurances
    current_insurances = hospital.insurance_providers.get('accepted', []) if hospital.insurance_providers else []
    
    context = {
        'hospital': hospital,
        'available_insurances': available_insurances,
        'current_insurances': current_insurances
    }
    return render(request, 'hospital/update_insurances.html', context)


@require_role('hospital')
def activity_logs(request):
    """View activity logs"""
    # Get logs for this user
    logs = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')[:50]
    
    context = {
        'logs': logs
    }
    return render(request, 'hospital/activity_logs.html', context)


@require_role('hospital')
def help_support(request):
    """Help and support page"""
    try:
        hospital = Hospital.objects.get(owner=request.user)
    except Hospital.DoesNotExist:
        hospital = None
    
    context = {
        'hospital': hospital
    }
    return render(request, 'hospital/help_support.html', context)
