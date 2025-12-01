from django.db import models

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Item(models.Model):
    
    nome = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
   
    unidade_medida = models.CharField(max_length=20, default='un', verbose_name="Unidade de Medida")
    
    quantidade_atual = models.PositiveIntegerField(default=0)
    
   
    quantidade_minima = models.PositiveIntegerField(default=5, verbose_name="Estoque Mínimo")
    quantidade_maxima = models.PositiveIntegerField(default=100, verbose_name="Estoque Máximo")
    
   
    localizacao = models.CharField(max_length=50, blank=True, null=True, verbose_name="Localização Física")
    status = models.BooleanField(default=True, verbose_name="Ativo")
    
    descricao = models.TextField(max_length=200, blank=True, null=True, verbose_name="Descrição")
    
    
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
   
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    def __str__(self):
        return self.nome


class MovimentacaoEstoque(models.Model):
    TIPO_CHOICES = (
        ('entrada', 'Entrada'),
        ('saida', 'Saída')
    )

    tipo_movimentacao = models.CharField(max_length=10, choices=TIPO_CHOICES)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantidade_movimentada = models.PositiveIntegerField()
    data_movimentacao = models.DateTimeField(auto_now_add=True)
    usuario_responsavel = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.tipo_movimentacao} - {self.item.nome}"