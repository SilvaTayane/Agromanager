from django.shortcuts import render
from django.utils import timezone
from .models import RegistroClimatico
from django.db.models import Avg, Max, Min
import datetime
import requests

WEATHERCODES = {
    0: "Céu limpo",
    1: "Poucas nuvens",
    2: "Nuvens dispersas",
    3: "Nublado",
    45: "Névoa",
    48: "Névoa com deposição",
    51: "Garoa leve",
    53: "Garoa moderada",
    55: "Garoa intensa",
    61: "Chuva leve",
    63: "Chuva moderada",
    65: "Chuva forte",
    71: "Neve leve",
    73: "Neve moderada",
    75: "Neve intensa",
    95: "Tempestade",
    96: "Tempestade com granizo leve",
    99: "Tempestade com granizo forte",
}

def clima_atual(request):

    latitude = -15.5958
    longitude = -56.0969

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&current=temperature_2m,wind_speed_10m,wind_direction_10m,weather_code"
        "&timezone=auto"
    )

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json().get("current", {})
    except Exception as e:
        return render(request, "monitoramento.html", {
            "erro": f"Erro ao consultar API: {e}"
        })

    if not data:
        return render(request, "monitoramento.html", {
            "erro": "A API não retornou dados climáticos."
        })

    temperatura = data.get("temperature_2m")
    vento = data.get("wind_speed_10m")
    direcao = data.get("wind_direction_10m")
    cond_codigo = data.get("weather_code")

    condicao_texto = WEATHERCODES.get(cond_codigo, "Indefinido")

    context = {
        "temperatura": temperatura,
        "vento": vento,
        "direcao": direcao,
        "condicao_texto": condicao_texto,
        "erro": None,
    }

    return render(request, "monitoramento.html", context)
def index(request):
    ultimo = RegistroClimatico.objects.filter(origem="automatico").order_by("-data_coleta").first()
    context = {"ultimo": ultimo}
    return render(request, "monitoramento.html", context)

def historico_semanal(request):
    hoje = timezone.now().date()
    inicio = hoje - datetime.timedelta(days=7)
    registros = RegistroClimatico.objects.filter(data_coleta__date__gte=inicio).order_by("-data_coleta")
    medias_por_dia = (
        RegistroClimatico.objects
        .filter(data_coleta__date__gte=inicio)
        .extra({"dia": "date(data_coleta)"})
        .values("dia")
        .annotate(media_temp=Avg("temperatura"))
        .order_by("dia")
    )
    return render(request, "historico_climatico_semanal.html", {"registros": registros, "medias_por_dia": medias_por_dia})

def previsao(request):
    latitude = -15.5958
    longitude = -56.0969
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
    previsao = {}
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        previsao = r.json().get("daily", {})
    except Exception as e:
        print("previsao: erro ao obter dados:", e)
        previsao = {}

    return render(request, "previsao.html", {"previsao": previsao})

def historico_mensal(request):
    hoje = timezone.now().date()
    inicio = hoje - datetime.timedelta(days=30)

    registros = (
        RegistroClimatico.objects
        .filter(data_coleta__date__gte=inicio)
        .order_by("-data_coleta")
    )
    medias_por_dia = (
        RegistroClimatico.objects
        .filter(data_coleta__date__gte=inicio)
        .extra({"dia": "date(data_coleta)"})
        .values("dia")
        .annotate(media_temp=Avg("temperatura"))
        .order_by("dia")
    )

    context = {
        "registros": registros,
        "medias_por_dia": medias_por_dia,
        "periodo": "Últimos 30 dias"
    }

    return render(request, "historico_climatico_mensal.html", context)

