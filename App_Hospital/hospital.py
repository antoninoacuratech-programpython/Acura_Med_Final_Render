from django.db import models
from uuid import uuid4

class Hospital(models.Model):
    uuid = models.UUIDField(
        default=uuid4,
        editable=False,
        unique=True
    )
    codigo = models.CharField(
        "Código",
        max_length=20,
        unique=True
    )
    nome = models.CharField(
        "Nome",
        max_length=200
    )
    sigla = models.CharField(
        "Sigla",
        max_length=30,
        blank=True
    )
    nif = models.CharField(
        "NIF",
        max_length=30,
        blank=True
    )
    telefone = models.CharField(
        "Telefone",
        max_length=20,
        blank=True
    )
    email = models.EmailField(
        "E-mail",
        blank=True
    )
    website = models.URLField(
        "Website",
        blank=True
    )
    pais = models.CharField(
        "País",
        max_length=100,
        default="Angola"
    )
    provincia = models.CharField(
        "Província",
        max_length=100
    )
    municipio = models.CharField(
        "Município",
        max_length=100
    )
    endereco = models.CharField(
        "Endereço",
        max_length=250,
        blank=True
    )
    logo = models.ImageField(
        "Logótipo",
        upload_to="hospital/logo/",
        blank=True,
        null=True
    )
    observacoes = models.TextField(
        "Observações",
        blank=True
    )
    ativo = models.BooleanField(
        "Ativo",
        default=True
    )
    criado_em = models.DateTimeField(
        "Criado em",
        auto_now_add=True
    )
    atualizado_em = models.DateTimeField(
        "Atualizado em",
        auto_now=True
    )

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    class Meta:
        verbose_name = "Hospital"
        verbose_name_plural = "Hospitais"
        ordering = ["nome"]
    ativo = models.BooleanField(
        default=True
    )
    criado_em = models.DateTimeField(
        auto_now_add=True
    )
    atualizado_em = models.DateTimeField(
        auto_now=True
    )
    def __str__(self):
        return self.nome
    class Meta:
        verbose_name = "Hospital"
        verbose_name_plural = "Hospitais"
        ordering = ["nome"]
        


