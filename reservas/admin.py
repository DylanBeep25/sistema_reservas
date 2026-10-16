from django.contrib import admin
from .models import Salon, Reserva

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad', 'ubicacion', 'activo', 'es_especial')
    list_filter = ('activo', 'es_especial')
    search_fields = ('nombre', 'ubicacion')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('salon', 'fecha', 'horario', 'docente', 'estado', 'creada_en')
    list_filter = ('estado', 'fecha', 'salon__es_especial', 'salon')
    search_fields = ('salon__nombre', 'docente__username', 'docente__first_name', 'docente__last_name')
    list_editable = ('estado',)
    actions = ['aprobar_reservas_seleccionadas', 'rechazar_reservas_seleccionadas']

    @admin.action(description='Aprobar reservas seleccionadas')
    def aprobar_reservas_seleccionadas(self, request, queryset):
        actualizadas = queryset.update(estado='aprobada')
        self.message_user(request, f'Se aprobaron {actualizadas} reservas exitosamente.')

    @admin.action(description='Rechazar reservas seleccionadas')
    def rechazar_reservas_seleccionadas(self, request, queryset):
        actualizadas = queryset.update(estado='rechazada')
        self.message_user(request, f'Se rechazaron {actualizadas} reservas.')