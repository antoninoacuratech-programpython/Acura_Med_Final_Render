from uuid import uuid4
from django.db import models
from django.utils import timezone
from App_Hospital.hospital import Hospital

class Paciente(models.Model):

    class Sexo(models.TextChoices):
        MASCULINO = "M", "Masculino"
        FEMININO = "F", "Feminino"

    class EstadoCivil(models.TextChoices):
        SOLTEIRO = "SOL", "Solteiro(a)"
        CASADO = "CAS", "Casado(a)"
        DIVORCIADO = "DIV", "Divorciado(a)"
        VIUVO = "VIU", "Viúvo(a)"
        UNIAO_FACTO = "UNI", "União de Facto"

    class EstadoPaciente(models.TextChoices):
        ATIVO = "ATIVO", "Ativo"
        INATIVO = "INATIVO", "Inativo"
        OBITO = "OBITO", "Óbito"
        ARQUIVADO = "ARQUIVADO", "Arquivado"
    uuid = models.UUIDField(
        default=uuid4,
        editable=False,
        unique=True
    )

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT,
        related_name="pacientes",
        verbose_name="Hospital"
    )

    codigo = models.CharField(
        "Código do Paciente",
        max_length=20,
        unique=True,
        editable=False
    )

    numero_processo = models.CharField(
        "Número do Processo",
        max_length=30,
        unique=True,
        editable=False
    )
    primeiro_nome = models.CharField(
        "Primeiro Nome",
        max_length=100
    )

    outros_nomes = models.CharField(
        "Outros Nomes",
        max_length=150,
        blank=True
    )

    ultimo_nome = models.CharField(
        "Apelido",
        max_length=100
    )

    nome_social = models.CharField(
        "Nome Social",
        max_length=200,
        blank=True
    )

    sexo = models.CharField(
        "Sexo",
        max_length=1,
        choices=Sexo.choices
    )

    data_nascimento = models.DateField(
        "Data de Nascimento"
    )

    estado_civil = models.CharField(
        "Estado Civil",
        max_length=5,
        choices=EstadoCivil.choices,
        blank=True
    )

    nacionalidade = models.CharField(
        "Nacionalidade",
        max_length=100,
        default="Angolana"
    )

    profissao = models.CharField(
        "Profissão",
        max_length=150,
        blank=True
    )

    fotografia = models.ImageField(
        "Fotografia",
        upload_to="pacientes/",
        blank=True,
        null=True
    )

    estado = models.CharField(
        "Estado",
        max_length=20,
        choices=EstadoPaciente.choices,
        default=EstadoPaciente.ATIVO
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    @property
    def nome_completo(self):
        return f"{self.primeiro_nome} {self.outros_nomes} {self.ultimo_nome}".replace("  ", " ").strip()

    @property
    def idade(self):
        hoje = timezone.now().date()

        idade = hoje.year - self.data_nascimento.year

        if (hoje.month, hoje.day) < (
            self.data_nascimento.month,
            self.data_nascimento.day,
        ):
            idade -= 1

        return idade

    def save(self, *args, **kwargs):

        if not self.codigo:

            ultimo = Paciente.objects.order_by("-id").first()

            if ultimo:
                numero = int(ultimo.codigo.replace("PAC", ""))
                numero += 1
            else:
                numero = 1

            self.codigo = f"PAC{numero:08d}"

        if not self.numero_processo:
            self.numero_processo = self.codigo

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.nome_completo}"

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ["primeiro_nome", "ultimo_nome"]