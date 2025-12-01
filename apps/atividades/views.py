from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
import datetime
from .models import Atividade, LogAtividade

def menuativ(request): 
    return render(request, "admin_listar_atividades.html")

def criarAtividade(request):
    trabalhadores_teste = [
        {'id': 1, 'nome': 'Gustavo C.'},
        {'id': 2, 'nome': 'Daniel B'},
        {'id': 3, 'nome': 'Danilo V'},
        {'id': 4, 'nome': 'João G'},
        {'id': 5, 'nome': 'Tayane S'},
        {'id': 6, 'nome': 'Admin Sistema'}
    ]
    
    if request.method == 'POST':
        try:
            titulo = request.POST.get('titulo')
            descricao = request.POST.get('descricao')
            tipo_atividade = request.POST.get('tipo_atividade')
            prioridade = request.POST.get('prioridade')
            trabalhador_id = request.POST.get('trabalhador')
            data_limite = request.POST.get('data_limite')
            
            if not titulo or not tipo_atividade or not prioridade:
                messages.error(request, 'Título, tipo e prioridade são obrigatórios.')
                return render(request, 'criacao_atividade_placeholder.html', {'trabalhadores': trabalhadores_teste})
            
            atividade = Atividade(
                titulo=titulo,
                descricao=descricao,
                tipo_atividade=tipo_atividade,
                prioridade=prioridade,
                usuario_responsavel='usuario_teste',
                data_limite=data_limite if data_limite else None
            )
            
            if trabalhador_id:
                trabalhador_selecionado = next((t for t in trabalhadores_teste if str(t['id']) == trabalhador_id), None)
                if trabalhador_selecionado:
                    atividade.nome_trabalhador = trabalhador_selecionado['nome']
            
            atividade.save()
            
            LogAtividade.objects.create(
                atividade=atividade,
                log_atividade=f"Atividade criada - Título: {titulo}",
                usuario_responsavel='usuario_teste',
                tipo_acao="CRIACAO"
            )
            
            messages.success(request, 'Atividade criada com sucesso!')
            return redirect('criar_atividade')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar atividade: {str(e)}')
    
    return render(request, 'admin_criar_atividade.html', {'trabalhadores': trabalhadores_teste})

def listar_atividades(request):
    atividades = Atividade.objects.filter(data_exclusao__isnull=True)

    # hoje como datetime para evitar erro
    hoje = timezone.now()

    # Marca automaticamente atividades atrasadas
    for a in atividades:
        if a.data_limite:
            data_limite_dt = a.data_limite

            # Se data_limite for date, converte para datetime
            if isinstance(data_limite_dt, datetime.date) and not isinstance(data_limite_dt, datetime.datetime):
                data_limite_dt = datetime.datetime.combine(data_limite_dt, datetime.time.min, tzinfo=timezone.get_current_timezone())

            # Agora a comparação é SEMPRE datetime vs datetime
            if data_limite_dt < hoje and a.status not in ["concluida", "atrasada"]:
                a.status = "atrasada"
                a.save()

    # FILTROS
    tipo = request.GET.get("tipo")
    prioridade = request.GET.get("prioridade")
    data = request.GET.get("data")
    responsavel = request.GET.get("responsavel")

    if tipo:
        atividades = atividades.filter(tipo_atividade=tipo)
    if prioridade:
        atividades = atividades.filter(prioridade=prioridade)
    if data:
        atividades = atividades.filter(data_limite=data)
    if responsavel:
        atividades = atividades.filter(nome_trabalhador=responsavel)

    context = {
        "atividades": atividades,
        "tipos": Atividade.objects.values_list("tipo_atividade", flat=True).distinct(),
        "prioridades": Atividade.objects.values_list("prioridade", flat=True).distinct(),
        "responsaveis": Atividade.objects.values_list("nome_trabalhador", flat=True).distinct(),
        "filtros_ativos": {
            "tipo": tipo,
            "prioridade": prioridade,
            "data": data,
            "responsavel": responsavel,
        }
    }

    return render(request, "admin_listar_atividades.html", context)

def listar_atividades_admin(request):
    atividades = Atividade.objects.filter(data_exclusao__isnull=True).order_by('-data_criacao')
    
    filtro_excluidas = request.GET.get('excluidas', '')
    
    if filtro_excluidas:
        atividades = Atividade.objects.filter(data_exclusao__isnull=False).order_by('-data_exclusao')
    
    context = {
        'atividades': atividades,
        'filtro_excluidas': filtro_excluidas
    }
    return render(request, 'admin_listar_atividades.html', context)

