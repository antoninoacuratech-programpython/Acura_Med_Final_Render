from django.db import models


# Catálogo de medicamentos, comum a todos os hospitais da plataforma
# (à semelhança de Especialidade). O controlo de quantidade e validade
# é feito por hospital através do model Lote — Medicamento é só a ficha
# técnica do produto, nunca guarda quantidade.
class Medicamento(models.Model):

    class FormaFarmaceutica(models.TextChoices):
        COMPRIMIDO = "COMPRIMIDO", "Comprimido"
        CAPSULA = "CAPSULA", "Cápsula"
        XAROPE = "XAROPE", "Xarope"
        SUSPENSAO = "SUSPENSAO", "Suspensão"
        INJETAVEL = "INJETAVEL", "Injetável"
        POMADA = "POMADA", "Pomada/Creme"
        GOTAS = "GOTAS", "Gotas"
        SUPOSITORIO = "SUPOSITORIO", "Supositório"
        SORO = "SORO", "Soro/Solução"
        OUTRO = "OUTRO", "Outro"

    class UnidadeMedida(models.TextChoices):
        COMPRIMIDO = "COMPRIMIDO", "Comprimido"
        CAPSULA = "CAPSULA", "Cápsula"
        ML = "ML", "Mililitro (ml)"
        MG = "MG", "Miligrama (mg)"
        AMPOLA = "AMPOLA", "Ampola"
        FRASCO = "FRASCO", "Frasco"
        UNIDADE = "UNIDADE", "Unidade"

    codigo = models.CharField(
        "Código",
        max_length=30,
        unique=True,
    )

    nome = models.CharField(
        "Nome comercial",
        max_length=150,
    )

    principio_ativo = models.CharField(
        "Princípio activo",
        max_length=150,
    )

    concentracao = models.CharField(
        "Concentração",
        max_length=50,
        blank=True,
        help_text="Ex.: 500mg, 250mg/5ml",
    )

    forma_farmaceutica = models.CharField(
        "Forma farmacêutica",
        max_length=20,
        choices=FormaFarmaceutica.choices,
    )

    unidade_medida = models.CharField(
        "Unidade de medida",
        max_length=20,
        choices=UnidadeMedida.choices,
    )

    classe_terapeutica = models.CharField(
        "Classe terapêutica",
        max_length=100,
        blank=True,
    )

    controlado = models.BooleanField(
        "Medicamento controlado",
        default=False,
        help_text="Requer receita/controlo reforçado (psicotrópicos, entorpecentes, etc.)",
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
        return f"{self.nome} ({self.concentracao})" if self.concentracao else self.nome

    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"
        ordering = ["nome"]