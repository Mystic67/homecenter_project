from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect

from .backend.zwave import Zwave
from .backend.rollershutter import Rollershutter
from .backend.light import Light
from .models import Controller, Node, Params, Instances
from .forms import InstanceForm

zwave = Zwave()


@staff_member_required(login_url='/')
def network(request):
    if zwave.network.is_ready:
        switch_state = "On"
        nw_text_state = "démarré !"
    else:
        switch_state = "Off"
        nw_text_state = "arrêté !"

    if request.is_ajax and request.method == 'POST':
        jsmessages = {}
        switch_state = request.POST.get('state')
        if not zwave.network.is_ready and switch_state == "On":
            zwave.start()
            jsmessages['success'] = "Le réseau z-wave est démarré !"
            data = {
                'nw_text_state': "démarré !",
                'messages': jsmessages
            }
            return JsonResponse(data)

        elif zwave.network.is_ready and switch_state == "Off":
            zwave.stop()
            jsmessages['success'] = "Le réseau z-wave est arrêté !"
            data = {
                'nw_text_state': "arrêté !",
                'messages': jsmessages
            }
            return JsonResponse(data)
    else:
        network_state = zwave.network.is_ready
        context = {
            "state": switch_state,
            "network_state": network_state,
            "nw_text_state": nw_text_state
        }
        return render(request, 'homecenter/network.html', context)


@login_required(login_url='/')
def roller_shutter(request):
    roller_shutter_nodes = Instances.objects.filter(index=1).filter(node__product_type__contains="0x030")
    if zwave.network.is_ready:
        nw_state = "On"
    else:
        nw_state = "Off"
    setLevel = 0
    level = 0
    if request.is_ajax and request.method == 'POST':
        jsmessages = {}
        if not zwave.network.is_ready:
            jsmessages['warning'] = "Le réseau z-wave est à l'arrêt !"
            data = {
                'nw_state': nw_state,
                'messages': jsmessages
            }
            return JsonResponse(data)
        else:
            node_id = request.POST.get('node_id')
            setLevel = request.POST.get('setLevel')
            stop = request.POST.get('stop')

            jsmessages.clear()
            rollershutter = Rollershutter(zwave.network, int(node_id))
            if not rollershutter.is_ready:
                jsmessages['warning'] = "Le modules {} n'est pas prêt.".format(node_id)
                data = {'messages': jsmessages}
                return JsonResponse(data)
            else:
                if int(stop) == 0:
                    jsmessages['success'], level = rollershutter.set_open_level(int(setLevel))
                else:
                    if int(stop) == 1:
                        print(rollershutter.level)
                        print(rollershutter.infos())

                data = {'messages': jsmessages, 'level': level}
                return JsonResponse(data)
    else:
        context = {
            "setLevel": setLevel,
            "level": level,
            "nw_state": nw_state,
            "roller_shutter_nodes": roller_shutter_nodes
        }
        return render(request, 'homecenter/roller_shutter.html', context)


@staff_member_required(login_url='/')
def nodes_config(request):
    if request.is_ajax and request.method == 'POST':
        jsmessages = {}
        if request.POST.get('calibrate') == 'True':
            if not zwave.network.is_ready:
                jsmessages['warning'] = "Le réseau z-wave est à l'arrêt !"
                data = {
                    'messages': jsmessages
                }
                return JsonResponse(data)
            else:
                node_id = request.POST.get('node_id')
                rollershutter = Rollershutter(zwave.network, int(node_id))
                print("Calibration node: {}".format(node_id))
                rollershutter.calibrate()
                jsmessages['success'] = 'La calibration du volet N°{} est terminé'.format(node_id)
                data = {
                    'messages': jsmessages
                }
        else:
            instanceForm = InstanceForm(request.POST)
            if instanceForm.is_valid():
                node_id = request.POST.get('node_id')
                node_instance = request.POST.get('node_instance')
                node_name = instanceForm.cleaned_data.get('name')
                node_location = instanceForm.cleaned_data.get('location')
                node = Instances.objects.get(node=node_id, index=node_instance)
                node.name = node_name
                node.location = node_location
                node.save()
                jsmessages['success'] = "Enregistrement réussi"

                print('node_id: {}\n node_instance: {}\n  node_name: {}\n node_location: {}'.format(node_id,
                                                                                                    node_instance,
                                                                                                    node_name,
                                                                                                    node_location))
                data = {
                    "messages": jsmessages
                }
                return JsonResponse(data)
    else:
        roller_shutter_nodes = Instances.objects.filter(index=1).filter(node__product_type__contains="0x030") \
            .select_related('node')
        light_nodes = Instances.objects.filter(node__product_type__contains="0x020").select_related(
            'node')

        instanceForm = InstanceForm()

        context = {
            "instanceForm": instanceForm,
            "roller_shutter_nodes": roller_shutter_nodes,
            "light_nodes": light_nodes
        }

        return render(request, 'homecenter/config.html', context)


@login_required(login_url='/')
def light(request):
    light_nodes = Instances.objects.filter(node__product_type__contains="0x020")
    if zwave.network.is_ready:
        nw_state = "On"
    else:
        nw_state = "Off"

    if request.is_ajax and request.method == 'POST':
        jsmessages = {}
        if not zwave.network.is_ready:
            jsmessages['warning'] = "Le réseau z-wave est à l'arrêt !"
            data = {
                'nw_state': nw_state,
                'messages': jsmessages
            }
            return JsonResponse(data)
        else:
            node_id = request.POST.get('nodeId')
            node_instance = request.POST.get('nodeInstance')
            setState = request.POST.get('setState')

            light = Light(zwave.network, int(node_id), int(node_instance))
            light_nodes = Instances.objects.get(node_id=node_id, index=node_instance)
            if not light.is_ready:
                jsmessages['success'] = "Le modules n'est pas prêt."
                data = {'messages': messages}
                return JsonResponse(data)
            else:
                print(setState)
                if setState == "Off":
                    jsmessages['success'], state = light.set_off()
                else:
                    jsmessages['success'], state = light.set_on()
                light_nodes.state = state
                light_nodes.save()
                jsmessages.clear()

                data = {'messages': jsmessages, 'state': state}
                return JsonResponse(data)
    else:
        context = {
            "nw_state": nw_state,
            "light_nodes": light_nodes
        }
        return render(request, 'homecenter/light.html', context)
