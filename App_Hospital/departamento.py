from django.db import models
from .hospital import Hospital
class Departamento(models.Model):
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="departamentos"
    )
    nome = models.CharField(
        "Nome",
        max_length=100
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
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ["nome"]
        unique_together = ("hospital", "nome")
    def __str__(self):
        return self.nome