from django.db import models

from App_Pacientes.paciente import Paciente
from App_Hospital.hospital import Hospital
from App_Hospital.departamento import Departamento
from App_Hospital.especialidade import Especialidade
from App_Usuarios.ultilizador import Utilizador


class Agendamento(models.Model):

    class Status(models.TextChoices):
        AGENDADO = "agendado", "Agendado"
        CONFIRMADO = "confirmado", "Confirmado"
        EM_ATENDIMENTO = "em_atendimento", "Em Atendimento"
        CONCLUIDO = "concluido", "Concluído"
        CANCELADO = "cancelado", "Cancelado"
        FALTA = "falta", "Falta"

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="agendamentos",
        verbose_name="Paciente",
    )

    profissional = models.ForeignKey(
        Utilizador,
        on_delete=models.PROTECT,
        related_name="agendamentos",
        verbose_name="Profissional",
    )

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT,
        related_name="agendamentos",
        verbose_name="Hospital",
    )

    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        related_name="agendamentos",
        verbose_name="Departamento",
        blank=True,
        null=True,
    )

    especialidade = models.ForeignKey(
        Especialidade,
        on_delete=models.SET_NULL,
        related_name="agendamentos",
        verbose_name="Especialidade",
        blank=True,
        null=True,
    )

    data_hora = models.DateTimeField("Data e Hora")

    duracao_minutos = models.PositiveIntegerField("Duração (min)", default=30)

    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.AGENDADO,
    )

    motivo = models.CharField("Motivo", max_length=200)

    observacoes = models.TextField("Observações", blank=True)

    criado_por = models.ForeignKey(
        Utilizador,
        on_delete=models.PROTECT,
        related_name="agendamentos_criados",
        verbose_name="Criado por",
    )

    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    def __str__(self):
        return f"{self.paciente} - {self.data_hora:%d/%m/%Y %H:%M}"

    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ["data_hora"]