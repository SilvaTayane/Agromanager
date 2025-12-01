from django.urls import path
from . import views

urlpatterns = [
    path('', views.menuativ, name='menu_atividades'),
    path('criaratividade/', views.criarAtividade, name='criar_atividade'),
    path('admin/atividades/', views.listar_atividades_admin, name='listar_atividades_admin'),
    path('admin/editar/<int:id_atividade>/', views.editar_atividade, name='editar_atividade'),
    path('admin/excluir/<int:id_atividade>/', views.excluir_atividade_logica, name='excluir_atividade'),
    path('trabalhador/', views.area_trabalhador, name='area_trabalhador'),
    path('atualizar-status/<int:id_atividade>/<str:nome_trabalhador>/', views.atualizar_status_atividade, name='atualizar_status'),
]