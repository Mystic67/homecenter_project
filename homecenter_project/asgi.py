"""
ASGI config for untitled project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
import socketio
from django.core.asgi import get_asgi_application

from socketio_app.views import sio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homecenter_project.settings')

django_app = get_asgi_application()
application = socketio.ASGIApp(sio, django_app)
#application = get_asgi_application()
