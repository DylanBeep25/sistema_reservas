from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Salon(models.Model):
    nombre = models.CharField(max_length=50, unique=True, help_text="Ej. Salón CC1")
    capacidad = models.PositiveIntegerField(help_text="Número máximo de personas")
    ubicacion = models.CharField(max_length=100, help_text="Área de cabañas ciencia de la comunicación")
    activo = models.BooleanField(default=True, help_text="Indica si el salón está habilitado para reserva")

    class Meta:
        verbose_name = "Salón"
        verbose_name_plural = "Salones"
        ordering = ['nombre']


    def __str__(self):
        return f"{self.nombre} (Cap: {self.capacidad})"


class Reserva(models.Model):
    HORARIO_7_9 = '07:00-09:00'
    HORARIO_95_115 = '09:30-11:30'
    HORARIO_115_135 = '11:30-13:30'
    HORARIO_14_16 = '14:00-16:00'
    HORARIO_16_18 = '16:00-18:00'

    ELEGIR_HORARIOS = [
        (HORARIO_7_9, '07:00 a 09:00'),
        (HORARIO_95_115, '09:30 a 11:30'),
        (HORARIO_115_135, '11:30 a 13:30'),
        (HORARIO_14_16, '14:00 a 16:00'),
        (HORARIO_16_18, '16:00 a 18:00'),
    ]

    salon = models.ForeignKey(
        Salon,
        on_delete=models.PROTECT,
        related_name='reservas'
    )
    docente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservas'
    )
    fecha = models.DateField()
    horario=models.CharField(max_length=20, choices=ELEGIR_HORARIOS)
    curso= models.CharField(max_length=120, help_text="Materia o proposito de la reserva")
    creada_en= models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering=['-fecha', 'horario']

        constraints = [
            models.UniqueConstraint(
                fields=['salon', 'fecha', 'horario'],
                name='unique_reserva_salon_horario'
            )
        ]

    def clean(self):
        super().clean()
        if self.fecha and self.fecha < timezone.now().date():
            raise ValidationError({'fecha': 'No puedes reservar en una fecha pasada.'})

    def __str__(self):
        return f"{self.salon.nombre} | {self.fecha} [{self.horario}] - {self.docente.get_full_name() or self.docente.username}"