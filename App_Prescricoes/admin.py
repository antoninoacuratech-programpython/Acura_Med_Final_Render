from django.contrib import admin

from .prescricao_medicamento import PrescricaoMedicamento
from .item_prescricao import ItemPrescricao


class ItemPrescricaoInline(admin.TabularInline):
    model = ItemPrescricao
    extra = 0


@admin.register(PrescricaoMedicamento)
class PrescricaoMedicamentoAdmin(admin.ModelAdmin):
    list_display = ("id", "paciente", "medico", "status", "hospital", "criado_em")
    list_filter = ("status", "hospital", "criado_em")
    search_fields = ("paciente__primeiro_nome", "paciente__ultimo_nome", "paciente__codigo")
    ordering = ("-criado_em",)
    readonly_fields = ("criado_em", "atualizado_em")
    inlines = [ItemPrescricaoInline]