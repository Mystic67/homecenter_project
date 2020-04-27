from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect

from .backend.zwave import Zwave
from .backend.rollershutter import Rollershutter
from .backend.light import Light
from .models import Controller, Node, Params, Instances
from .forms import InstanceForm

zwave = Zwave()

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



