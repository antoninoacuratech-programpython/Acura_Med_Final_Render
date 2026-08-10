from django.db import models

from .paciente import Paciente


class ContactoPaciente(models.Model):

    class TipoContacto(models.TextChoices):
        TELEFONE = "TELEFONE", "Telefone"
        TELEMOVEL = "TELEMOVEL", "Telemóvel"
        EMAIL = "EMAIL", "E-mail"
        WHATSAPP = "WHATSAPP", "WhatsApp"

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="contactos"
    )

    tipo = models.CharField(
        max_length=20,
        choices=TipoContacto.choices
    )

    contacto = models.CharField(
        max_length=120
    )

    principal = models.BooleanField(
        default=False
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.contacto

    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"