from django.db import models

from App_Hospital.hospital import Hospital
from App_Pacientes.paciente import Paciente
from App_Usuarios.ultilizador import Utilizador
from App_Atendimentos.atendimento import Atendimento


# Solicitação de exames laboratoriais, criada pelo médico a partir do
# Atendimento (mesmo padrão de PrescricaoMedicamento). O status percorre
# as 3 fases do laboratório: Aguardando Colheita (Pré-analítica) →
# Colhido → Em Análise (Analítica) → Concluído (Pós-analítica).
class SolicitacaoExame(models.Model):

    class Status(models.TextChoices):
        AGUARDANDO = "AGUARDANDO", "Aguardando Colheita"
        COLETADO = "COLETADO", "Colhido"
        EM_ANALISE = "EM_ANALISE", "Em Análise"
        CONCLUIDO = "CONCLUIDO", "Concluído"
        CANCELADO = "CANCELADO", "Cancelado"

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT,
        related_name="solicitacoes_exame",
        verbose_name="Hospital",
    )

    atendimento = models.ForeignKey(
        Atendimento,
        on_delete=models.PROTECT,
        related_name="solicitacoes_exame",
        verbose_name="Atendimento",
    )

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="solicitacoes_exame",
        verbose_name="Paciente",
    )

    medico = models.ForeignKey(
        Utilizador,
        on_delete=models.PROTECT,
        related_name="solicitacoes_exame_emitidas",
        verbose_name="Médico",
    )

    status = models.CharField(
        "Estado",
        max_length=20,
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
        return f"Solicitação #{self.id} — {self.paciente.nome_completo} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Solicitação de Exame"
        verbose_name_plural = "Solicitações de Exame"
        ordering = ["-criado_em"]