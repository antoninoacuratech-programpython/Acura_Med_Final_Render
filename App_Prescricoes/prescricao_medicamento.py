from django.db import models

from App_Hospital.hospital import Hospital
from App_Pacientes.paciente import Paciente
from App_Usuarios.ultilizador import Utilizador
from App_Atendimentos.atendimento import Atendimento



class PrescricaoMedicamento(models.Model):

    class Status(models.TextChoices):
        AGUARDANDO = "AGUARDANDO", "Aguardando"
        EM_ANALISE = "EM_ANALISE", "Em análise"
        EM_SEPARACAO = "EM_SEPARACAO", "Em separação"
        AGUARDANDO_CONFERENCIA = "AGUARDANDO_CONFERENCIA", "Aguardando conferência"
        DISPENSADO = "DISPENSADO", "Dispensado"
        PENDENCIA = "PENDENCIA", "Pendência"
        CANCELADO = "CANCELADO", "Cancelado"

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT,
        related_name="prescricoes",
        verbose_name="Hospital",
    )

    atendimento = models.ForeignKey(
        Atendimento,
        on_delete=models.PROTECT,
        related_name="prescricoes",
        verbose_name="Atendimento",
    )

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="prescricoes",
        verbose_name="Paciente",
    )

    medico = models.ForeignKey(
        Utilizador,
        on_delete=models.PROTECT,
        related_name="prescricoes_emitidas",
        verbose_name="Médico",
    )

    status = models.CharField(
        "Estado",
        max_length=25,
        choices=Status.choices,
        default=Status.AGUARDANDO,
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
        return f"Receita #{self.id} — {self.paciente.nome_completo} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Prescrição de Medicamento"
        verbose_name_plural = "Prescrições de Medicamentos"
        ordering = ["-criado_em"]