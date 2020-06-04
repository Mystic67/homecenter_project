import os
import sys
import logging
import threading
from logging import NullHandler
from threading import Thread
from pydispatch import dispatcher
from openzwave.network import ZWaveNetwork
from openzwave.controller import ZWaveController
from .db import update_instance_state

logging.getLogger('openzwave').addHandler(NullHandler())

listener = None


class ListenerThread(Thread):
    """ The listener Tread
    """
    def __init__(self, _socketio, _app):
        """The constructor"""
        Thread.__init__(self)
        self._stopevent = threading.Event()
        self.connected = False
        self.socketio = _socketio
        self.app = _app

    def connect(self):
        """Connect to the zwave notifications
        """
        if not self.connected:
            self.join_room_network()
            self.join_room_controller()
            self.join_room_node()
            self.join_room_values()
            self.connected = True
            logging.info("L'écouteur d'évênement est connecté")

    def run(self):
        """The running method
        """
        logging.info("Démarrage de l'écouteur d'évênements")
        self._stopevent.wait(5.0)
        self.connect()
        while not self._stopevent.isSet():
            self._stopevent.wait(0.1)

    def join_room_network(self):
        """Join room network
        """
        dispatcher.connect(self._dispatch_network,
                           ZWaveNetwork.SIGNAL_NETWORK_STARTED)
        dispatcher.connect(self._dispatch_network,
                           ZWaveNetwork.SIGNAL_NETWORK_RESETTED)
        dispatcher.connect(self._dispatch_network,
                           ZWaveNetwork.SIGNAL_NETWORK_AWAKED)
        dispatcher.connect(self._dispatch_network,
                           ZWaveNetwork.SIGNAL_NETWORK_READY)
        dispatcher.connect(self._dispatch_network,
                           ZWaveNetwork.SIGNAL_NETWORK_STOPPED)
        return True

    def leave_room_network(self):
        """Leave room network
        """
        dispatcher.disconnect(self._dispatch_network,
                              ZWaveNetwork.SIGNAL_NETWORK_STARTED)
        dispatcher.disconnect(self._dispatch_network,
                              ZWaveNetwork.SIGNAL_NETWORK_RESETTED)
        dispatcher.disconnect(self._dispatch_network,
                              ZWaveNetwork.SIGNAL_NETWORK_AWAKED)
        dispatcher.disconnect(self._dispatch_network,
                              ZWaveNetwork.SIGNAL_NETWORK_READY)
        dispatcher.disconnect(self._dispatch_network,
                              ZWaveNetwork.SIGNAL_NETWORK_STOPPED)
        return True

    def _dispatch_network(self, network):
        """dispatch for netowrk
        """
        logging.debug('Notification du réseau OpenZWave : '
                      'homeid %0.8x (state:%s) - %d noeuds trouvés.' % (
                          network.home_id, network.state, network.nodes_count))
        data = {'data': network.to_dict()}
        self.socketio.emit('network data', data)  # , namespace='/network')

    def join_room_node(self):
        """Join room nodes
        """
        dispatcher.connect(self._dispatch_node, ZWaveNetwork.SIGNAL_NODE)
        return True

    def leave_room_node(self):
        """Leave room nodes
        """
        dispatcher.disconnect(self._dispatch_node, ZWaveNetwork.SIGNAL_NODE)
        return True

    def _dispatch_node(self, network, node):
        """dispatch for node
        """
        data = node.to_dict()
        logging.debug('Notification de noeuds OpenZWave : noeud %s.', data)

    def join_room_values(self):
        """Join room values
        """
        dispatcher.connect(self._dispatch_values, ZWaveNetwork.SIGNAL_VALUE)
        return True

    def leave_room_values(self):
        """Leave room values
        """
        dispatcher.disconnect(self._dispatch_values, ZWaveNetwork.SIGNAL_VALUE)
        return True

    def _dispatch_values(self, network, node, value):
        """dispatch dispatch for values
        """
        if network is None:
            logging.debug('Notification des valeurs OpenZWave : Pas de réseau.')
        elif node is None:
            logging.debug('Notification des valeurs OpenZWave : '
                          'Aucun noeud trouvé.')
        elif value is None:
            logging.debug('Notification des valeurs OpenZWave : '
                          'Pas de retour de valeurs.')
        else:
            logging.debug('Notification des valeurs OpenZWave : '
                          'homeid %0.8x - noeud %d - valeur %d.',
                          network.home_id, node.node_id, value.value_id)
            if network.is_ready:
                logging.info("la valeur '{}' renvoyée par l'instance '{}' du "
                             "noeud '{}' est: {}".format(value.label,
                                                         value.instance,
                                                         value.value_id,
                                                         value.data))
                update_instance_state(value.value_id, value)

                data = \
                    network.nodes[node.node_id].values[value.value_id].to_dict()
                data["value_id"] = str(value.value_id)
                if data['label'] == 'Switch':
                    self.socketio.emit("update light state", {"data": data})

                elif data['label'] == 'Level':
                    self.socketio.emit("update roller shutter state",
                                       {"data": data})

                elif data['label'] == 'Power':
                    self.socketio.emit("update roller shutter power state",
                                       {"data": data})

    def join_room_controller(self):
        """Join room controller
        """
        dispatcher.connect(self._dispatch_controller,
                           ZWaveController.SIGNAL_CTRL_WAITING)
        dispatcher.connect(self._dispatch_controller,
                           ZWaveController.SIGNAL_CONTROLLER)
        return True

    def leave_room_controller(self):
        """Leave room controller
        """
        dispatcher.disconnect(self._dispatch_controller,
                              ZWaveController.SIGNAL_CTRL_WAITING)
        dispatcher.disconnect(self._dispatch_controller,
                              ZWaveController.SIGNAL_CONTROLLER)
        return True

    def _dispatch_controller(self, state, message, network, controller):
        """dispatch for controller
        """
        if network is None or controller is None:
            logging.debug('Message du contrôleur OpenZWave : '
                          'Aucun réseau ou de contrôleur détecté.')
        else:
            logging.debug('Message du contrôleur OpenZWave : '
                          'état %s - message %s.', state, message)

    def stop(self):
        """Stop the tread
        """
        self.leave_room_node()
        self.leave_room_values()
        self.leave_room_controller()
        self.leave_room_network()
        self._stopevent.set()
        logging.info("Arrêt de l'écouteur d'évênement")


def start_listener(socketio_, app_):
    """Start the listener
    """
    global listener
    if listener is None:
        listener = ListenerThread(socketio_, app_)
        # listener = ListenerThread()
        listener.start()
    return listener


def stop_listener():
    """Stop the listener
    """
    global listener
    listener.stop()
    listener = None
