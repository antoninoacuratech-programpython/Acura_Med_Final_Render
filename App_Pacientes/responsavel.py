from django.db import models

from .paciente import Paciente


class ResponsavelPaciente(models.Model):

    class Parentesco(models.TextChoices):
        PAI = "PAI", "Pai"
        MAE = "MAE", "Mãe"
        CONJUGE = "CONJUGE", "Cônjuge"
        FILHO = "FILHO", "Filho(a)"
        IRMAO = "IRMAO", "Irmão(ã)"
        TIO = "TIO", "Tio(a)"
        AVO = "AVO", "Avô/Avó"
        AMIGO = "AMIGO", "Amigo(a)"
        OUTRO = "OUTRO", "Outro"

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="responsaveis"
    )

    nome = models.CharField(
        "Nome",
        max_length=200
    )

    parentesco = models.CharField(
        "Parentesco",
        max_length=20,
        choices=Parentesco.choices
    )

    telefone = models.CharField(
        "Telefone",
        max_length=30
    )

    email = models.EmailField(
        "E-mail",
        blank=True
    )

    endereco = models.CharField(
        "Endereço",
        max_length=250,
        blank=True
    )

    contacto_emergencia = models.BooleanField(
        "Contacto de Emergência",
        default=False
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Responsável"
        verbose_name_plural = "Responsáveis"