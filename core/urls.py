"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.urls import path
from django.contrib.auth import views as auth_views
from reservas.views import crear_reserva, pagina_de_exito, Home, lista_salones, detalle_salon, api_chatbot, editar_reserva, eliminar_reserva

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reservar/', crear_reserva, name='crear_reserva'),
    path('exito/', pagina_de_exito, name='pagina_de_exito'),
    path('home/', Home, name='home'),
    path('salones/', lista_salones, name='lista_salones'),
    path('salones/salon/<int:salon_id>', detalle_salon, name='detalle_salon'),
    path('chatbot/', api_chatbot, name= 'api_chatbot'),
    path('reserva/editar/<int:reserva_id>/', editar_reserva, name='editar_reserva'),
    path('reserva/eliminar/<int:reserva_id>/', eliminar_reserva, name='eliminar_reserva'),


    #Login
    path('login/', auth_views.LoginView.as_view(template_name = 'reservas/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]