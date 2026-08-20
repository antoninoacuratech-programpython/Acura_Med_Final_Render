from django.db import models

from App_Usuarios.ultilizador import Utilizador
from .internamento import Internamento


# Cada linha é uma nota de evolução clínica — o histórico do que
# aconteceu com o paciente durante o internamento (feito por médico ou
# enfermeiro, várias vezes ao dia se for preciso). Nunca se edita nem
# apaga uma nota já escrita — é um registo cronológico, como um diário
# clínico; para corrigir algo, escreve-se uma nova nota a esclarecer.
class Evolucao(models.Model):

    class Tipo(models.TextChoices):
        MEDICA = "MEDICA", "Evolução Médica"
        ENFERMAGEM = "ENFERMAGEM", "Evolução de Enfermagem"
        OUTRA = "OUTRA", "Outra"

    internamento = models.ForeignKey(
        Internamento,
        on_delete=models.CASCADE,
        related_name="evolucoes",
        verbose_name="Internamento",
    )

    profissional = models.ForeignKey(
        Utilizador,
        on_delete=models.PROTECT,
        related_name="evolucoes_registadas",
        verbose_name="Profissional",
    )

    tipo = models.CharField(
        "Tipo",
        max_length=20,
        choices=Tipo.choices,
    )

    texto = models.TextField(
        "Nota de Evolução",
    )

    criado_em = models.DateTimeField(
        "Criado em",
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.internamento.paciente.nome_completo} ({self.criado_em:%d/%m/%Y %H:%M})"

    class Meta:
        verbose_name = "Evolução"
        verbose_name_plural = "Evoluções"
        ordering = ["-criado_em"]