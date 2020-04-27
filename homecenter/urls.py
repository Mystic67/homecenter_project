from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path, include
from homecenter import views

app_name = "homecenter"

urlpatterns = [
#    path('', views.index, name='index'),
    path('light/', views.light, name='light'),
    path('network/', views.network, name='network'),
    path('roller_shutter/', views.roller_shutter, name='roller_shutter'),
    path('admin/', admin.site.urls),
]
