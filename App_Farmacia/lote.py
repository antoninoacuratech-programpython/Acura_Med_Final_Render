from django.db import models
from django.utils import timezone

from App_Hospital.hospital import Hospital
from .medicamento import Medicamento


# Stock de um medicamento num hospital, controlado por lote — obrigatório
# para rastreabilidade e para aplicar a regra FEFO (First-Expire-First-Out:
# lote com validade mais próxima sai primeiro). A quantidade disponível de
# um medicamento num hospital é a soma dos seus lotes com quantidade > 0.
class Lote(models.Model):

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT,
        related_name="lotes_medicamento",
        verbose_name="Hospital",
    )

    medicamento = models.ForeignKey(
        Medicamento,
        on_delete=models.PROTECT,
        related_name="lotes",
        verbose_name="Medicamento",
    )

    numero_lote = models.CharField(
        "Número do lote",
        max_length=50,
    )

    validade = models.DateField(
        "Data de validade",
    )

    quantidade = models.PositiveIntegerField(
        "Quantidade disponível",
        default=0,
    )

    fornecedor = models.CharField(
        "Fornecedor",
        max_length=150,
        blank=True,
    )

    data_entrada = models.DateField(
        "Data de entrada",
        auto_now_add=True,
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
    )

    @property
    def vencido(self):
        return self.validade < timezone.localdate()

    @property
    def dias_para_vencer(self):
        return (self.validade - timezone.localdate()).days

    def __str__(self):
        return f"{self.medicamento} — Lote {self.numero_lote} ({self.hospital})"

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        # FEFO: ordenar por validade garante que o primeiro lote devolvido
        # numa queryset é sempre o que vence primeiro.
        ordering = ["validade"]
        unique_together = ("hospital", "medicamento", "numero_lote")