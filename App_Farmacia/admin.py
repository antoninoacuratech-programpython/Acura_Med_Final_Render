from django.contrib import admin

from .medicamento import Medicamento
from .lote import Lote
from .movimento_stock import MovimentoStock
from .dispensacao import Dispensacao, ItemDispensacao
from .requisicao_interna import RequisicaoInterna
from .item_requisicao_interna import ItemRequisicaoInterna


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo", "nome", "principio_ativo", "concentracao",
        "forma_farmaceutica", "unidade_medida", "controlado", "ativo",
    )
    list_filter = ("forma_farmaceutica", "unidade_medida", "controlado", "ativo")
    search_fields = ("codigo", "nome", "principio_ativo", "classe_terapeutica")
    ordering = ("nome",)
    list_editable = ("ativo",)
    readonly_fields = ("criado_em", "atualizado_em")


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
    list_display = ("medicamento", "hospital", "numero_lote", "validade", "quantidade", "fornecedor")
    list_filter = ("hospital", LoteVencidoFilter)
    search_fields = ("medicamento__nome", "medicamento__codigo", "numero_lote", "fornecedor")
    ordering = ("validade",)
    autocomplete_fields = ("medicamento",)
    readonly_fields = ("data_entrada", "criado_em", "atualizado_em")


@admin.register(MovimentoStock)
class MovimentoStockAdmin(admin.ModelAdmin):
    list_display = ("lote", "tipo", "quantidade", "utilizador", "referencia", "criado_em")
    list_filter = ("tipo", "criado_em")
    search_fields = ("lote__numero_lote", "lote__medicamento__nome", "referencia")
    ordering = ("-criado_em",)
    readonly_fields = ("criado_em",)
    # Movimentos são sempre gerados pelo sistema (cadastrar_lote, dispensar_medicamento),
    # nunca criados/editados à mão — o admin serve só para consulta e auditoria.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ItemDispensacaoInline(admin.TabularInline):
    model = ItemDispensacao
    extra = 0
    readonly_fields = ("lote", "quantidade")
    can_delete = False


@admin.register(Dispensacao)
class DispensacaoAdmin(admin.ModelAdmin):
    list_display = ("medicamento", "paciente", "quantidade", "farmaceutico", "hospital", "criado_em")
    list_filter = ("hospital", "criado_em")
    search_fields = ("medicamento__nome", "paciente__primeiro_nome", "paciente__ultimo_nome", "paciente__codigo")
    ordering = ("-criado_em",)
    readonly_fields = ("criado_em",)
    inlines = [ItemDispensacaoInline]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ItemRequisicaoInternaInline(admin.TabularInline):
    model = ItemRequisicaoInterna
    extra = 0


@admin.register(RequisicaoInterna)
class RequisicaoInternaAdmin(admin.ModelAdmin):
    list_display = ("id", "origem", "solicitante", "status", "hospital", "criado_em")
    list_filter = ("status", "hospital")
    search_fields = ("origem", "solicitante__primeiro_nome", "solicitante__ultimo_nome")
    ordering = ("-criado_em",)
    readonly_fields = ("criado_em", "atualizado_em")
    inlines = [ItemRequisicaoInternaInline]