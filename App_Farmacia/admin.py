from django.contrib import admin

from .medicamento import Medicamento
from .lote import Lote


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ("nome", "principio_ativo", "concentracao", "forma_farmaceutica", "controlado", "ativo")
    list_filter = ("forma_farmaceutica", "controlado", "ativo")
    search_fields = ("nome", "principio_ativo", "codigo")
    ordering = ("nome",)


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ("medicamento", "hospital", "numero_lote", "validade", "quantidade")
    list_filter = ("hospital",)
    search_fields = ("medicamento__nome", "numero_lote")
    ordering = ("validade",)