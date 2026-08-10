from uuid import uuid4
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from App_Hospital.hospital import Hospital
from App_Hospital.departamento import Departamento
from App_Hospital.especialidade import Especialidade
from .perfil import Perfil
from .managers import UtilizadorManager

#Classe utilizador que representa um utilizador do sistema, com campos para informações pessoais, hospital, perfil, departamento e especialidade. Herda de AbstractBaseUser e PermissionsMixin para fornecer funcionalidades de autenticação e permissões.
class Utilizador(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(
        default=uuid4,
        editable=False,
        unique=True
    )

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.PROTECT,
        related_name="utilizadores",
        verbose_name="Hospital",
        blank=True,
        null=True
    )

    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.PROTECT,
        related_name="utilizadores",
        verbose_name="Perfil",
        blank=True,
        null=True
    )

    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        related_name="utilizadores",
        verbose_name="Departamento",
        blank=True,
        null=True
    )

    especialidade = models.ForeignKey(
        Especialidade,
        on_delete=models.PROTECT,
        related_name="utilizadores",
        verbose_name="Especialidade",
        blank=True,
        null=True
    )

    primeiro_nome = models.CharField(
        "Primeiro Nome",
        max_length=100
    )

    ultimo_nome = models.CharField(
        "Apelido",
        max_length=100
    )

    email = models.EmailField(
        "E-mail",
        unique=True
    )

    telefone = models.CharField(
        "Telefone",
        max_length=20,
        blank=True
    )

    fotografia = models.ImageField(
        "Fotografia",
        upload_to="utilizadores/",
        blank=True,
        null=True
    )

    cargo = models.CharField(
        "Cargo",
        max_length=100,
        blank=True
    )

    is_active = models.BooleanField(
        "Ativo",
        default=True
    )

    is_staff = models.BooleanField(
        "Membro da Equipa",
        default=False
    )

    criado_em = models.DateTimeField(
        "Criado em",
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        "Atualizado em",
        auto_now=True
    )

    objects = UtilizadorManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "primeiro_nome",
        "ultimo_nome",
    ]

    @property
    def nome_completo(self):
        return f"{self.primeiro_nome} {self.ultimo_nome}"

    def __str__(self):
        return f"{self.nome_completo} ({self.email})"

    class Meta:
        verbose_name = "Utilizador"
        verbose_name_plural = "Utilizadores"
        ordering = ["primeiro_nome", "ultimo_nome"]