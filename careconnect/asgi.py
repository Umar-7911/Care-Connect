"""
ASGI config for careconnect project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'careconnect.settings')

application = get_asgi_application()
