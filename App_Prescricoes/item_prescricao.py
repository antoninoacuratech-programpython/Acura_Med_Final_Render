from django.db import models

from App_Farmacia.medicamento import Medicamento
from .prescricao_medicamento import PrescricaoMedicamento


# Cada linha da receita: um medicamento com a sua posologia. Uma
# PrescricaoMedicamento pode (e normalmente vai) ter vários ItemPrescricao —
# ex.: Amoxicilina 500mg + Paracetamol 500mg na mesma receita.
class ItemPrescricao(models.Model):

    class ViaAdministracao(models.TextChoices):
        ORAL = "ORAL", "Oral"
        INTRAVENOSA = "INTRAVENOSA", "Intravenosa"
        INTRAMUSCULAR = "INTRAMUSCULAR", "Intramuscular"
        SUBCUTANEA = "SUBCUTANEA", "Subcutânea"
        TOPICA = "TOPICA", "Tópica"
        INALATORIA = "INALATORIA", "Inalatória"
        RECTAL = "RECTAL", "Rectal"
        OUTRA = "OUTRA", "Outra"

    prescricao = models.ForeignKey(
        PrescricaoMedicamento,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Prescrição",
    )

    medicamento = models.ForeignKey(
        Medicamento,
        on_delete=models.PROTECT,
        related_name="itens_prescritos",
        verbose_name="Medicamento",
    )

    dosagem = models.CharField(
        "Dosagem",
        max_length=50,
        blank=True,
        help_text="Ex.: 500mg, 1 cápsula",
    )

    via_administracao = models.CharField(
        "Via de administração",
        max_length=20,
        choices=ViaAdministracao.choices,
        default=ViaAdministracao.ORAL,
    )

    frequencia = models.CharField(
        "Frequência",
        max_length=50,
        blank=True,
        help_text="Ex.: 8/8h, 1x ao dia",
    )

    duracao_dias = models.PositiveIntegerField(
        "Duração (dias)",
        blank=True,
        null=True,
    )

    quantidade = models.PositiveIntegerField(
        "Quantidade total prescrita",
    )

    observacoes = models.CharField(
        "Observações",
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return f"{self.medicamento.nome} — {self.dosagem} ({self.quantidade})"

    class Meta:
        verbose_name = "Item de Prescrição"
        verbose_name_plural = "Itens de Prescrição"