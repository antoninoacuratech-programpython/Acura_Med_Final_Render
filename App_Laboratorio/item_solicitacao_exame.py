from django.db import models

from .tipo_exame import TipoExame
from .solicitacao_exame import SolicitacaoExame


# Cada linha da solicitação: um exame específico. O resultado fica em
# texto livre porque cada TipoExame tem o seu próprio formato (números,
# texto qualitativo tipo "Negativo/Positivo", etc.) — não vale a pena
# tentar estruturar isso de forma genérica.
class ItemSolicitacaoExame(models.Model):

    solicitacao = models.ForeignKey(
        SolicitacaoExame,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Solicitação",
    )

    tipo_exame = models.ForeignKey(
        TipoExame,
        on_delete=models.PROTECT,
        related_name="itens_solicitados",
        verbose_name="Tipo de Exame",
    )

    observacoes = models.CharField(
        "Observações",
        max_length=255,
        blank=True,
    )

    resultado = models.TextField(
        "Resultado",
        blank=True,
    )

    data_colheita = models.DateTimeField(
        "Data da colheita",
        blank=True,
        null=True,
    )

    data_resultado = models.DateTimeField(
        "Data do resultado",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.tipo_exame.nome} — {self.solicitacao}"

    class Meta:
        verbose_name = "Item de Solicitação de Exame"
        verbose_name_plural = "Itens de Solicitação de Exame"