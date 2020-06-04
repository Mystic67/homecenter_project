class Rollershutter():
    def __init__(self, network, node_id):
        self.network = network
        self.node_id = node_id
        self.nodes = self.network.nodes

    @property
    def is_ready(self):
        return self.nodes[self.node_id].is_ready

    @property
    def is_failed(self):
        return self.nodes[self.node_id].is_failed

    @property
    def manufacturer_name(self):
        return self.nodes[self.node_id].manufacturer_name

    @property
    def product_name(self):
        return self.nodes[self.node_id].product_name

    @property
    def name(self):
        return self.nodes[self.node_id].name

    def set_name(self, name):
        self.nodes[self.node_id].name = name

    @property
    def location(self):
        return self.nodes[self.node_id].location

    def set_location(self, location):
        self.nodes[self.node_id].name = location

    @property
    def level(self):
        level = [val.data for val in
                 self.nodes[self.node_id].get_values_for_command_class(38)
                     .values()][4]
        print("level_value_id: {} ".format(self.get_level_value_id()))
        print("level: {} ".format(level))
        return level

    @property
    def switch_state(self):
        state = self.nodes[self.node_id].get_switch_state(
            self.get_switch_value_id())
        return state

    @property
    def configs(self):
        configs = self.nodes[self.node_id].get_configs()
        return configs

    @property
    def query_state(self):
        query_state = self.nodes[self.node_id].request_state()
        return query_state

    def calibrate(self):
        # self.network.
        message = "Le volet est en cours de calibration. Veuillez patienter !"
        self.nodes[self.node_id].set_config_param(29, 1)
        return message

    def set_param(self, param, value):
        message = "Le paramètre est remplacé"
        self.nodes[self.node_id].set_config_param(param, value)
        return message

    def set_field(self, field, value):
        self.nodes[self.node_id].set_field(field, value)

    def open(self):
        message = "Le volet s'ouvre !"
        self.network.nodes[self.node_id].set_switch(self.get_switch_value_id(),
                                                    True)
        level = "100"
        return message, level

    def close(self):
        message = "Le volet se ferme fermeture !"
        self.network.nodes[self.node_id].set_switch(self.get_switch_value_id(),
                                                    False)
        level = "0"
        return message, level

    def stop(self, value):
        message = "Le volet a été stoppé !."
        self.network.nodes[self.node_id].set_switch(self.get_switch_value_id(),
                                                    value)
        return message, self.level

    def set_open_level(self, set_level):
        self.network.nodes[self.node_id].set_dimmer(self.value_id, set_level)
        if set_level == 99:
            set_level = 100
        message = "Le volet se met en position à {} % d'ouverture.".format(
            set_level)
        return message, self.level

    def get_switch_value_id(self):
        node_value_id = [key for key in
                         self.nodes[self.node_id].get_switches().keys()].pop()
        return node_value_id

    @property
    def value_id(self):
        node_values = [key for key in
                       self.nodes[self.node_id].get_dimmers().keys()].pop()
        return node_values

    @property
    def power(self):
        power = [val.data for val in
                 self.nodes[self.node_id].get_values_for_command_class(
                     50).values()][1]
        return power

    def get_level_value_id(self):
        level_value_id = [val.value_id for val in
                          self.nodes[self.node_id].get_values_for_command_class(
                              38).values()][4]
        return level_value_id

    def infos(self):
        data = self.nodes[self.node_id].to_dict()
        return data

