import os
from django.core.management.commands.runserver import Command as RunCommand

from socketio_app.views import sio


class Command(RunCommand):
    help = 'Run the Socket.IO server'

    def handle(self, *args, **options):
        if sio.async_mode == 'threading':
            super(Command, self).handle(*args, **options)
        elif sio.async_mode == 'eventlet':
            import eventlet
            import eventlet.wsgi
            from homecenter_project.wsgi import application
            eventlet.wsgi.server(eventlet.listen(('', 8001)), application)
