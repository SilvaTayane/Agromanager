import requests
from django.utils import timezone
from .models import RegistroClimatico

def coletar_clima():
    """
    Coleta o clima pela Open-Meteo e salva como 'automatico' no banco.
    Executado pelo scheduler a cada 6 horas.
    """
    latitude = -15.5958
    longitude = -56.0969

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    try:
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
    except Exception as e:
        print("coletar_clima: erro na requisição:", e)
        return

    dados = resposta.json().get("current_weather", {})
    if not dados:
        print("coletar_clima: resposta sem current_weather")
        return

    try:
        RegistroClimatico.objects.create(
            temperatura=dados.get("temperature"),
            umidade=None,                # Open-Meteo current_weather não traz umidade (padrão None)
            vento=dados.get("windspeed"),
            condicao=int(dados.get("weathercode") or 0),
            origem="automatico",
            data_coleta=timezone.now()
        )
        print("coletar_clima: registro salvo em", timezone.now())
    except Exception as e:
        print("coletar_clima: erro ao salvar no BD:", e)
