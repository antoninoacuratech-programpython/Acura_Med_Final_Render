from django.contrib import admin

from .models import Agendamento


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = (
        "paciente",
        "profissional",
        "data_hora",
        "status",
        "hospital",
    )

    list_filter = (
        "status",
        "hospital",
        "departamento",
        "especialidade",
    )

    search_fields = (
        "paciente__nome",
        "profissional__primeiro_nome",
        "profissional__ultimo_nome",
        "motivo",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    ordering = (
        "data_hora",
    )