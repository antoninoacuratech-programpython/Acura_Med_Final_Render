from django.db import models

from App_Usuarios.ultilizador import Utilizador
from .requisicao import Requisicao
from .tipo_exame import TipoExame
from .amostra import Amostra


class ExameSolicitado(models.Model):
    """Item de uma Requisição — um exame específico pedido pelo médico.

    É a "espinha dorsal" que atravessa as 3 fases: nasce na triagem
    (Pré-analítica), recebe uma Amostra na colheita (fim da
    Pré-analítica), é processado na fase Analítica (tecnico_responsavel,
    datas de início/conclusão) e termina ligado a um Resultado na fase
    Pós-analítica."""

    class Status(models.TextChoices):
        AGUARDANDO_COLHEITA = "aguardando_colheita", "Aguardando Colheita"
        COLETADO = "coletado", "Coletado"
        EM_ANALISE = "em_analise", "Em Análise"
        CONCLUIDO = "concluido", "Concluído"
        LIBERADO = "liberado", "Liberado"
        REJEITADO = "rejeitado", "Rejeitado"
        CANCELADO = "cancelado", "Cancelado"

    requisicao = models.ForeignKey(
        Requisicao,
        on_delete=models.CASCADE,
        related_name="exames_solicitados",
        verbose_name="Requisição",
    )

    tipo_exame = models.ForeignKey(
        TipoExame,
        on_delete=models.PROTECT,
        related_name="solicitacoes",
        verbose_name="Exame",
    )

    amostra = models.ForeignKey(
        Amostra,
        on_delete=models.SET_NULL,
        related_name="exames",
        verbose_name="Amostra",
        blank=True,
        null=True,
    )

    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.AGUARDANDO_COLHEITA,
    )

    tecnico_responsavel = models.ForeignKey(
        Utilizador,
        on_delete=models.SET_NULL,
        related_name="exames_processados",
        verbose_name="Técnico Responsável",
        blank=True,
        null=True,
    )

    data_inicio_analise = models.DateTimeField("Início da Análise", blank=True, null=True)
    data_conclusao_analise = models.DateTimeField("Conclusão da Análise", blank=True, null=True)

    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    def __str__(self):
        return f"{self.tipo_exame} - Requisição #{self.requisicao_id}"

    class Meta:
        verbose_name = "Exame Solicitado"
        verbose_name_plural = "Exames Solicitados"
        ordering = ["-criado_em"]