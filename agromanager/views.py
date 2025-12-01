from django.shortcuts import render
import requests
from django.db.models import F, Count, Sum
import json
from apps.animal.models import Animal
from apps.atividades.models import Atividade
from apps.estoque.models import Item


def visualizar_login(request):
    return render(request, 'login.html')

def visualizar_dashboard(request):

    total_animais = Animal.objects.count()

    tarefas_pendentes = Atividade.objects.filter(status="registrada").count()
    tarefas_urgentes = Atividade.objects.filter(status="registrada", prioridade="ALTA").count()

    itens_estoque = Item.objects.count()

    itens_baixo_estoque = Item.objects.filter(
        quantidade_atual__lte=F("quantidade_minima")
    ).count()

    # ATIVIDADES RECENTES (últimos 4 registros)
    atividades_recentes = Atividade.objects.order_by('-data_criacao')[:4]

    contexto = {
        "total_animais": total_animais,
        "tarefas_pendentes": tarefas_pendentes,
        "tarefas_urgentes": tarefas_urgentes,
        "itens_estoque": itens_estoque,
        "itens_baixo_estoque": itens_baixo_estoque,
        "atividades_recentes": atividades_recentes,
    }

    return render(request, 'dashboard.html', contexto)

def visualizar_home(request):
    return render(request, 'homePrincipal.html')

def mostrar_localizacao(request):
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")

    url = "https://www.circuitdigest.cloud/geolinker-web-app"
    params = {
        "lat": lat,
        "lon": lon,
        "key": "AYb4wvgEp9kg",
    }

    response = requests.get(url, params=params)

    # garante que só tentamos decodificar JSON se o content-type for JSON
    if "application/json" in response.headers.get("Content-Type", ""):
        dados = response.json()
    else:
        # salva texto bruto mesmo, sem erro
        dados = {"raw": response.text}

    return render(request, "localizacao.html", {"dados": dados, "lat": lat, "lon": lon})


def visualizar_relatorio(request):
    # Paleta de cores harmoniosa com a identidade visual do sistema
    paleta_cores = [
        '#10b981',  # Verde vibrante (primária)
        '#2e5d3a',  # Verde escuro (secundária)
        '#4a9561',  # Verde médio (accent)
        '#3d7a52',  # Verde musgo
        '#1a3621',  # Verde muito escuro
        '#6ca98f',  # Verde menta suave
        '#8fb8a3',  # Verde pastel claro
        '#5eb3a1',  # Verde azulado
        '#7cb89c',  # Verde cinzento
        '#9dc9b8',  # Verde claro muito suave
        '#3f9572',  # Verde teal
        '#2d9c7f',  # Verde teal escuro
        '#69b89f',  # Verde cinzento claro
        '#4fa582',  # Verde meio-tom
        '#5ba08a',  # Verde cinza-esverdeado
        '#6db899',  # Verde suave
    ]

    # Cores para diferentes status de tarefas
    cores_status = {
        'registrada': '#f0e7d1',
        'em_andamento': '#10b981',
        'concluida': '#2e5d3a',
        'cancelada': '#8fb8a3',
    }

    animais_por_especie = (
        Animal.objects.values('especie')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    animals_data = []
    for idx, item in enumerate(animais_por_especie):
        cor = paleta_cores[idx % len(paleta_cores)]
        animals_data.append({
            "name": item["especie"],
            "value": item["total"],
            "color": cor
        })


    # --- 2) Atividades por Status ---
    atividades_status = (
        Atividade.objects.values('status')
        .annotate(total=Count('id_atividade'))
        .order_by('-total')
    )

    tasks_data = [
        {
            "status": item["status"],
            "value": item["total"],
            "color": cores_status.get(item["status"], '#2E5D3A')
        }
        for item in atividades_status
    ]


    # --- 3) Estoque por Categoria ---
    estoque_por_categoria = (
        Item.objects
        .values("categoria__nome")    # agrupa pela categoria
        .annotate(
            total_itens=Sum("quantidade_atual")
        )
        .order_by("-total_itens")
    )

    stock_data = [
        {
            "category": item["categoria__nome"],
            "quantity": item["total_itens"],
        }
        for item in estoque_por_categoria
    ]

    # Total de animais
    total_animais = Animal.objects.count()

    contexto = {
    "animals_data": json.dumps(animals_data),
    "tasks_data": json.dumps(tasks_data),
    "stock_data": json.dumps(stock_data),
    "total_animais": total_animais,
    }


    return render(request, 'relatorios.html', contexto)
    
