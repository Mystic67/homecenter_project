"""
WSGI config for homecenter_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
import socketio

from socketio_app.views import sio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homecenter_project.settings')

django_app = get_wsgi_application()
application = socketio.WSGIApp(sio, django_app)

#application = get_wsgi_application()
