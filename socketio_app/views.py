# Create your views here.
import socketio

# create a Socket.IO server
sio = socketio.Server(async_mode='eventlet',
                      # implémente les origines autorisées
                      cors_allowed_origins='*',
                      # décommente pour activer la journalisation
                      engineio_logger=True,
                      logger = True,
                      )


@sio.event
def my_event(sid, message):
    sio.emit('instance states', {'data': message})

