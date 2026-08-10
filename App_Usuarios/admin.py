from django.contrib import admin
from .perfil import Perfil
from .permissao import Permissao
from .perfil_permissao import PerfilPermissao
from .ultilizador import Utilizador

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "ativo",
        "criado_em",
    )

    list_filter = (
        "ativo",
    )

    search_fields = (
        "nome",
        "descricao",
    )

    ordering = (
        "nome",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )


@admin.register(Permissao)
class PermissaoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nome",
        "ativo",
        "criado_em",
    )

    list_filter = (
        "ativo",
    )

    search_fields = (
        "codigo",
        "nome",
        "descricao",
    )

    ordering = (
        "nome",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )


@admin.register(PerfilPermissao)
class PerfilPermissaoAdmin(admin.ModelAdmin):
    list_display = (
        "perfil",
        "permissao",
        "criado_em",
    )

    list_filter = (
        "perfil",
    )

    search_fields = (
        "perfil__nome",
        "permissao__nome",
        "permissao__codigo",
    )

    autocomplete_fields = (
        "perfil",
        "permissao",
    )

    readonly_fields = (
        "criado_em",
    )


@admin.register(Utilizador)
class UtilizadorAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "nome_completo",
        "hospital",
        "perfil",
        "departamento",
        "especialidade",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "hospital",
        "perfil",
        "departamento",
        "especialidade",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "primeiro_nome",
        "ultimo_nome",
        "email",
        "telefone",
    )

    readonly_fields = (
        "uuid",
        "criado_em",
        "atualizado_em",
    )

    ordering = (
        "primeiro_nome",
        "ultimo_nome",
    )

    fieldsets = (
        (
            "Informações Gerais",
            {
                "fields": (
                    "uuid",
                    "hospital",
                    "perfil",
                    "departamento",
                    "especialidade",
                )
            },
        ),
        (
            "Dados Pessoais",
            {
                "fields": (
                    "primeiro_nome",
                    "ultimo_nome",
                    "email",
                    "telefone",
                    "cargo",
                    "fotografia",
                )
            },
        ),
        (
            "Permissões do Django",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Datas",
            {
                "fields": (
                    "criado_em",
                    "atualizado_em",
                )
            },
        ),
    )