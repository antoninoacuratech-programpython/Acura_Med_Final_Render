from django.db import models

from App_Usuarios.ultilizador import Utilizador
from .requisicao import Requisicao


class LivroSaida(models.Model):
    """Fase Pós-analítica — Livro de Saídas.

    Regista a entrega/liberação dos resultados de uma requisição a
    quem os for levantar (o próprio paciente ou um responsável),
    equivalente digital do "livro de saídas" físico do laboratório."""

    requisicao = models.OneToOneField(
        Requisicao,
        on_delete=models.CASCADE,
        related_name="livro_saida",
        verbose_name="Requisição",
    )

    entregue_em = models.DateTimeField("Entregue em", auto_now_add=True)

    entregue_por = models.ForeignKey(
        Utilizador,
        on_delete=models.PROTECT,
        related_name="entregas_realizadas",
        verbose_name="Entregue por",
    )

    recebido_por = models.CharField(
        "Recebido por",
        max_length=150,
        help_text="Nome de quem retirou o resultado (paciente ou responsável).",
    )

    documento_recebedor = models.CharField(
        "Documento de Identificação",
        max_length=50,
        blank=True,
    )

    observacoes = models.TextField("Observações", blank=True)

    def __str__(self):
        return f"Saída - Requisição #{self.requisicao_id}"

    class Meta:
        verbose_name = "Registo de Saída"
        verbose_name_plural = "Livro de Saídas"
        ordering = ["-entregue_em"]