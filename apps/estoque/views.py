from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Categoria, Item, MovimentacaoEstoque
from .forms import ItemForm, MovimentacaoForm
from django.contrib import messages


def listar_estoque(request):
    itens = Item.objects.all()
    return render(request, 'listar_items.html', {'itens': itens})


def visualizar_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'visualizar_item.html', {'item': item})


def criar_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Item criado com sucesso!")
            return redirect('listar_estoque')
    else:
        form = ItemForm()
    return render(request, 'criar_item.html', {'form': form})


def editar_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item atualizado!")
            return redirect('listar_estoque')
    else:
        form = ItemForm(instance=item)
    return render(request, 'editar_item.html', {'form': form, 'item': item})

def excluir_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Item excluído!")
        return redirect('listar_estoque')
    return render(request, 'excluir_item.html', {'item': item})


def registrar_movimentacao(request):
    if request.method == "POST":
        form = MovimentacaoForm(request.POST)
        if form.is_valid():
            movimentacao = form.save(commit=False)
            item = movimentacao.item
            quantidade = movimentacao.quantidade_movimentada
            
     
            if movimentacao.tipo_movimentacao == 'entrada':
                item.quantidade_atual += quantidade
                messages.success(request, f"Entrada de {quantidade} itens realizada com sucesso!")
            
            
            elif movimentacao.tipo_movimentacao == 'saida':
                if item.quantidade_atual >= quantidade:
                    item.quantidade_atual -= quantidade
                    messages.success(request, f"Saída de {quantidade} itens realizada com sucesso!")
                else:
                    messages.error(request, f"Estoque insuficiente! Atual: {item.quantidade_atual}")
                    return render(request, 'registrar_movimentacao.html', {'form': form})

            item.save() 
            movimentacao.save() 
            
            return redirect('listar_estoque')
    else:
        form = MovimentacaoForm()

    return render(request, 'registrar_movimentacao.html', {'form': form})


def historico_movimentacoes(request):
    movimentacoes = MovimentacaoEstoque.objects.select_related('item', 'item__categoria').all().order_by('-data_movimentacao')
    return render(request, 'historico_movimentacoes.html', {'movimentacoes': movimentacoes})