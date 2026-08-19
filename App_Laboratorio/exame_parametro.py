from django.db import models

from .tipo_exame import TipoExame
from .parametro import Parametro


# Liga um TipoExame aos seus Parametros — o mesmo parâmetro pode
# pertencer a vários exames diferentes (ex.: Hemoglobina em Hemograma
# Completo e em Perfil Hematológico), por isso não dá para pôr uma FK
# directa de Parametro para TipoExame; precisa desta tabela no meio.
class ExameParametro(models.Model):

    tipo_exame = models.ForeignKey(
        TipoExame,
        on_delete=models.CASCADE,
        related_name="exame_parametros",
        verbose_name="Tipo de Exame",
    )

    parametro = models.ForeignKey(
        Parametro,
        on_delete=models.PROTECT,
        related_name="exame_parametros",
        verbose_name="Parâmetro",
    )

    ordem = models.PositiveIntegerField(
        "Ordem de Exibição",
        default=0,
    )

    subgrupo = models.CharField(
        "Subgrupo",
        max_length=100,
        blank=True,
        help_text="Ex.: Série Vermelha, Série Branca — para agrupar parâmetros no laudo",
    )

    obrigatorio = models.BooleanField(
        "Obrigatório",
        default=True,
    )

    exibir_no_laudo = models.BooleanField(
        "Exibir no Laudo",
        default=True,
    )

    permitir_resultado_manual = models.BooleanField(
        "Permitir Resultado Manual",
        default=True,
    )

    # Overrides opcionais — se vazios, usa-se o método/unidade do próprio
    # Parametro. Só se preenche aqui quando este exame específico precisa
    # de algo diferente do padrão do parâmetro.
    metodo = models.CharField(
        "Método (substitui o do Parâmetro, se preenchido)",
        max_length=30,
        choices=TipoExame.Metodo.choices,
        blank=True,
    )

    unidade = models.CharField(
        "Unidade (substitui a do Parâmetro, se preenchida)",
        max_length=30,
        blank=True,
    )

    def __str__(self):
        return f"{self.tipo_exame.nome} — {self.parametro.nome}"

    class Meta:
        verbose_name = "Parâmetro do Exame"
        verbose_name_plural = "Parâmetros do Exame"
        ordering = ["tipo_exame__nome", "ordem"]
        unique_together = ("tipo_exame", "parametro")