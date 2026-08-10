from django.db import models

from .paciente import Paciente


class DocumentoPaciente(models.Model):

    class TipoDocumento(models.TextChoices):
        BI = "BI", "Bilhete de Identidade"
        PASSAPORTE = "PASSAPORTE", "Passaporte"
        NIF = "NIF", "NIF"
        CARTAO_RESIDENTE = "CARTAO_RESIDENTE", "Cartão de Residente"
        OUTRO = "OUTRO", "Outro"

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="documentos",
        verbose_name="Paciente"
    )

    tipo = models.CharField(
        "Tipo",
        max_length=30,
        choices=TipoDocumento.choices
    )

    numero = models.CharField(
        "Número",
        max_length=50
    )

    data_emissao = models.DateField(
        "Data de Emissão",
        blank=True,
        null=True
    )

    data_validade = models.DateField(
        "Data de Validade",
        blank=True,
        null=True
    )

    emitido_por = models.CharField(
        "Emitido por",
        max_length=150,
        blank=True
    )

    principal = models.BooleanField(
        "Documento Principal",
        default=False
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tipo} - {self.numero}"

    class Meta:
        verbose_name = "Documento do Paciente"
        verbose_name_plural = "Documentos dos Pacientes"
        ordering = ["tipo"]