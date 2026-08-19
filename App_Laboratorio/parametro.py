from django.db import models


# Parâmetro é o que efectivamente recebe um resultado (ex.: Hemoglobina,
# Leucócitos). Um TipoExame (ex.: Hemograma Completo) tem vários
# parâmetros, ligados via ExameParametro — e o mesmo parâmetro pode
# aparecer em vários exames diferentes (ex.: Hemoglobina em Hemograma
# Completo E em Perfil Hematológico), por isso vive como catálogo global,
# tal como TipoExame.
#
# Os valores de referência NÃO ficam aqui — o parâmetro só guarda o
# "conceito" do resultado (nome, tipo, unidade, casas decimais). As
# referências por sexo/idade ficam em ValorReferencia, à parte, porque
# variam consoante o grupo demográfico do paciente.
class Parametro(models.Model):

    class TipoResultado(models.TextChoices):
        NUMERICO = "NUMERICO", "Numérico"
        TEXTO = "TEXTO", "Texto"
        POSITIVO_NEGATIVO = "POSITIVO_NEGATIVO", "Positivo/Negativo"
        SIM_NAO = "SIM_NAO", "Sim/Não"
        OPCOES = "OPCOES", "Opções"
        TITULO = "TITULO", "Título"
        DATA = "DATA", "Data"
        HORA = "HORA", "Hora"

    codigo = models.CharField(
        "Código",
        max_length=30,
        unique=True,
        help_text="Ex.: HGB",
    )

    nome = models.CharField(
        "Nome",
        max_length=150,
        help_text="Ex.: Hemoglobina",
    )

    nome_abreviado = models.CharField(
        "Nome Abreviado",
        max_length=30,
        blank=True,
        help_text="Ex.: Hb",
    )

    descricao = models.TextField(
        "Descrição",
        blank=True,
        help_text="Ex.: Concentração de hemoglobina no sangue",
    )

    tipo_resultado = models.CharField(
        "Tipo de Resultado",
        max_length=20,
        choices=TipoResultado.choices,
    )

    unidade = models.CharField(
        "Unidade",
        max_length=30,
        blank=True,
        help_text="Ex.: g/dL",
    )

    casas_decimais = models.PositiveSmallIntegerField(
        "Casas Decimais",
        null=True,
        blank=True,
        help_text="Só relevante para resultados Numéricos. Ex.: 1",
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

    def __str__(self):
        return f"{self.nome} ({self.codigo})"

    class Meta:
        verbose_name = "Parâmetro"
        verbose_name_plural = "Parâmetros"
        ordering = ["nome"]