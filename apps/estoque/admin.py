from django.contrib import admin
from .models import Categoria, Item, MovimentacaoEstoque

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    search_fields = ['nome']

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'quantidade_atual')
    list_filter = ('categoria',)
    search_fields = ('nome',)

@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('tipo_movimentacao', 'item', 'quantidade_movimentada', 'data_movimentacao', 'usuario_responsavel')
    list_filter = ('tipo_movimentacao', 'data_movimentacao')
    search_fields = ('item__nome',)
    readonly_fields = ('data_movimentacao',)
