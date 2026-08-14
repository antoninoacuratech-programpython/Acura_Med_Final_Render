from django.db import models

from App_Hospital.hospital import Hospital
from App_Pacientes.paciente import Paciente
from App_Usuarios.ultilizador import Utilizador
from App_Usuarios.entidade_vinculada import EntidadeVinculada
from App_Agendamentos.agendamento import Agendamento


# Atendimento é a fila real de hoje — onde o paciente efectivamente está a
# ser (ou vai ser) visto. Um Atendimento pode nascer de duas formas:
#
#   1) Check-in de um Agendamento existente (paciente que marcou e chegou):
#      agendamento fica preenchido, os dados são copiados do agendamento.
#   2) Chegada directa, sem marcação prévia (walk-in): agendamento fica
#      NULL, os dados são preenchidos de raiz no modal "Novo Atendimento".
#
# Isto separa "quando o paciente disse que vinha" (Agendamento) de
# "o paciente está aqui agora, nesta fila, neste estado" (Atendimento) —
# a Prescrição liga-se sempre a um Atendimento, nunca directamente a um
# Agendamento, porque nem todo o atendimento tem uma marcação por trás.
class Atendimento(models.Model):

    class Status(models.TextChoices):
        AGUARDANDO = "aguardando", "Aguardando"
        EM_ATENDIMENTO = "em_atendimento", "Em Atendimento"
        CONCLUIDO = "concluido", "Concluído"
        CANCELADO = "cancelado", "Cancelado"

    class TipoPlano(models.TextChoices):
        CONVENIO = "convenio", "Convênio"
        PARTICULAR = "particular", "Particular"

    class SubtipoConvenio(models.TextChoices):
        EMPRESA = "empresa", "Empresa"
        SEGURADORA = "seguradora", "Seguradora"

    class Prioridade(models.TextChoices):
        NORMAL = "Normal", "Normal"
        URGENTE = "Urgente", "Urgente"
        PREFERENCIAL = "Preferencial", "Preferencial (Idosos/Gestantes)"
        EMERGENCIA = "Emergência", "Emergência"

    class TipoAtendimento(models.TextChoices):
        CONSULTA_GERAL = "Consulta Geral", "Consulta Geral"
        ESPECIALIDADE = "Especialidade", "Especialidade Médica"
        EXAMES = "Exames Laboratoriais", "Exames Laboratoriais"
        TRIAGEM = "Triagem / Urgência", "Triagem / Urgência"
        RETORNO = "Retorno", "Retorno"

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT,
        related_name="atendimentos",
        verbose_name="Hospital",
    )

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="atendimentos",
        verbose_name="Paciente",
    )

    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.SET_NULL,
        related_name="atendimentos",
        verbose_name="Agendamento de origem",
        blank=True,
        null=True,
        help_text="Vazio quando o paciente chega directamente, sem marcação prévia.",
    )

    profissional = models.ForeignKey(
        Utilizador,
        on_delete=models.PROTECT,
        related_name="atendimentos",
        verbose_name="Profissional",
    )

    entidade_vinculada = models.ForeignKey(
        EntidadeVinculada,
        on_delete=models.SET_NULL,
        related_name="atendimentos",
        verbose_name="Entidade Vinculada",
        blank=True,
        null=True,
    )

    tipo_plano = models.CharField(
        "Tipo de Plano",
        max_length=20,
        choices=TipoPlano.choices,
        default=TipoPlano.PARTICULAR,
    )

    subtipo_convenio = models.CharField(
        "Subtipo de Convénio",
        max_length=20,
        choices=SubtipoConvenio.choices,
        blank=True,
    )

    prioridade = models.CharField(
        "Prioridade",
        max_length=20,
        choices=Prioridade.choices,
        default=Prioridade.NORMAL,
    )

    tipo_atendimento = models.CharField(
        "Tipo de Atendimento",
        max_length=30,
        choices=TipoAtendimento.choices,
    )

    status = models.CharField(
        "Estado",
        max_length=20,
        choices=Status.choices,
        default=Status.AGUARDANDO,
    )

    criado_por = models.ForeignKey(
        Utilizador,
        on_delete=models.PROTECT,
        related_name="atendimentos_criados",
        verbose_name="Criado por",
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
        return f"{self.paciente} — {self.get_status_display()}"

    class Meta:
        verbose_name = "Atendimento"
        verbose_name_plural = "Atendimentos"
        ordering = ["-criado_em"]