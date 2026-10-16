from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Salon(models.Model):
    nombre = models.CharField(max_length=50, unique=True, help_text="Ej. Salón CC1")
    capacidad = models.PositiveIntegerField(help_text="Número máximo de personas")
    ubicacion = models.CharField(max_length=100, help_text="Área de cabañas ciencia de la comunicación")
    activo = models.BooleanField(default=True, help_text="Indica si el salón está habilitado para reserva")
    
    # NUEVO: Bandera para identificar salones tipo "Aula Magna"
    es_especial = models.BooleanField(default=False, help_text="Si es verdadero, tiene horarios restringidos y requiere aprobación del administrador.")

    class Meta:
        verbose_name = "Salón"
        verbose_name_plural = "Salones"
        ordering = ['nombre']

    def __str__(self):
        tipo = "*|VIP|*" if self.es_especial else "Regular"
        return f"{self.nombre} (Cap: {self.capacidad}) - {tipo}"


class Reserva(models.Model):
    # Horarios Regulares
    HORARIO_7_9 = '07:00-09:00'
    HORARIO_95_115 = '09:30-11:30'
    HORARIO_115_135 = '11:30-13:30'
    HORARIO_14_16 = '14:00-16:00'
    HORARIO_16_18 = '16:00-18:00'
    
    # Horarios Especiales
    HORARIO_ESPECIAL_MANANA = '08:00-12:00'
    HORARIO_ESPECIAL_TARDE = '14:00-17:00'

    ELEGIR_HORARIOS = [
        ('Horarios Regulares', (
            (HORARIO_7_9, '07:00 a 09:00'),
            (HORARIO_95_115, '09:30 a 11:30'),
            (HORARIO_115_135, '11:30 a 13:30'),
            (HORARIO_14_16, '14:00 a 16:00'),
            (HORARIO_16_18, '16:00 a 18:00'),
        )),
        ('Horarios Especiales (Solo Aula Magna)', (
            (HORARIO_ESPECIAL_MANANA, '08:00 a 12:00'),
            (HORARIO_ESPECIAL_TARDE, '14:00 a 17:00'),
        )),
    ]

    # NUEVO: Sistema de estados
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_APROBADA = 'aprobada'
    ESTADO_RECHAZADA = 'rechazada'
    
    OPCIONES_ESTADO = [
        (ESTADO_PENDIENTE, 'Pendiente de revisión'),
        (ESTADO_APROBADA, 'Aprobada'),
        (ESTADO_RECHAZADA, 'Rechazada'),
    ]

    salon = models.ForeignKey(Salon, on_delete=models.PROTECT, related_name='reservas')
    docente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas')
    fecha = models.DateField()
    horario = models.CharField(max_length=20, choices=ELEGIR_HORARIOS)
    curso = models.CharField(max_length=120, help_text="Materia o proposito de la reserva")
    
    # NUEVO: Campo de estado (por defecto se aprueba, el 'clean' lo cambia si es VIP)
    estado = models.CharField(max_length=20, choices=OPCIONES_ESTADO, default=ESTADO_APROBADA)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha', 'horario']
        constraints = [
            models.UniqueConstraint(
                fields=['salon', 'fecha', 'horario'],
                name='unique_reserva_salon_horario'
            )
        ]

    def clean(self):
        super().clean()
        
        # 1. Validación de fecha en el pasado
        if self.fecha and self.fecha < timezone.now().date():
            raise ValidationError({'fecha': 'No puedes reservar en una fecha pasada.'})

        # Si aún no hemos seleccionado un salón (pasa a veces en el panel de admin al crear), saltamos el resto
        if not hasattr(self, 'salon') or not self.salon:
            return

        horarios_regulares = [self.HORARIO_7_9, self.HORARIO_95_115, self.HORARIO_115_135, self.HORARIO_14_16, self.HORARIO_16_18]
        horarios_especiales = [self.HORARIO_ESPECIAL_MANANA, self.HORARIO_ESPECIAL_TARDE]

        # 2. Lógica para Salones VIP (Aula Magna)
        if self.salon.es_especial:
            if self.horario not in horarios_especiales:
                raise ValidationError({
                    'horario': f'El salón {self.salon.nombre} es de uso especial. Solo admite los bloques largos: 08:00-12:00 o 14:00-17:00.'
                })
            # Forzar a que entre en estado pendiente si es una reserva nueva
            if not self.pk: 
                self.estado = self.ESTADO_PENDIENTE

        # 3. Lógica para Salones Normales
        else:
            if self.horario not in horarios_regulares:
                raise ValidationError({
                    'horario': f'El salón {self.salon.nombre} es un aula regular. Has seleccionado un horario que no le corresponde.'
                })
            # Los salones normales se aprueban automáticamente
            if not self.pk:
                self.estado = self.ESTADO_APROBADA

    def __str__(self):
        return f"{self.salon.nombre} | {self.fecha} [{self.horario}] - {self.docente.username} ({self.get_estado_display()})"