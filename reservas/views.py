from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ReservaForm
from .models import Salon

@login_required
def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)

            reserva.docente = request.user

            reserva.save()
            return redirect('pagina_de_exito')
    else:
        form = ReservaForm()

    return render(request, 'reservas/crear_reserva.html',{'form': form})


@login_required
def pagina_de_exito(request):
    return render(request, 'reservas/exito.html')


@login_required
def Home(request):
    return render(request, 'reservas/home.html')


@login_required
def lista_salones (request):
    salones = Salon.objects.filter(activo=True)
    return render(request, 'reservas/lista_salones.html', {'salones': salones})

@login_required
def detalle_salon (request, salon_id):
    salon = get_object_or_404(Salon, pk=salon_id)
    return render(request, 'reservas/detalle_salon.html', {'salon': salon})
