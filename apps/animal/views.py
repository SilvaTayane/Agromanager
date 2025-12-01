from django.contrib import messages
from django.shortcuts import render,get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse

from apps.animal.forms import AnimalForm
from .models import Animal
from django.views.decorators.http import require_POST



def listar_animais(request):
    # Obtém todos os animais
    animais_list = Animal.objects.all().order_by('-id')
    
    # Aplica filtros
    search_term = request.GET.get('search', '')
    especie_filter = request.GET.get('especie', '')
    sexo_filter = request.GET.get('sexo', '')
    
    if search_term:
        animais_list = animais_list.filter(
            Q(nome__icontains=search_term) | 
            Q(numero_identificacao__icontains=search_term)
        )
    
    if especie_filter:
        animais_list = animais_list.filter(especie=especie_filter)
    
    if sexo_filter:
        animais_list = animais_list.filter(sexo=sexo_filter)
    
    # Paginação
    paginator = Paginator(animais_list, 10)  # 10 animais por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'animais': page_obj,
        'total_animais': animais_list.count(),
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
    }
    
    return render(request, 'listar_animais.html', context)

def detalhe_animal(request, animal_id):
    # Usar get_object_or_404 com o ID específico
    animal = get_object_or_404(Animal, id=animal_id)
    
    # Seus dados para as abas (exemplo)
    health_history = []  # Substitua pelo seu modelo real
    movement_history = []  # Substitua pelo seu modelo real
    
    context = {
        'animal': animal,
        'health_history': health_history,
        'movement_history': movement_history,
    }
    
    return render(request, 'detalhe_animal.html', context)

def criar_animais(request):
    if request.method == 'POST':
        form = AnimalForm(request.POST)
        if form.is_valid():
            animal = form.save()
            return redirect('listar_animais')  # ou outra URL de sucesso
    else:
        form = AnimalForm()
    
    return render(request, 'criar_animais.html', {'form': form})

@require_POST
def deletar_animal(request, animal_id):
    animal = get_object_or_404(Animal, pk=animal_id)
    animal_nome = animal.nome
    animal.delete()
    
    # Agora messages está importado corretamente
    messages.success(request, f'Animal "{animal_nome}" excluído com sucesso!')
    return redirect('listar_animais')

def editar_animal(request, animal_id):
    animal = get_object_or_404(Animal, pk=animal_id)
    form_action = reverse('editar_animal', args=(animal_id,))

    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES, instance=animal)

        context = {
            'form': form,
            'form_action': form_action,
        }
        
        if form.is_valid():
            animal = form.save()
            return redirect('editar_animal', animal_id=animal.pk)

        return render(
            request,
            'criar_animais.html',  # mesmo template de criação
            context
        )

    context = {
        'form': AnimalForm(instance=animal),
        'form_action': form_action,
    }
    return render(
        request,
        'criar_animais.html',  # mesmo template de criação
        context
    )

