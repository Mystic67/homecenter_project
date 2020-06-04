from sqlite3 import DataError
from homecenter.models import Controller, Node, Params, Instances


def update_instance_state(instance_value_id, instance_values):
    print("Mise à jour des status")
    print(instance_values)
    try:
        instance = Instances.objects.get(value_id=instance_value_id)
        # post_save.connect(update_instance_state, sender=Instances)
        if instance_values.label == "Switch":
            if instance_values.data:
                instance.state = 'On'
            else:
                instance.state = 'Off'
            instance.save()
        elif instance_values.label == 'Level':
            instance.level = instance_values.data
            instance.save()
        else:
            pass
    except:
        pass


class DB:
    def __init__(self, zwave):
        self.network = zwave.network

    def update_database(self):
        nodes = self.network.nodes
        controller = self.network.controller
        try:
            controller, created = Controller.objects.update_or_create(
                home_id=controller.home_id,
                defaults={
                    'name': controller.node.name,
                    'product': controller.node.product_name
                }
            )

            for node_id in nodes:
                node, created = Node.objects.update_or_create(
                    node_id=node_id,
                    defaults={
                        'name': nodes[node_id].name,
                        'location': nodes[node_id].location,
                        'product_type': nodes[node_id].product_type,
                        'product_name': nodes[node_id].product_name,
                        'manufacturer_name': nodes[node_id].manufacturer_name,
                        'num_groups': nodes[node_id].num_groups,
                        'is_beaming_device': nodes[node_id].is_beaming_device,
                        'is_failed': nodes[node_id].is_failed,
                        'is_ready': nodes[node_id].is_ready,
                        'is_awake': nodes[node_id].is_awake,
                        'controller_node': controller,
                    }
                )

                for conf in nodes[node_id].get_configs():
                    params, created = Params.objects.update_or_create(
                        node_param=node,
                        index=nodes[node_id].get_configs()[conf].index,
                        defaults={
                            'label': nodes[node_id].get_configs()[conf].label,
                            'data': nodes[node_id].get_configs()[conf].data
                        }
                    )

                for switch_instance, switch_instance_value_id in enumerate(
                        nodes[node_id].get_switches()):
                    bool_state = self.network.nodes[node_id].get_switch_state(
                        switch_instance_value_id)
                    if bool_state:
                        str_state = "On"
                    else:
                        str_state = "Off"
                    instances, created = Instances.objects.update_or_create(
                        node=node,
                        index=switch_instance,
                        value_id=switch_instance_value_id,
                        defaults={
                            'type': 'switch',
                            'state': str_state
                        }
                    )

                for dimmer_instance, dimmer_instance_value_id in enumerate(
                        nodes[node_id].get_dimmers()):
                    level = self.network.nodes[node_id].get_dimmer_level(
                        dimmer_instance_value_id)
                    instances, created = Instances.objects.update_or_create(
                        node=node,
                        index=dimmer_instance,
                        value_id=dimmer_instance_value_id,
                        defaults={
                            'type': 'dimmer',
                            'level': level
                        }
                    )

        except DataError:
            pass
