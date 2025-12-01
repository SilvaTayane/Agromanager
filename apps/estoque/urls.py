from django.urls import path
from . import views

urlpatterns = [
    path('estoque/', views.listar_estoque, name='listar_estoque'),
    path('item/<int:item_id>/visualizar/', views.visualizar_item, name='visualizar_item'),
    path('item/criar/', views.criar_item, name='criar_item'),
    path('item/<int:item_id>/editar/', views.editar_item, name='editar_item'),
    path('item/<int:item_id>/excluir/', views.excluir_item, name='excluir_item'),
    path('movimentacao/', views.registrar_movimentacao, name='registrar_movimentacao'),
    path('historico/', views.historico_movimentacoes, name='historico_movimentacoes'),
]