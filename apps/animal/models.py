# Create your models here.
from django.db import models
from django.utils import timezone


class Animal(models.Model):

    # Choices simples
    SEXO_CHOICES = [
        ("Macho", "Macho"),
        ("Fêmea", "Fêmea"),
    ]

    FINALIDADE_CHOICES = [
        ("Leite", "Leite"),
        ("Corte", "Corte"),
        ("Reprodução", "Reprodução"),
        ("Venda", "Venda"),
    ]

    ORIGEM_CHOICES = [
        ("Compra", "Compra"),
        ("Nascimento Interno", "Nascimento Interno"),
        ("Doação", "Doação"),
    ]
  

    # CAMPOS DO MODEL

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50)
    especie = models.CharField(max_length=30)
    raca = models.CharField(max_length=30, blank=True, null=True)
    sexo = models.CharField(max_length=10, choices=SEXO_CHOICES)
    data_nascimento = models.DateField()
    numero_identificacao = models.CharField(max_length=20,blank=True,null=True,unique=True)
    finalidade = models.CharField(max_length=20,choices=FINALIDADE_CHOICES,blank=True,null=True)
    peso_inicial = models.DecimalField(max_digits=8,decimal_places=2,blank=True,null=True)
    observacoes = models.TextField(blank=True,null=True)
    data_aquisicao = models.DateField(blank=True,null=True)
    origem = models.CharField(max_length=20,choices=ORIGEM_CHOICES,blank=True,null=True)
    valor_compra = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    data_criacao = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animais"
        ordering = ['-id']

    def __str__(self):
        return f"{self.id} - {self.nome} - {self.especie}"
