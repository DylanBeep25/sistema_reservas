import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ReservaForm
from .models import Salon
from .models import Reserva
from .Gemini.agent import consultar_asistente


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
    reservas_usuario = Reserva.objects.filter(docente=request.user)
    return render(request, 'reservas/home.html',{
        'reservas_usuario': reservas_usuario
    })


@login_required
def lista_salones (request):
    salones = Salon.objects.filter(activo=True)
    return render(request, 'reservas/lista_salones.html', {'salones': salones})

@login_required
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, docente=request.user)
    
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            reserva_actualizada = form.save(commit=False)
            
            # Si es un salón VIP (Aula Magna) y le cambian algo, lo devolvemos a estado 'pendiente' para que el admin lo vuelva a revisar
            if reserva_actualizada.salon.es_especial:
                reserva_actualizada.estado = Reserva.ESTADO_PENDIENTE
                
            reserva_actualizada.save()
            return redirect('home')
    else:
        form = ReservaForm(instance=reserva)
        
    return render(request, 'reservas/editar_reserva.html', {'form': form, 'reserva': reserva})

@login_required
def eliminar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, docente=request.user)
    
    if request.method == 'POST':
        reserva.delete()
        return redirect('home')
        
    return render(request, 'reservas/eliminar_reserva.html', {'reserva': reserva})

@login_required
def detalle_salon (request, salon_id):
    salon = get_object_or_404(Salon, pk=salon_id)
    
    reservas = salon.reservas.exclude(estado=Reserva.ESTADO_RECHAZADA)

    eventos = []
    for reserva in reservas:
        hora_inicio, hora_fin = reserva.horario.split('-')

        if reserva.estado == Reserva.ESTADO_PENDIENTE:
            color = '#f59e0b'
            titulo = f'Pendiente: {reserva.curso}'
        else:
            color = '#1e293b'
            titulo = f'Aprovada: {reserva.curso}'

        eventos.append({
            'title': f'{titulo} ({reserva.docente.first_name})',
            'start': f'{reserva.fecha}T{hora_inicio}:00',
            'end': f'{reserva.fecha}T{hora_fin}',
            'backgroundColor': color,
            'borderColor': color
        })


    return render(request, 'reservas/detalle_salon.html', {
        'salon': salon,
        'eventos_json': eventos
    })

#chatbot
@csrf_exempt
def api_chatbot(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mensaje = data.get('mensaje', '')

            # 1. Traemos los salones activos Y sus reservas en una sola consulta optimizada
            salones = Salon.objects.filter(activo=True).prefetch_related('reservas')
            
            # 2. Armamos un texto mucho más descriptivo
            contexto_lista = []
            for s in salones:
                info_salon = f"- SALÓN: {s.nombre} | Capacidad: {s.capacidad} | Ubicación: {s.ubicacion}"
                
                # Revisamos si tiene reservas
                reservas = s.reservas.all()
                if reservas.exists():
                    info_reservas = "  [Reservas programadas]:"
                    for r in reservas:
                        # Asumiendo que tus campos se llaman fecha, horario y curso
                        info_reservas += f"\n    * Fecha: {r.fecha} | Horario: {r.horario} | Curso: {r.curso} (Docente: {r.docente.first_name})"
                else:
                    info_reservas = "  [Reservas programadas]: Ninguna. Está totalmente disponible en todos los horarios."
                
                contexto_lista.append(f"{info_salon}\n{info_reservas}")

            # Unimos todo en un solo gran bloque de texto
            contexto_final = "\n\n".join(contexto_lista)

            # 3. Le pasamos este super-contexto a Gemini
            respuesta_ia = consultar_asistente(mensaje, contexto_final)

            return JsonResponse({'respuesta': respuesta_ia})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=400)