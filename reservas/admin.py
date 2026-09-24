from django.contrib import admin
from .models import Salon, Reserva

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display=('nombre','capacidad','ubicacion','activo')
    list_filter=('activo','ubicacion')
    search_fields = ('nombre', 'ubicacion')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('salon', 'fecha', 'horario', 'docente', 'curso','creada_en')
    list_filter = ('fecha', 'horario', 'salon')
    search_fields = ('curso', 'docente__username', 'docente__first_name', 'docente__last_name', 'salon__nombre')
    date_hierarchy = 'fecha'