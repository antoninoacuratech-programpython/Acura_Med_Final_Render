from django.db import models

from App_Hospital.hospital import Hospital


# Nave (pavilhão/ala) do hospital — agrupa vários Quartos. É por hospital,
# não global, porque cada hospital tem a sua própria estrutura física.
class Nave(models.Model):

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT,
        related_name="naves",
        verbose_name="Hospital",
    )

    nome = models.CharField(
        "Nome",
        max_length=100,
        help_text="Ex.: Nave A, Pediatria, Maternidade",
    )

    descricao = models.CharField(
        "Descrição",
        max_length=255,
        blank=True,
    )

    ativa = models.BooleanField(
        "Activa",
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
        return self.nome

    class Meta:
        verbose_name = "Nave"
        verbose_name_plural = "Naves"
        ordering = ["nome"]
        unique_together = ("hospital", "nome")
