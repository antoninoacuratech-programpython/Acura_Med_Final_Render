from django.db import models
class Especialidade(models.Model):
    nome = models.CharField(
        "Nome",
        max_length=120,
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
    class Meta:
        verbose_name = "Especialidade"
        verbose_name_plural = "Especialidades"
        ordering = ["nome"]
    def __str__(self):
        return self.nome