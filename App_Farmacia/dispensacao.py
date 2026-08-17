from django.conf import settings
from django.db import models

from App_Hospital.hospital import Hospital
from App_Pacientes.paciente import Paciente
from .medicamento import Medicamento
from .lote import Lote


# Cabeçalho de uma dispensação: um paciente veio à farmácia com receita,
# pediu X unidades de um medicamento, e o farmacêutico autorizou a entrega.
# A quantidade aqui é sempre o total entregue — de onde exactamente saiu
# (que lotes) fica registado em ItemDispensacao.
class Dispensacao(models.Model):

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT,
        related_name="dispensacoes",
        verbose_name="Hospital",
    )

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="dispensacoes",
        verbose_name="Paciente",
    )

    medicamento = models.ForeignKey(
        Medicamento,
        on_delete=models.PROTECT,
        related_name="dispensacoes",
        verbose_name="Medicamento",
    )

    quantidade = models.PositiveIntegerField(
        "Quantidade dispensada",
    )

    farmaceutico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="dispensacoes_realizadas",
        verbose_name="Farmacêutico",
    )

    observacao = models.CharField(
        "Observação",
        max_length=255,
        blank=True,
    )

    criado_em = models.DateTimeField(
        "Criado em",
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.medicamento} x{self.quantidade} — {self.paciente}"

    class Meta:
        verbose_name = "Dispensação"
        verbose_name_plural = "Dispensações"
        ordering = ["-criado_em"]


# Detalhe de que lote(s) exactamente cobriram a dispensação — uma
# dispensação de 20 unidades pode ter saído de 2 lotes diferentes se o
# primeiro (mais próximo de vencer, regra FEFO) não tinha os 20 completos.
class ItemDispensacao(models.Model):

    dispensacao = models.ForeignKey(
        Dispensacao,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Dispensação",
    )

    lote = models.ForeignKey(
        Lote,
        on_delete=models.PROTECT,
        related_name="itens_dispensados",
        verbose_name="Lote",
    )

    quantidade = models.PositiveIntegerField(
        "Quantidade retirada deste lote",
    )

    def __str__(self):
        return f"{self.lote.numero_lote}: {self.quantidade}"

    class Meta:
        verbose_name = "Item de Dispensação"
        verbose_name_plural = "Itens de Dispensação"