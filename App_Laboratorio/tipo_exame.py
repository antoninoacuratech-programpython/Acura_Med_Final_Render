from django.db import models


# Catálogo de exames laboratoriais, comum a todos os hospitais da
# plataforma. É só a ficha técnica do exame — não guarda resultados nem
# solicitações, isso é feito por SolicitacaoExame/ItemSolicitacaoExame.
class TipoExame(models.Model):

    class Departamento(models.TextChoices):
        HEMATOLOGIA = "HEMATOLOGIA", "Hematologia"
        BIOQUIMICA = "BIOQUIMICA", "Bioquímica"
        IMUNOLOGIA = "IMUNOLOGIA", "Imunologia"
        MICROBIOLOGIA = "MICROBIOLOGIA", "Microbiologia"
        PARASITOLOGIA = "PARASITOLOGIA", "Parasitologia"
        URINALISE = "URINALISE", "Urinálise"
        COAGULACAO = "COAGULACAO", "Coagulação"
        HORMONIOS = "HORMONIOS", "Hormônios"
        SEROLOGIA = "SEROLOGIA", "Serologia"
        GENETICA = "GENETICA", "Genética"
        ANATOMIA_PATOLOGICA = "ANATOMIA_PATOLOGICA", "Anatomia Patológica"

    class Metodo(models.TextChoices):
        ESPECTROFOTOMETRIA = "ESPECTROFOTOMETRIA", "Espectrofotometria"
        IMUNOENSAIO = "IMUNOENSAIO", "Imunoensaio"
        ELISA = "ELISA", "ELISA"
        QUIMIOLUMINESCENCIA = "QUIMIOLUMINESCENCIA", "Quimioluminescência"
        ELETROQUIMIOLUMINESCENCIA = "ELETROQUIMIOLUMINESCENCIA", "Eletroquimioluminescência"
        PCR = "PCR", "PCR"
        MICROSCOPIA = "MICROSCOPIA", "Microscopia"
        CULTURA = "CULTURA", "Cultura"
        COLORIMETRIA = "COLORIMETRIA", "Colorimetria"
        IMUNOCROMATOGRAFIA = "IMUNOCROMATOGRAFIA", "Imunocromatografia"
        POTENCIOMETRIA = "POTENCIOMETRIA", "Potenciometria"
        TURBIDIMETRIA = "TURBIDIMETRIA", "Turbidimetria"
        CITOMETRIA_FLUXO = "CITOMETRIA_FLUXO", "Citometria de Fluxo"

    class TipoAmostra(models.TextChoices):
        SANGUE = "SANGUE", "Sangue"
        SORO = "SORO", "Soro"
        PLASMA = "PLASMA", "Plasma"
        URINA = "URINA", "Urina"
        FEZES = "FEZES", "Fezes"
        ESCARRO = "ESCARRO", "Escarro"
        SWAB = "SWAB", "Swab"
        SECRECAO = "SECRECAO", "Secreção"
        LCR = "LCR", "Líquido Cefalorraquidiano"
        LIQUIDO_PLEURAL = "LIQUIDO_PLEURAL", "Líquido Pleural"
        LIQUIDO_ASCITICO = "LIQUIDO_ASCITICO", "Líquido Ascítico"
        LIQUIDO_SINOVIAL = "LIQUIDO_SINOVIAL", "Líquido Sinovial"
        MEDULA_OSSEA = "MEDULA_OSSEA", "Medula Óssea"
        TECIDO = "TECIDO", "Tecido"

    class TipoResultado(models.TextChoices):
        NUMERICO = "NUMERICO", "Numérico"
        QUALITATIVO = "QUALITATIVO", "Qualitativo"
        MULTIPARAMETRO = "MULTIPARAMETRO", "Multiparâmetro"
        TEXTO_LIVRE = "TEXTO_LIVRE", "Texto Livre"

    codigo = models.CharField(
        "Código Interno",
        max_length=30,
        unique=True,
        help_text="Identificador único do exame dentro do sistema",
    )

    codigo_padronizado = models.CharField(
        "Código Padronizado",
        max_length=30,
        blank=True,
        help_text="Identificador de padrão externo (ex.: LOINC), quando aplicável",
    )

    departamento = models.CharField(
        "Departamento",
        max_length=30,
        choices=Departamento.choices,
    )

    nome = models.CharField(
        "Nome do Exame",
        max_length=150,
        help_text="Nome comercial/técnico apresentado no sistema",
    )

    nome_tecnico = models.CharField(
        "Nome Técnico",
        max_length=150,
        blank=True,
        help_text="Nome técnico/científico do exame",
    )

    metodo = models.CharField(
        "Método",
        max_length=30,
        choices=Metodo.choices,
        blank=True,
    )

    tipo_amostra = models.CharField(
        "Tipo de Amostra",
        max_length=30,
        choices=TipoAmostra.choices,
    )

    tipo_resultado = models.CharField(
        "Tipo de Resultado",
        max_length=20,
        choices=TipoResultado.choices,
        help_text="Define como o resultado será lançado",
    )

    # Não estão na especificação nova, mas mantidos porque já são usados
    # no ecrã de resultados do Laboratório (mostram a referência clínica
    # ao lado do valor lançado pelo técnico).
    valor_referencia = models.CharField(
        "Valor de Referência",
        max_length=150,
        blank=True,
        help_text="Ex.: 4.5 - 11.0, ou 'Negativo' para exames qualitativos",
    )

    unidade_medida = models.CharField(
        "Unidade de Medida",
        max_length=30,
        blank=True,
        help_text="Ex.: mg/dL, g/dL, x10⁹/L",
    )

    tempo_estimado = models.CharField(
        "Tempo de Resultado (TAT)",
        max_length=30,
        blank=True,
        help_text="Ex.: 24 horas, 3 dias",
    )

    instrucoes_preparacao = models.TextField(
        "Instruções de Preparação",
        blank=True,
        help_text="Orientações ao paciente antes da colheita",
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
        return self.nome

    class Meta:
        verbose_name = "Tipo de Exame"
        verbose_name_plural = "Tipos de Exame"
        ordering = ["nome"]