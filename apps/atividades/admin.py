from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Atividade, LogAtividade

class LogAtividadeInline(admin.TabularInline):
    model = LogAtividade
    extra = 0
    readonly_fields = ['data_criacao', 'usuario_responsavel', 'tipo_acao']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo_atividade', 'prioridade', 'status', 'nome_trabalhador', 'data_limite', 'data_criacao']
    list_filter = ['tipo_atividade', 'prioridade', 'status', 'data_criacao', 'data_limite']
    search_fields = ['titulo', 'descricao', 'nome_trabalhador']
    readonly_fields = ['data_criacao', 'data_modificacao', 'data_exclusao']
    fieldsets = [
        ('Informações Básicas', {
            'fields': ['titulo', 'descricao', 'tipo_atividade', 'prioridade', 'status']
        }),
        ('Datas Importantes', {
            'fields': ['data_limite', 'data_criacao', 'data_modificacao', 'data_exclusao']
        }),
        ('Atribuição', {
            'fields': ['nome_trabalhador']
        }),
        ('Problemas', {
            'fields': ['descricao_problema'],
            'classes': ['collapse']
        }),
        ('Auditoria', {
            'fields': ['usuario_responsavel'],
            'classes': ['collapse']
        })
    ]
    inlines = [LogAtividadeInline]

    def save_model(self, request, obj, form, change):
        if not obj.usuario_responsavel or obj.usuario_responsavel == 'sistema':
            obj.usuario_responsavel = request.user.username
        super().save_model(request, obj, form, change)

@admin.register(LogAtividade)
class LogAtividadeAdmin(admin.ModelAdmin):
    list_display = ['atividade', 'tipo_acao', 'usuario_responsavel', 'data_criacao']
    list_filter = ['tipo_acao', 'data_criacao', 'usuario_responsavel']
    search_fields = ['atividade__titulo', 'log_atividade', 'usuario_responsavel']
    readonly_fields = ['data_criacao', 'usuario_responsavel', 'atividade', 'log_atividade', 'tipo_acao']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False