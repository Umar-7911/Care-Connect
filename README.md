# CareConnect - Healthcare Coordination Platform

<div align="center">

**A web-based healthcare coordination platform that empowers patients and families to make informed decisions about hospital selection and ambulance services during medical emergencies.**

[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-brightgreen.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-Educational-blue.svg)](#license)

</div>

---

## 🌟 Overview

CareConnect bridges the gap between patients and healthcare providers by providing real-time information about hospital bed availability, facilities, pricing, and ambulance services, enabling quick and informed decisions during medical emergencies.

## ✨ Key Features

- 🏥 **Hospital Search & Comparison** - Find and compare hospitals based on location, facilities, and real-time bed availability
- 🚑 **Ambulance Directory** - Browse ambulance services with transparent pricing and service areas
- 📊 **Admin Dashboards** - Separate dashboards for hospital and ambulance administrators
- 💰 **Transparent Pricing** - View detailed pricing for hospital services and ambulance rates
- 🛏️ **Real-time Updates** - Live bed availability and facility information

## 📸 Screenshots

### Landing Page, Sign-In and Sign-Up

````carousel
![CareConnect Landing Page](screenshots/c_landing_page.png)
<!-- slide -->
![Sign Up Page](screenshots/c_signup_page.png)
<!-- slide -->
![Sign In Page](screenshots/c_signin_page.png)
````

### User Dashboard

````carousel
![Hospital Search](screenshots/user_hospital_search.png)
<!-- slide -->
![Hospital Results](screenshots/user_hospital_results.png)
<!-- slide -->
![Hospital Comparison](screenshots/user_hospital_comparison.png)
<!-- slide -->
![Ambulance Directory](screenshots/user_ambulance_directory.png)
````

### Hospital Dashboard

````carousel
![Update Bed Availability](screenshots/hospital_update_beds.png)
<!-- slide -->
![Update Facilities](screenshots/hospital_update_facilities.png)
<!-- slide -->
![Update Insurance](screenshots/hospital_update_insurance.png)
<!-- slide -->
![Update Pricing](screenshots/hospital_update_pricing.png)
````

### Ambulance Dashboard

````carousel
![Dashboard Overview](screenshots/ambulance_dashboard_overview.png)
<!-- slide -->
![Manage Ambulances](screenshots/ambulance_manage_fleet.png)
<!-- slide -->
![Fleet List](screenshots/ambulance_fleet_list.png)
<!-- slide -->
![Service Area](screenshots/ambulance_service_area.png)
<!-- slide -->
![Update Pricing](screenshots/ambulance_update_pricing.png)
````

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Django 4.2.7, Python 3.x
- **Database**: SQLite3
- **Authentication**: Custom role-based authentication

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd careconnect
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables** (if needed)
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open browser: http://localhost:8000

## 👥 User Roles

1. **General Users** - Search hospitals, compare facilities, and find ambulance services
2. **Hospital Admins** - Manage bed availability, facilities, pricing, and insurance providers
3. **Ambulance Providers** - Manage fleet, service areas, and pricing

## 📁 Project Structure

```
careconnect/
├── manage.py
├── careconnect/          # Project settings
├── core/                 # Authentication & landing pages
├── hospital/             # Hospital admin functionality
├── ambulance/            # Ambulance admin functionality
├── userapp/              # User-facing features
└── static/               # CSS, JS, images
```

## 📄 License

This project is developed for **educational purposes**.

---

<div align="center">

**Made with ❤️ for better healthcare coordination**

</div>
