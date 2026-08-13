from django.contrib import admin

from .medicamento import Medicamento
from .lote import Lote


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nome",
        "principio_ativo",
        "concentracao",
        "forma_farmaceutica",
        "unidade_medida",
        "controlado",
        "ativo",
    )
    list_filter = ("forma_farmaceutica", "unidade_medida", "controlado", "ativo")
    search_fields = ("codigo", "nome", "principio_ativo", "classe_terapeutica")
    ordering = ("nome",)
    list_editable = ("ativo",)
    readonly_fields = ("criado_em", "atualizado_em")

    fieldsets = (
        ("Identificação", {
            "fields": ("codigo", "nome", "principio_ativo", "concentracao")
        }),
        ("Classificação", {
            "fields": ("forma_farmaceutica", "unidade_medida", "classe_terapeutica", "controlado")
        }),
        ("Estado", {
            "fields": ("ativo",)
        }),
        ("Registo", {
            "fields": ("criado_em", "atualizado_em"),
            "classes": ("collapse",),
        }),
    )


class LoteVencidoFilter(admin.SimpleListFilter):
    title = "validade"
    parameter_name = "estado_validade"

    def lookups(self, request, model_admin):
        return (
            ("vencido", "Vencido"),
            ("a_vencer", "A vencer em 30 dias"),
            ("ok", "Dentro da validade"),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta

        hoje = timezone.localdate()
        if self.value() == "vencido":
            return queryset.filter(validade__lt=hoje)
        if self.value() == "a_vencer":
            return queryset.filter(validade__gte=hoje, validade__lte=hoje + timedelta(days=30))
        if self.value() == "ok":
            return queryset.filter(validade__gt=hoje + timedelta(days=30))
        return queryset


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = (
        "medicamento",
        "hospital",
        "numero_lote",
        "validade",
        "quantidade",
        "fornecedor",
    )
    list_filter = ("hospital", LoteVencidoFilter)
    search_fields = ("medicamento__nome", "medicamento__codigo", "numero_lote", "fornecedor")
    ordering = ("validade",)
    autocomplete_fields = ("medicamento",)
    readonly_fields = ("data_entrada", "criado_em", "atualizado_em")

    fieldsets = (
        ("Identificação do lote", {
            "fields": ("hospital", "medicamento", "numero_lote")
        }),
        ("Stock", {
            "fields": ("quantidade", "validade", "preco_custo_unitario", "fornecedor")
        }),
        ("Registo", {
            "fields": ("data_entrada", "criado_em", "atualizado_em"),
            "classes": ("collapse",),
        }),
    )