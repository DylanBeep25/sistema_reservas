from django import forms
from .models import Reserva
from django.core.exceptions import NON_FIELD_ERRORS

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['salon', 'fecha', 'horario', 'curso']

        error_message = {
            NON_FIELD_ERRORS: {
                'unique_together': 'Lo sentimos, este salón ya está ocupado en esa fecha y horario. Por favor, elige otro.',
            }
        }