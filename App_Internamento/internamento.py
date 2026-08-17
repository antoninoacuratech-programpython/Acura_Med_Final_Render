from django.db import models

from .quarto import Quarto


class Internamento(models.Model):

    class Status(models.TextChoices):
        INTERNADO = "INTERNADO", "Internado"
        ALTA = "ALTA", "Alta"
        TRANSFERIDO = "TRANSFERIDO", "Transferido"
        CANCELADO = "CANCELADO", "Cancelado"

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
            f"— Quarto {self.quarto.numero}"
        )

    class Meta:
        verbose_name = "Internamento"
        verbose_name_plural = "Internamentos"
        ordering = ["-data_entrada"]