from django.db import models

from .medicamento import Medicamento
from .requisicao_interna import RequisicaoInterna


class ItemRequisicaoInterna(models.Model):

    requisicao = models.ForeignKey(
        RequisicaoInterna,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Requisição",
    )

    medicamento = models.ForeignKey(
        Medicamento,
        on_delete=models.PROTECT,
        related_name="itens_requisitados",
        verbose_name="Medicamento",
    )

    quantidade_solicitada = models.PositiveIntegerField(
        "Quantidade Solicitada",
    )

    quantidade_entregue = models.PositiveIntegerField(
        "Quantidade Entregue",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.medicamento.nome} — {self.requisicao}"

    class Meta:
        verbose_name = "Item de Requisição Interna"
        verbose_name_plural = "Itens de Requisição Interna"