def editar_atividade(request, id_atividade):
    atividade = get_object_or_404(Atividade, id_atividade=id_atividade)
    
    if atividade.data_exclusao:
        messages.error(request, 'Não é possível editar uma atividade excluída.')
        return redirect('listar_atividades_admin')
    
    trabalhadores_hardcoded = [
        {'id': 1, 'nome': 'Gustavo C.'},
        {'id': 2, 'nome': 'Daniel B'},
        {'id': 3, 'nome': 'Danilo V'},
        {'id': 4, 'nome': 'João G'},
        {'id': 5, 'nome': 'Tayane S'},
        {'id': 6, 'nome': 'Admin Sistema'}
    ]
    
    if request.method == 'POST':
        try:
            titulo = request.POST.get('titulo')
            descricao = request.POST.get('descricao')
            tipo_atividade = request.POST.get('tipo_atividade')
            prioridade = request.POST.get('prioridade')
            status = request.POST.get('status')
            trabalhador_id = request.POST.get('trabalhador')
            data_limite = request.POST.get('data_limite')
            descricao_problema = request.POST.get('descricao_problema')
            
            if not titulo or not tipo_atividade or not prioridade or not status:
                messages.error(request, 'Título, tipo, prioridade e status são obrigatórios.')
                return render(request, 'admin_editar_atividade.html', {
                    'atividade': atividade,
                    'trabalhadores': trabalhadores_hardcoded
                })
            
            dados_antigos = f"Título: {atividade.titulo}, Tipo: {atividade.tipo_atividade}, Prioridade: {atividade.prioridade}, Status: {atividade.status}"
            
            atividade.titulo = titulo
            atividade.descricao = descricao
            atividade.tipo_atividade = tipo_atividade
            atividade.prioridade = prioridade
            atividade.status = status
            atividade.data_limite = data_limite if data_limite else None
            atividade.descricao_problema = descricao_problema
            atividade.usuario_responsavel = 'admin_edicao'
            
            if trabalhador_id:
                trabalhador_selecionado = next((t for t in trabalhadores_hardcoded if str(t['id']) == trabalhador_id), None)
                if trabalhador_selecionado:
                    atividade.nome_trabalhador = trabalhador_selecionado['nome']
            else:
                atividade.nome_trabalhador = None
            
            atividade.save()
            
            LogAtividade.objects.create(
                atividade=atividade,
                log_atividade=f"Atividade editada. Dados antigos: {dados_antigos}",
                usuario_responsavel='admin_edicao',
                tipo_acao="EDICAO"
            )
            
            messages.success(request, 'Atividade atualizada com sucesso!')
            return redirect('listar_atividades_admin')
            
        except Exception as e:
            messages.error(request, f'Erro ao editar atividade: {str(e)}')
    
    return render(request, 'admin_editar_atividade.html', {
        'atividade': atividade,
        'trabalhadores': trabalhadores_hardcoded
    })

def excluir_atividade_logica(request, id_atividade):
    atividade = get_object_or_404(Atividade, id_atividade=id_atividade)
    
    if atividade.data_exclusao:
        messages.warning(request, 'Esta atividade já foi excluída.')
        return redirect('listar_atividades')
    
    if request.method == 'POST':
        try:
            atividade.data_exclusao = timezone.now()
            atividade.usuario_responsavel = 'admin_sistema'
            atividade.save()
            
            LogAtividade.objects.create(
                atividade=atividade,
                log_atividade=f"Atividade excluída por admin_sistema",
                usuario_responsavel='admin_sistema',
                tipo_acao="EXCLUSAO_LOGICA"
            )
            
            messages.success(request, 'Atividade excluída com sucesso!')
            return redirect('listar_atividades_admin')
        except Exception as e:
            messages.error(request, f'Erro ao excluir atividade: {str(e)}')
    
    return render(request, 'admin_confirmar_exclusao.html', {'atividade': atividade})

def area_trabalhador(request):
    """Página única da área do trabalhador com seleção por dropdown"""
    trabalhadores = [
        {'id': 1, 'nome': 'Gustavo C.'},
        {'id': 2, 'nome': 'Daniel B'},
        {'id': 3, 'nome': 'Danilo V'},
        {'id': 4, 'nome': 'João G'},
        {'id': 5, 'nome': 'Tayane S'},
    ]
    
    trabalhador_selecionado = None
    atividades = []
    
    if request.method == 'POST':
        nome_trabalhador = request.POST.get('trabalhador')
        if nome_trabalhador:
            atividades = Atividade.objects.filter(
                nome_trabalhador=nome_trabalhador,
                data_exclusao__isnull=True
            ).order_by('-data_criacao')
            
            trabalhador_selecionado = next(
                (t for t in trabalhadores if t['nome'] == nome_trabalhador), 
                None
            )
    
    total_atividades = len(atividades)
    
    context = {
        'trabalhadores': trabalhadores,
        'trabalhador_selecionado': trabalhador_selecionado,
        'atividades': atividades,
        'total_atividades': total_atividades
    }
    
    return render(request, 'area_trabalhador.html', context)

def atualizar_status_atividade(request, id_atividade, nome_trabalhador):
    print(f"DEBUG: Acessando atualizar_status para {nome_trabalhador}, atividade {id_atividade}")
    
    atividade = get_object_or_404(Atividade, id_atividade=id_atividade)
    print(f"DEBUG: Atividade encontrada - {atividade.titulo}")
    
    if not atividade.pode_ser_editada_por(nome_trabalhador):
        messages.error(request, 'Você não tem permissão para editar esta atividade.')
        return redirect('area_trabalhador')
    
    if request.method == 'POST':
        try:
            novo_status = request.POST.get('status')
            descricao_problema = request.POST.get('descricao_problema', '')
            
            status_anterior = atividade.status
 
            atividade.status = novo_status
            atividade.data_modificacao = timezone.now()

            if novo_status == 'com_problemas' and descricao_problema:
                atividade.descricao_problema = descricao_problema
            
            atividade.save()

            LogAtividade.objects.create(
                atividade=atividade,
                log_atividade=f"Status alterado de {status_anterior} para {novo_status} por {nome_trabalhador}",
                usuario_responsavel=nome_trabalhador,
                tipo_acao="ATUALIZACAO_STATUS"
            )
            
            messages.success(request, 'Status da atividade atualizado com sucesso!')
            return redirect('area_trabalhador')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar atividade: {str(e)}')

    return render(request, 'funcionario_atualizar_status.html', {
        'atividade': atividade,
        'nome_trabalhador': nome_trabalhador
    })