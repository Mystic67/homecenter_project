"""homecenter_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from account.forms import MyLoginView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from homecenter_project import settings

urlpatterns = [
    path('', MyLoginView.as_view(template_name='account/login.html'), name='login'),
    path('account/', include('account.urls', namespace='account')),
    path('homecenter/', include('homecenter.urls', namespace='homecenter')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
