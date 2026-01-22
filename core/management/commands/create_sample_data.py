"""
Django management command to create sample data
Usage: python manage.py create_sample_data
"""
from django.core.management.base import BaseCommand
from core.models import User, Hospital, AmbulanceProvider, Ambulance


class Command(BaseCommand):
    help = 'Creates sample hospitals, ambulances, and admin users'

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating sample data for CareConnect...")

        # Create Hospital Admins
        self.stdout.write("\n1. Creating Hospital Admin Users...")
        
        hospital_admins_data = [
            ('apollo_admin', 'admin@apollohospital.com', '+919876543210', 'apollo123'),
            ('fortis_admin', 'admin@fortishospital.com', '+919876543211', 'fortis123'),
            ('max_admin', 'admin@maxhospital.com', '+919876543212', 'max123'),
        ]
        
        hospital_admins = []
        for username, email, phone, password in hospital_admins_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'phone': phone,
                    'role': 'hospital',
                    'is_active': True
                }
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Created user: {username}'))
            else:
                self.stdout.write(f'- User already exists: {username}')
            hospital_admins.append(user)

        # Create Hospitals
        self.stdout.write("\n2. Creating Hospitals...")
        
        hospitals_data = [
            {
                'name': 'Apollo Hospital',
                'address': 'Kondhwa, Pune',
                'city': 'Pune',
                'type': 'private',
                'email': 'contact@apollohospital.com',
                'phone': '+912067891234',
                'beds_total': 500,
                'beds_icu': 50,
                'beds_oxygen': 100,
                'beds_ventilator': 30,
                'beds_isolation': 80,
                'facilities': 'Emergency, ICU, Cardiology, Neurology, Orthopedics',
                'owner': hospital_admins[0]
            },
            {
                'name': 'Fortis Hospital',
                'address': 'Viman Nagar, Pune',
                'city': 'Pune',
                'type': 'private',
                'email': 'contact@fortishospital.com',
                'phone': '+912067891235',
                'beds_total': 400,
                'beds_icu': 40,
                'beds_oxygen': 80,
                'beds_ventilator': 25,
                'beds_isolation': 60,
                'facilities': 'Emergency, ICU, Oncology, Pediatrics, Maternity',
                'owner': hospital_admins[1]
            },
            {
                'name': 'Max Hospital',
                'address': 'Kharadi, Pune',
                'city': 'Pune',
                'type': 'private',
                'email': 'contact@maxhospital.com',
                'phone': '+912067891236',
                'beds_total': 350,
                'beds_icu': 35,
                'beds_oxygen': 70,
                'beds_ventilator': 20,
                'beds_isolation': 50,
                'facilities': 'Emergency, ICU, Gastroenterology, Nephrology, Urology',
                'owner': hospital_admins[2]
            },
            {
                'name': 'City General Hospital',
                'address': 'Shivaji Nagar, Mumbai',
                'city': 'Mumbai',
                'type': 'government',
                'email': 'contact@citygeneral.gov.in',
                'phone': '+912267891237',
                'beds_total': 600,
                'beds_icu': 60,
                'beds_oxygen': 120,
                'beds_ventilator': 35,
                'beds_isolation': 100,
                'facilities': 'Emergency, ICU, General Medicine, Surgery, Trauma Care',
                'owner': hospital_admins[0]
            },
            {
                'name': 'Lilavati Hospital',
                'address': 'Bandra West, Mumbai',
                'city': 'Mumbai',
                'type': 'private',
                'email': 'contact@lilavatihospital.com',
                'phone': '+912267891238',
                'beds_total': 450,
                'beds_icu': 45,
                'beds_oxygen': 90,
                'beds_ventilator': 28,
                'beds_isolation': 70,
                'facilities': 'Emergency, ICU, Cardiology, Neurosurgery, Oncology',
                'owner': hospital_admins[1]
            }
        ]
        
        for hospital_data in hospitals_data:
            hospital, created = Hospital.objects.get_or_create(
                name=hospital_data['name'],
                defaults=hospital_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created hospital: {hospital.name} in {hospital.city}'))
            else:
                self.stdout.write(f'- Hospital already exists: {hospital.name}')

        # Create Ambulance Admins
        self.stdout.write("\n3. Creating Ambulance Provider Admin Users...")
        
        ambulance_admins_data = [
            ('ziqitza_admin', 'admin@ziqitza.com', '+919876543220', 'ziqitza123'),
            ('redcross_admin', 'admin@redcross.org', '+919876543221', 'redcross123'),
        ]
        
        ambulance_admins = []
        for username, email, phone, password in ambulance_admins_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'phone': phone,
                    'role': 'ambulance',
                    'is_active': True
                }
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Created user: {username}'))
            else:
                self.stdout.write(f'- User already exists: {username}')
            ambulance_admins.append(user)

        # Create Ambulance Providers
        self.stdout.write("\n4. Creating Ambulance Providers...")
        
        providers_data = [
            {
                'name': 'Ziqitza Healthcare',
                'address': 'Wakad, Pune',
                'city': 'Pune',
                'email': 'contact@ziqitza.com',
                'phone': '+912067891240',
                'service_area': 'Pune, Mumbai, Thane',
                'pricing_info': {'basic': 1500, 'advanced': 3000, 'icu': 5000},
                'owner': ambulance_admins[0]
            },
            {
                'name': 'Red Cross Ambulance Service',
                'address': 'Deccan, Pune',
                'city': 'Pune',
                'email': 'contact@redcross.org',
                'phone': '+912067891241',
                'service_area': 'Pune, Pimpri-Chinchwad',
                'pricing_info': {'basic': 1200, 'advanced': 2500, 'icu': 4500},
                'owner': ambulance_admins[1]
            }
        ]
        
        providers = []
        for provider_data in providers_data:
            provider, created = AmbulanceProvider.objects.get_or_create(
                name=provider_data['name'],
                defaults=provider_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created provider: {provider.name}'))
            else:
                self.stdout.write(f'- Provider already exists: {provider.name}')
            providers.append(provider)

        # Create Ambulances
        self.stdout.write("\n5. Creating Ambulances...")
        
        ambulances_data = [
            ('MH12AB1234', 'basic', 'Rajesh Kumar', '+919876000001', 'available', providers[0]),
            ('MH12AB1235', 'advanced', 'Suresh Patil', '+919876000002', 'available', providers[0]),
            ('MH12AB1236', 'icu', 'Amit Sharma', '+919876000003', 'busy', providers[0]),
            ('MH12CD5678', 'basic', 'Prakash Desai', '+919876000004', 'available', providers[1]),
            ('MH12CD5679', 'advanced', 'Vijay Jadhav', '+919876000005', 'available', providers[1]),
            ('MH12CD5680', 'neonatal', 'Santosh More', '+919876000006', 'maintenance', providers[1]),
        ]
        
        for vehicle_number, amb_type, driver_name, driver_phone, status, provider in ambulances_data:
            ambulance, created = Ambulance.objects.get_or_create(
                vehicle_number=vehicle_number,
                defaults={
                    'type': amb_type,
                    'driver_name': driver_name,
                    'driver_phone': driver_phone,
                    'status': status,
                    'provider': provider
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created ambulance: {vehicle_number} ({ambulance.get_type_display()})'))
            else:
                self.stdout.write(f'- Ambulance already exists: {vehicle_number}')

        # Summary
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data creation complete!'))
        self.stdout.write(f'\n📋 Summary:')
        self.stdout.write(f'- Hospitals: {Hospital.objects.count()}')
        self.stdout.write(f'- Ambulance Providers: {AmbulanceProvider.objects.count()}')
        self.stdout.write(f'- Ambulances: {Ambulance.objects.count()}')
        self.stdout.write(f'- Users: {User.objects.count()}')
        
        self.stdout.write(self.style.SUCCESS('\n🔑 Login Credentials:'))
        self.stdout.write('\nHospital Admins:')
        self.stdout.write('- apollo_admin / apollo123')
        self.stdout.write('- fortis_admin / fortis123')
        self.stdout.write('- max_admin / max123')
        self.stdout.write('\nAmbulance Admins:')
        self.stdout.write('- ziqitza_admin / ziqitza123')
        self.stdout.write('- redcross_admin / redcross123')
