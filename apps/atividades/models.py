from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class AtividadeManager(models.Manager):
    def ativas(self):
        return self.filter(data_exclusao__isnull=True)

class Atividade(models.Model):
    PRIORIDADE_CHOICES = [
        ('ALTA', 'Alta'),
        ('MEDIA', 'Média'),
        ('BAIXA', 'Baixa'),
    ]
    
    STATUS_CHOICES = [
        ('registrada', 'Registrada'),
        ('atribuida', 'Atribuída'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
        ('pendente', 'Pendente'),
        ('com_problemas', 'Com Problemas'),
    ]
    
    TIPO_ATIVIDADE_CHOICES = [
        ('AGRICOLA', 'Agrícola'),
        ('AGROPECUARIA', 'Agropecuária'),
        ('GERAL', 'Geral'),
    ]

    id_atividade = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(max_length=500, blank=True, null=True)
    tipo_atividade = models.CharField(max_length=12, choices=TIPO_ATIVIDADE_CHOICES, default='GERAL')
    prioridade = models.CharField(max_length=5, choices=PRIORIDADE_CHOICES, default='MEDIA')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='registrada')
    id_trabalhador = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='atividades')
    nome_trabalhador = models.CharField(max_length=100, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_modificacao = models.DateTimeField(auto_now=True)
    data_exclusao = models.DateTimeField(blank=True, null=True)
    data_limite = models.DateTimeField(blank=True, null=True)
    descricao_problema = models.TextField(max_length=500, blank=True, null=True)
    usuario_responsavel = models.CharField(max_length=20, default='sistema')

    objects = AtividadeManager()
    
    def excluir_logicamente(self, usuario):
        self.data_exclusao = timezone.now()
        self.usuario_responsavel = usuario
        self.save()

        LogAtividade.objects.create(
            atividade=self,
            log_atividade=f"Atividade excluída logicamente por {usuario}",
            usuario_responsavel=usuario,
            tipo_acao="EXCLUSAO_LOGICA"
        )
    def pode_ser_editada_por(self, nome_trabalhador):
        return self.nome_trabalhador == nome_trabalhador and not self.data_exclusao

    class Meta:
        db_table = 'atividades'

    def __str__(self):
        return self.titulo

    def esta_atrasada(self):
        from django.utils import timezone
        if self.data_limite and self.status not in ['concluida', 'cancelada']:
            return timezone.now() > self.data_limite
        return False

class LogAtividade(models.Model):
    id_log = models.AutoField(primary_key=True)
    atividade = models.ForeignKey('Atividade', on_delete=models.CASCADE, related_name='logs')
    log_atividade = models.TextField(max_length=500)
    usuario_responsavel = models.CharField(max_length=20)
    data_criacao = models.DateTimeField(auto_now_add=True)
    tipo_acao = models.CharField(max_length=50)

    class Meta:
        db_table = 'log_atividades'
        verbose_name = 'Log de Atividade'
        verbose_name_plural = 'Logs de Atividades'

    def __str__(self):
        return f"Log {self.id_log} - {self.atividade.titulo}"