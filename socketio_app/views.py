from django.shortcuts import render

# Create your views here.
import socketio

# create a Socket.IO server
sio = socketio.Server(async_mode='threading',
                      # implémente les origines autorisées
                      cors_allowed_origins='*',
                      # décommente pour activer la journalisation
                      engineio_logger=True,
                      logger=True,
                      )


@sio.on('connect')
def connect(sid, environ):
    print('Le serveur est connecté ', sid)
