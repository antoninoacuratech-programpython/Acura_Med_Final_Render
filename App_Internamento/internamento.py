from django.db import models

from App_Hospital.hospital import Hospital
from App_Usuarios.ultilizador import Utilizador
from App_Atendimentos.atendimento import Atendimento
from .quarto import Quarto


# Internamento liga-se sempre a um Atendimento (1-para-1: um atendimento
# só pode gerar um internamento), tal como PrescricaoMedicamento e
# SolicitacaoExame já se ligam. O "hospital" fica aqui também, mesmo
# sendo derivável via quarto.nave.hospital, porque é o mesmo padrão usado
# em todo o resto do sistema (Dispensacao, Atendimento, etc.) — evita
# joins extra em todas as queries filtradas por hospital do utilizador.
class Internamento(models.Model):

    class Status(models.TextChoices):
        INTERNADO = "INTERNADO", "Internado"
        ALTA = "ALTA", "Alta"
        TRANSFERIDO = "TRANSFERIDO", "Transferido"
        CANCELADO = "CANCELADO", "Cancelado"

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT,
        related_name="internamentos",
        verbose_name="Hospital",
    )

    atendimento = models.OneToOneField(
        Atendimento,
        on_delete=models.PROTECT,
        related_name="internamento",
        verbose_name="Atendimento",
    )

    paciente = models.ForeignKey(
        "App_Pacientes.Paciente",
        on_delete=models.PROTECT,
        related_name="internamentos",
        verbose_name="Paciente",
    )

    quarto = models.ForeignKey(
        Quarto,
        on_delete=models.PROTECT,
        related_name="internamentos",
        verbose_name="Quarto",
    )

    medico_responsavel = models.ForeignKey(
        Utilizador,
        on_delete=models.PROTECT,
        related_name="internamentos_responsavel",
        verbose_name="Médico Responsável",
    )

    data_entrada = models.DateTimeField(
        "Data de entrada",
        auto_now_add=True,
    )

    data_alta = models.DateTimeField(
        "Data de alta",
        null=True,
        blank=True,
    )

    status = models.CharField(
        "Estado",
        max_length=20,
        choices=Status.choices,
        default=Status.INTERNADO,
    )

    motivo = models.TextField(
        "Motivo do internamento",
        blank=True,
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
        return (
            f"{self.paciente.nome_completo} "
            f"— Quarto {self.quarto.numero} ({self.get_status_display()})"
        )

    class Meta:
        verbose_name = "Internamento"
        verbose_name_plural = "Internamentos"
        ordering = ["-data_entrada"]