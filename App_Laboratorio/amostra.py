from django.db import models

from App_Usuarios.ultilizador import Utilizador
from .requisicao import Requisicao
from .tipo_exame import TipoExame


class Amostra(models.Model):
    """Fase Pré-analítica — Colheita.

    Uma amostra biológica colhida na sala de colheita (ou orientada para
    colheita ao domicílio), associada a uma Requisição. Uma amostra pode
    servir vários exames do mesmo tipo de amostra dentro da mesma
    requisição. O fim desta fase é marcado por `colhida_em`, que dá
    início à fase Analítica para os exames ligados a ela."""

    class LocalColheita(models.TextChoices):
        LABORATORIO = "laboratorio", "Laboratório"
        DOMICILIO = "domicilio", "Domicílio"

    class Condicao(models.TextChoices):
        ADEQUADA = "adequada", "Adequada"
        INADEQUADA = "inadequada", "Inadequada"
        PENDENTE = "pendente", "Pendente de Avaliação"

    requisicao = models.ForeignKey(
        Requisicao,
        on_delete=models.CASCADE,
        related_name="amostras",
        verbose_name="Requisição",
    )

    codigo = models.CharField(
        "Código da Amostra",
        max_length=40,
        unique=True,
        help_text="Código/etiqueta de identificação da amostra (ex.: código de barras).",
    )

    tipo_amostra = models.CharField(
        "Tipo de Amostra",
        max_length=20,
        choices=TipoExame.TipoAmostra.choices,
    )

    local_colheita = models.CharField(
        "Local da Colheita",
        max_length=15,
        choices=LocalColheita.choices,
        default=LocalColheita.LABORATORIO,
    )

    colhida_por = models.ForeignKey(
        Utilizador,
        on_delete=models.SET_NULL,
        related_name="amostras_colhidas",
        verbose_name="Colhida por",
        blank=True,
        null=True,
    )

    colhida_em = models.DateTimeField("Colhida em", blank=True, null=True)

    condicao = models.CharField(
        "Condição da Amostra",
        max_length=15,
        choices=Condicao.choices,
        default=Condicao.PENDENTE,
    )

    motivo_rejeicao = models.TextField("Motivo de Rejeição", blank=True)

    observacoes = models.TextField("Observações", blank=True)

    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    def __str__(self):
        return f"Amostra {self.codigo} ({self.get_tipo_amostra_display()})"

    class Meta:
        verbose_name = "Amostra"
        verbose_name_plural = "Amostras"
        ordering = ["-criado_em"]