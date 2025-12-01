from django.urls import path
from . import views

urlpatterns = [
    # CRUD
    path('animais/', views.listar_animais, name='listar_animais'),  #Mostra todos os animais cadastrados.
    path('animais/novo', views.criar_animais, name='criar_animais'),  #Formulário para cadastrar um novo animal.
    path('detalhe/<int:animal_id>/', views.detalhe_animal, name='detalhe_animal'),  #Mostra informações de um animal específico (por ID).
    path('editar/<int:animal_id>/', views.editar_animal, name='editar_animal'),
    path('deletar/<int:animal_id>/', views.deletar_animal, name='deletar_animal'),   #Página ou ação para confirmação de exclusão.
]
