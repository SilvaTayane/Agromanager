from django.urls import path
from . import views

urlpatterns = [
    path("", views.clima_atual, name="monitoramento"),
    path("previsao/", views.previsao, name="previsao_semana"),
    path("historico/semanal/", views.historico_semanal, name="historico_clima_semanal"),
    path("historico/mensal/", views.historico_mensal, name="historico_clima_mensal"),
]
