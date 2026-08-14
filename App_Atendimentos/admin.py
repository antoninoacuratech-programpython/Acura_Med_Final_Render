from django.contrib import admin

from .atendimento import Atendimento


@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = ("paciente", "profissional", "tipo_atendimento", "prioridade", "status", "agendamento", "criado_em")
    list_filter = ("status", "tipo_atendimento", "prioridade", "hospital")
    search_fields = ("paciente__primeiro_nome", "paciente__ultimo_nome", "paciente__codigo")
    ordering = ("-criado_em",)
    readonly_fields = ("criado_em", "atualizado_em")