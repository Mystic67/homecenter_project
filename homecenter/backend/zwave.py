# set async_mode to 'threading', 'eventlet', 'gevent' or 'gevent_uwsgi' to
# force a mode else, the best mode is selected automatically from what's
# installed
async_mode = None

import sys
import time
import logging

from django.conf import settings
from openzwave.object import ZWaveException
from openzwave.option import ZWaveOption
from .db import DB
from openzwave.network import ZWaveNetwork

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('openzwave')


class Zwave:
    def __init__(self):
        self.network = ZWaveNetwork(self.options, autostart=False)
        self.zwave_start = False
        self.db = DB(self.network)

    @property
    def options(self):
        # Define some manager options
        try:
            options = ZWaveOption(settings.DEVICE, config_path=settings.CONFIG_PATH, user_path=settings.USER_PATH,
                                  cmd_line=settings.CMD_LINE)
            options.set_log_file(settings.LOG_FILE)
            options.set_append_log_file(settings.APPEND_LOG_FILE)
            options.set_console_output(settings.CONSOLE_OUTPUT)
            options.set_save_log_level(settings.LOG)
            options.set_logging(settings.LOGIN)
            options.lock()
            is_options_set = True
            return options
        except ZWaveException as exception:
            self.message = "Error : {}".format(exception)
            return self.message

    def start(self):
        if self.network.is_ready:
            print("***** Le réseau est déjà démarré ! *****")
        else:
            start_listener()
            self.network.start()

            # We wait for the network.
            print("***** Le réseau est en cours de démarrage. Veuillez patienter. *****")
            for i in range(0, 90):
                if self.network.state >= self.network.STATE_READY:
                    print("***** Le réseau est prêt ! *****")
                    print("Le controlleur réseau est : {}".format(self.network.controller))

                    self.db.update_database()
                    break
                else:
                    sys.stdout.write(".")
                    sys.stdout.flush()
                    time.sleep(1.0)

    def stop(self):
        if self.network.is_ready:
            print("***** Le réseau est en cours de d'arrêt. Veuillez patienter. *****")
            self.network.stop()
            stop_listener()
        else:
            print("***** Le réseau est déjà à l'arrêt. *****")
