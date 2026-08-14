from django.contrib import admin

from .atendimento import Atendimento
from .consulta import Consulta


@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = ("paciente", "profissional", "tipo_atendimento", "prioridade", "status", "agendamento", "criado_em")
    list_filter = ("status", "tipo_atendimento", "prioridade", "hospital")
    search_fields = ("paciente__primeiro_nome", "paciente__ultimo_nome", "paciente__codigo")
    ordering = ("-criado_em",)
    readonly_fields = ("criado_em", "atualizado_em")


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ("atendimento", "conduta", "rascunho", "criado_em")
    list_filter = ("conduta", "rascunho")
    search_fields = ("atendimento__paciente__primeiro_nome", "atendimento__paciente__ultimo_nome")
    ordering = ("-criado_em",)
    readonly_fields = ("criado_em", "atualizado_em")