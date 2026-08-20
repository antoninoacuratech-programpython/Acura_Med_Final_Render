from django.db import models

from App_Hospital.hospital import Hospital
from App_Usuarios.ultilizador import Utilizador


# Requisição de medicamentos feita por um sector do hospital (enfermaria,
# internamento, bloco operatório, etc.) directamente à Farmácia — sem
# passar por uma Prescrição formal ligada a um paciente específico.
# Fluxo simplificado (tudo-ou-nada, mesmo padrão de Prescrição/Solicitação
# de Exame): PENDENTE → ENTREGUE ou REJEITADA.
class RequisicaoInterna(models.Model):

    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        ENTREGUE = "ENTREGUE", "Entregue"
        REJEITADA = "REJEITADA", "Rejeitada"

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT,
        related_name="requisicoes_internas",
        verbose_name="Hospital",
    )

    origem = models.CharField(
        "Sector de Origem",
        max_length=150,
        help_text="Ex.: Nave A - Enfermaria 3, Bloco Operatório",
    )

    solicitante = models.ForeignKey(
        Utilizador,
        on_delete=models.PROTECT,
        related_name="requisicoes_internas_solicitadas",
        verbose_name="Solicitante",
    )

    status = models.CharField(
        "Estado",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
    )

    observacoes = models.TextField(
        "Observações",
        blank=True,
    )

    criado_em = models.DateTimeField(
        "Criado em",
        auto_now_add=True,
    )

    atualizado_em = models.DateTimeField(
        "Atualizado em",
        auto_now=True,
    )

    def __str__(self):
        return f"Requisição #{self.id} — {self.origem} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Requisição Interna"
        verbose_name_plural = "Requisições Internas"
        ordering = ["-criado_em"]