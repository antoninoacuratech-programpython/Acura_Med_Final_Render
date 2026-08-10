from django.db import models

# as permissões são representadas por esta classe, que contém campos para nome, código, descrição, status de atividade e timestamps de criação e atualização. A classe também define a representação em string e metadados para exibição amigável no Django Admin.
class Permissao(models.Model):
    nome = models.CharField(
        "Nome",
        max_length=150,
        unique=True
    )

    codigo = models.CharField(
        "Código",
        max_length=100,
        unique=True
    )

    descricao = models.TextField(
        "Descrição",
        blank=True
    )

    ativo = models.BooleanField(
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
        verbose_name = "Permissão"
        verbose_name_plural = "Permissões"
        ordering = ["nome"]