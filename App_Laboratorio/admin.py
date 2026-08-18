from django.contrib import admin

from .tipo_exame import TipoExame


@admin.register(TipoExame)
class TipoExameAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "departamento", "tipo_amostra", "tempo_estimado", "ativo")
    list_filter = ("departamento", "tipo_amostra", "metodo", "tipo_resultado", "ativo")
    search_fields = ("codigo", "codigo_padronizado", "nome", "nome_tecnico")
    ordering = ("nome",)
    list_editable = ("ativo",)
    readonly_fields = ("criado_em", "atualizado_em")