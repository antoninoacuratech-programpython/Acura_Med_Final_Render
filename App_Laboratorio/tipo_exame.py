from django.db import models


class TipoExame(models.Model):
    """Catálogo de exames que o laboratório pode realizar. Cada exame
    define que tipo de amostra precisa e as características que guiam
    a fase pré-analítica (preparo do paciente) e a fase analítica
    (tempo estimado, valores de referência)."""

    class Categoria(models.TextChoices):
        HEMATOLOGIA = "hematologia", "Hematologia"
        BIOQUIMICA = "bioquimica", "Bioquímica"
        MICROBIOLOGIA = "microbiologia", "Microbiologia"
        IMUNOLOGIA = "imunologia", "Imunologia"
        UROANALISE = "uroanalise", "Uroanálise"
        PARASITOLOGIA = "parasitologia", "Parasitologia"
        HORMONAL = "hormonal", "Hormonal"
        OUTRO = "outro", "Outro"

    class TipoAmostra(models.TextChoices):
        SANGUE = "sangue", "Sangue"
        URINA = "urina", "Urina"
        FEZES = "fezes", "Fezes"
        ESCARRO = "escarro", "Escarro"
        SWAB = "swab", "Swab"
        LIQUIDO_CORPORAL = "liquido_corporal", "Líquido Corporal"
        OUTRO = "outro", "Outro"

    nome = models.CharField("Nome", max_length=150)

    codigo = models.CharField("Código", max_length=30, unique=True)

    categoria = models.CharField(
        "Categoria",
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.OUTRO,
    )

    tipo_amostra = models.CharField(
        "Tipo de Amostra",
        max_length=20,
        choices=TipoAmostra.choices,
        default=TipoAmostra.SANGUE,
    )

    preparo_necessario = models.TextField(
        "Preparo Necessário",
        blank=True,
        help_text="Ex.: jejum de 8 horas, suspender medicação X, etc.",
    )

    tempo_estimado_horas = models.PositiveIntegerField(
        "Tempo Estimado (horas)",
        default=24,
    )

    valores_referencia = models.TextField(
        "Valores de Referência",
        blank=True,
    )

    ativo = models.BooleanField("Ativo", default=True)

    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.codigo})"

    class Meta:
        verbose_name = "Tipo de Exame"
        verbose_name_plural = "Tipos de Exame"
        ordering = ["nome"]