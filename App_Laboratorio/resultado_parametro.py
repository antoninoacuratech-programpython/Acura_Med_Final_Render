from django.db import models

from .item_solicitacao_exame import ItemSolicitacaoExame
from .parametro import Parametro


# Guarda o valor lançado para CADA parâmetro de um exame Multiparâmetro,
# dentro de uma solicitação concreta. Para exames Numérico/Qualitativo/
# Texto Livre continua a usar-se ItemSolicitacaoExame.resultado
# directamente — isto só entra em jogo quando o exame tem parâmetros.
class ResultadoParametro(models.Model):

    item_solicitacao = models.ForeignKey(
        ItemSolicitacaoExame,
        on_delete=models.CASCADE,
        related_name="resultados_parametro",
        verbose_name="Item da Solicitação",
    )

    parametro = models.ForeignKey(
        Parametro,
        on_delete=models.PROTECT,
        related_name="resultados",
        verbose_name="Parâmetro",
    )

    valor = models.CharField(
        "Valor",
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return f"{self.parametro.nome} = {self.valor}"

    class Meta:
        verbose_name = "Resultado de Parâmetro"
        verbose_name_plural = "Resultados de Parâmetro"
        unique_together = ("item_solicitacao", "parametro")