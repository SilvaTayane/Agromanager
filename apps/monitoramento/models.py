from django.db import models
from django.utils import timezone


class RegistroClimatico(models.Model):
    temperatura = models.FloatField()
    umidade = models.FloatField(null=True, blank=True)
    vento = models.FloatField(null=True, blank=True)
    condicao = models.IntegerField()  # weathercode
    origem = models.CharField(
        max_length=20,
        choices=[("API", "API"), ("Sensor", "Sensor")],
        default="API"
    )

    data_coleta = models.DateTimeField(default=timezone.now)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.data_coleta} - {self.temperatura}°C"
