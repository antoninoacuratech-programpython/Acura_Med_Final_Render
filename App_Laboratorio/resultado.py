from django.db import models

from App_Usuarios.ultilizador import Utilizador
from .exame_solicitado import ExameSolicitado


class Resultado(models.Model):
    """Fase Pós-analítica — Resultado.

    Um resultado por exame solicitado. `validado_por` representa a
    segunda assinatura (conferência) comum em laboratórios antes da
    liberação; `data_liberacao` marca o momento em que o resultado
    fica disponível para consulta/entrega."""

    exame_solicitado = models.OneToOneField(
        ExameSolicitado,
        on_delete=models.CASCADE,
        related_name="resultado",
        verbose_name="Exame Solicitado",
    )

    valores = models.TextField(
        "Valores Encontrados",
        help_text="Resultado bruto do exame (valores, parâmetros, unidades).",
    )

    interpretacao = models.TextField("Interpretação/Observações", blank=True)

    arquivo_laudo = models.FileField(
        "Laudo (PDF)",
        upload_to="laboratorio/laudos/",
        blank=True,
        null=True,
    )

    tecnico_responsavel = models.ForeignKey(
        Utilizador,
        on_delete=models.PROTECT,
        related_name="resultados_lancados",
        verbose_name="Lançado por",
    )

    validado_por = models.ForeignKey(
        Utilizador,
        on_delete=models.SET_NULL,
        related_name="resultados_validados",
        verbose_name="Validado por",
        blank=True,
        null=True,
    )

    data_liberacao = models.DateTimeField("Data de Liberação", blank=True, null=True)

    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    def __str__(self):
        return f"Resultado - {self.exame_solicitado}"

    class Meta:
        verbose_name = "Resultado"
        verbose_name_plural = "Resultados"
        ordering = ["-criado_em"]