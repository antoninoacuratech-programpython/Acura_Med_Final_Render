from django.contrib import admin

from .item_solicitacao_exame import TipoExame


@admin.register(TipoExame)
class TipoExameAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "categoria", "tipo_amostra", "tempo_estimado_horas", "ativo")
    list_filter = ("categoria", "tipo_amostra", "ativo")
    search_fields = ("codigo", "nome")
    ordering = ("nome",)
    list_editable = ("ativo",)
    readonly_fields = ("criado_em", "atualizado_em")