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



