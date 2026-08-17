from django.conf import settings
from django.db import models

from .lote import Lote


# Regista TODA a alteração de quantidade num Lote — entrada, saída ou
# ajuste. É a única fonte de verdade para "quem mexeu no stock, quando e
# porquê"; a quantidade em Lote é sempre o resultado destes movimentos,
# nunca deve ser editada directamente fora deste fluxo.
class MovimentoStock(models.Model):

    class Tipo(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SAIDA = "SAIDA", "Saída"
        AJUSTE = "AJUSTE", "Ajuste"

    lote = models.ForeignKey(
        Lote,
        on_delete=models.PROTECT,
        related_name="movimentos",
        verbose_name="Lote",
    )

    tipo = models.CharField(
        "Tipo",
        max_length=10,
        choices=Tipo.choices,
    )

    quantidade = models.PositiveIntegerField(
        "Quantidade",
    )

    utilizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimentos_stock",
        verbose_name="Utilizador",
    )

    referencia = models.CharField(
        "Referência",
        max_length=150,
        blank=True,
        help_text="Ex.: 'Entrada inicial', 'Dispensação #12'",
    )

    criado_em = models.DateTimeField(
        "Criado em",
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.tipo} {self.quantidade} — {self.lote}"

    class Meta:
        verbose_name = "Movimento de Stock"
        verbose_name_plural = "Movimentos de Stock"
        ordering = ["-criado_em"]