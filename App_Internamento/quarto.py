from django.db import models

from .nave import Nave


# Quarto dentro de uma Nave. Não há leitos numerados individualmente —
# cada quarto tem uma capacidade (nº máximo de internantes em simultâneo),
# e a disponibilidade é calculada a partir de quantos internamentos
# activos existem ligados a este quarto (ver Internamento, passo 2).
class Quarto(models.Model):

    class Tipo(models.TextChoices):
        ENFERMARIA = "ENFERMARIA", "Enfermaria"
        INDIVIDUAL = "INDIVIDUAL", "Individual"
        UCI = "UCI", "UCI / Cuidados Intensivos"
        ISOLAMENTO = "ISOLAMENTO", "Isolamento"
        OUTRO = "OUTRO", "Outro"

    nave = models.ForeignKey(
        Nave,
        on_delete=models.PROTECT,
        related_name="quartos",
        verbose_name="Nave",
    )

    numero = models.CharField(
        "Número do Quarto",
        max_length=20,
    )

    tipo = models.CharField(
        "Tipo",
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.ENFERMARIA,
    )

    capacidade = models.PositiveIntegerField(
        "Capacidade (nº de internantes)",
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

    @property
    def ocupados(self):
        # Import local para evitar import circular — Internamento (passo 2)
        # ainda vai referenciar Quarto.
        from .internamento import Internamento
        return self.internamentos.filter(status=Internamento.Status.INTERNADO).count()

    @property
    def vagas_disponiveis(self):
        return max(self.capacidade - self.ocupados, 0)

    def __str__(self):
        return f"{self.nave.nome} — Quarto {self.numero}"

    class Meta:
        verbose_name = "Quarto"
        verbose_name_plural = "Quartos"
        ordering = ["nave__nome", "numero"]
        unique_together = ("nave", "numero")
