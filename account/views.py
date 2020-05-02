from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http.response import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import User
from .forms import MySignUpForm


@staff_member_required(login_url='/')
def user_admin(request):
    if request.is_ajax() and request.method == 'POST':
        jsmessages = {}
        action = request.POST.get('action')
        try:
            user_id = request.POST.get('user_id')
            user = User.objects.get(pk=int(user_id))
            user.delete()
            jsmessages['success'] = "L'utilisateur à été supprimé avec succès !"
        except Exception as e:
            jsmessages['error'] = "L'utilisateur n'a pas été supprimé ! Erreur: {}".format(e)
        data = {"messages": jsmessages, "action": action}
        return JsonResponse(data)

    if not request.is_ajax() and request.method == 'POST':
        form = MySignUpForm(request.POST)
        users = User.objects.all()
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, "Le nouvel utilisateur a été créé avec succès !")
            return HttpResponseRedirect(reverse('account:user_admin'))
        else:
            context = {
                'users': users,
                'form': form
            }
            return render(request, 'account/user_admin.html', context)
    else:
        form = MySignUpForm()
        users = User.objects.all()
        context = {
            'users': users,
            'form': form,
        }
        return render(request, 'account/user_admin.html', context)
