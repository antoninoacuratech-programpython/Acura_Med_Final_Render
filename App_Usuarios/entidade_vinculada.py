from django.db import models


# Entidade externa que pode ser vinculada a um paciente no acto de cadastro
# — empresa/hospital parceiro, seguradora, médico encaminhador ou
# colaborador interno responsável pela indicação. Substitui o antigo mock
# local (entidadesMock) que existia só no frontend.
class EntidadeVinculada(models.Model):

    class Tipo(models.TextChoices):
        EMPRESA = "EMPRESA", "Empresa"
        SEGURADORA = "SEGURADORA", "Seguradora"
        MEDICO = "MEDICO", "Médico"
        COLABORADOR = "COLABORADOR", "Colaborador"

    nome = models.CharField(
        "Nome",
        max_length=150,
    )

    tipo = models.CharField(
        "Tipo",
        max_length=20,
        choices=Tipo.choices,
    )

    contacto = models.CharField(
        "Contacto",
        max_length=100,
        blank=True,
    )

    ativo = models.BooleanField(
        "Activo",
        default=True,
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
        return f"{self.nome} ({self.get_tipo_display()})"

    class Meta:
        verbose_name = "Entidade Vinculada"
        verbose_name_plural = "Entidades Vinculadas"
        ordering = ["nome"]