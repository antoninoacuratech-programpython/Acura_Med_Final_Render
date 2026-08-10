from django.db import models


class Perfil(models.Model):

    nome = models.CharField(
        "Nome",
        max_length=100,
        unique=True
    )

    descricao = models.TextField(
        "Descrição",
        blank=True
    )

    ativo = models.BooleanField(
        "Ativo",
        default=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"
        ordering = ["nome"]