from django.db import models

from App_Pacientes.paciente import Paciente
from App_Hospital.hospital import Hospital
from App_Usuarios.ultilizador import Utilizador
from App_Agendamentos.models import Agendamento


class Requisicao(models.Model):
    """Fase Pré-analítica — Triagem.

    Representa o pedido de exames feito pelo médico e registado no
    laboratório quando o paciente chega para a triagem. Um pedido pode
    conter vários exames (ver ExameSolicitado), que por sua vez ficam
    associados a uma ou mais Amostras colhidas na sala de colheita."""

    class Status(models.TextChoices):
        AGUARDANDO_COLHEITA = "aguardando_colheita", "Aguardando Colheita"
        EM_COLHEITA = "em_colheita", "Em Colheita"
        EM_ANALISE = "em_analise", "Em Análise"
        CONCLUIDA = "concluida", "Concluída"
        LIBERADA = "liberada", "Liberada"
        CANCELADA = "cancelada", "Cancelada"

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="requisicoes_laboratorio",
        verbose_name="Paciente",
    )

    medico_solicitante = models.ForeignKey(
        Utilizador,
        on_delete=models.PROTECT,
        related_name="requisicoes_solicitadas",
        verbose_name="Médico Solicitante",
    )

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT,
        related_name="requisicoes_laboratorio",
        verbose_name="Hospital",
    )

    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.SET_NULL,
        related_name="requisicoes_laboratorio",
        verbose_name="Consulta de Origem",
        blank=True,
        null=True,
        help_text="Consulta médica que originou o pedido de exames, se aplicável.",
    )

    suspeita_clinica = models.CharField(
        "Suspeita Clínica",
        max_length=255,
        blank=True,
    )

    observacoes = models.TextField("Observações", blank=True)

    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.AGUARDANDO_COLHEITA,
    )

    criado_por = models.ForeignKey(
        Utilizador,
        on_delete=models.PROTECT,
        related_name="requisicoes_triadas",
        verbose_name="Registado por",
        help_text="Profissional que fez a triagem/receção do paciente.",
    )

    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    def __str__(self):
        return f"Requisição #{self.pk} - {self.paciente}"

    class Meta:
        verbose_name = "Requisição de Exames"
        verbose_name_plural = "Requisições de Exames"
        ordering = ["-criado_em"]