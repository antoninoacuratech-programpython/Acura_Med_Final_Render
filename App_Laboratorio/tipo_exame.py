from django.db import models


# Catálogo de exames laboratoriais, comum a todos os hospitais da
# plataforma (mesmo padrão de Medicamento na Farmácia). É só a ficha
# técnica do exame — não guarda resultados nem solicitações, isso é
# feito por outros models que se ligam a este.
class TipoExame(models.Model):

    class Categoria(models.TextChoices):
        HEMATOLOGIA = "HEMATOLOGIA", "Hematologia"
        BIOQUIMICA = "BIOQUIMICA", "Bioquímica"
        MICROBIOLOGIA = "MICROBIOLOGIA", "Microbiologia"
        IMUNOLOGIA = "IMUNOLOGIA", "Imunologia"
        UROANALISE = "UROANALISE", "Uroanálise"
        PARASITOLOGIA = "PARASITOLOGIA", "Parasitologia"
        HORMONAL = "HORMONAL", "Hormonal"
        OUTRO = "OUTRO", "Outro"

    class TipoAmostra(models.TextChoices):
        SANGUE = "SANGUE", "Sangue"
        URINA = "URINA", "Urina"
        FEZES = "FEZES", "Fezes"
        SORO = "SORO", "Soro"
        PLASMA = "PLASMA", "Plasma"
        SECRECAO = "SECRECAO", "Secreção"
        LIQUOR = "LIQUOR", "Líquor"
        OUTRA = "OUTRA", "Outra"

    codigo = models.CharField(
        "Código",
        max_length=30,
        unique=True,
    )

    nome = models.CharField(
        "Nome do exame",
        max_length=150,
    )

    categoria = models.CharField(
        "Categoria",
        max_length=20,
        choices=Categoria.choices,
    )

    tipo_amostra = models.CharField(
        "Tipo de amostra",
        max_length=20,
        choices=TipoAmostra.choices,
    )

    valor_referencia = models.CharField(
        "Valor de referência",
        max_length=150,
        blank=True,
        help_text="Ex.: 4.5 - 11.0, ou 'Negativo' para exames qualitativos",
    )

    unidade_medida = models.CharField(
        "Unidade de medida",
        max_length=30,
        blank=True,
        help_text="Ex.: mg/dL, g/dL, x10⁹/L",
    )

    tempo_estimado_horas = models.PositiveIntegerField(
        "Tempo estimado de resultado (horas)",
        blank=True,
        null=True,
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