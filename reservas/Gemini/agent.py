#agent.py
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def consultar_asistente(mensaje_usuario, contexto_salones):
    instrucciones =  f"""
    Eres el asistente virtual académico de EduPlace.
    Tu objetivo es ayudar a los catedráticos a consultar disponibilidad de salones.
    
    REGLA DE ORO PARA LA DISPONIBILIDAD:
    Si el usuario pregunta por un día o un horario (por ejemplo: "el sábado" o "el lunes a las 10:00"), 
    revisa el contexto que te paso. Si un salón NO tiene una reserva listada en ese día/horario, 
    SIGNIFICA QUE ESTÁ DISPONIBLE. Solo los horarios listados están ocupados.
    
    Aquí tienes la lista actual de salones y sus reservas ocupadas:
    {contexto_salones}

    Responde de forma amable, formal y muy breve. Con cualquier otra pregunta que no tenga
    relación al objetivo únicamente responde, "Como asistente de EduSpace no puedo responder esa pregunta, si necesitas ayuda para tu reserva de salones !Dímelo¡"
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=mensaje_usuario,
        config= types.GenerateContentConfig(
            system_instruction=instrucciones
        )
    )

    return response.text

#print(consultar_asistente("Cuanto es uno más uno?", "CC1 (30 personas)"))