from django.db import models

from .perfil import Perfil
from .permissao import Permissao


class PerfilPermissao(models.Model):
    """
    Liga perfis às permissões.
    """

    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name="permissoes"
    )

    permissao = models.ForeignKey(
        Permissao,
        on_delete=models.CASCADE,
        related_name="perfis"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Perfil x Permissão"
        verbose_name_plural = "Perfis x Permissões"
        unique_together = ("perfil", "permissao")

    def __str__(self):
        return f"{self.perfil} → {self.permissao}"