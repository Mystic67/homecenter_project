import time


class Light:
    def __init__(self, network, node_id, node_instance):
        self.network = network
        self.node_id = node_id
        self.node_instance = node_instance
        self.nodes = self.network.nodes

    def set_on(self):
        message = "La lumière allumée !"
        self.network.nodes[self.node_id].set_switch(self.value_id, True)
        time.sleep(0.2)
        state = self.state
        return message, state

    def set_off(self):
        message = "La lumière éteinte !"
        self.network.nodes[self.node_id].set_switch(self.value_id, False)
        time.sleep(0.2)
        state = self.state
        return message, state

    @property
    def is_ready(self):
        return self.nodes[self.node_id].is_ready

    @property
    def state(self):
        if self.nodes[self.node_id].get_switch_state(self.value_id):
            return 'On'
        else:
            return 'Off'

    @property
    def value_id(self):
        node_value_id = [key for key in self.nodes[self.node_id].get_switches()][self.node_instance]
        return node_value_id
