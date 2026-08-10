from django.db import models

from .paciente import Paciente


class EnderecoPaciente(models.Model):

    paciente = models.OneToOneField(
        Paciente,
        on_delete=models.CASCADE,
        related_name="endereco"
    )

    pais = models.CharField(
        "País",
        max_length=100,
        default="Angola"
    )

    provincia = models.CharField(
        "Província",
        max_length=100
    )

    municipio = models.CharField(
        "Município",
        max_length=100
    )

    comuna = models.CharField(
        "Comuna",
        max_length=100,
        blank=True
    )

    bairro = models.CharField(
        "Bairro",
        max_length=150,
        blank=True
    )

    rua = models.CharField(
        "Rua",
        max_length=150,
        blank=True
    )

    numero_casa = models.CharField(
        "Número",
        max_length=20,
        blank=True
    )

    referencia = models.TextField(
        "Referência",
        blank=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.provincia} - {self.municipio}"

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"