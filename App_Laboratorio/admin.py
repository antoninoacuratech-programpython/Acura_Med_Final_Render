from django.contrib import admin

from .tipo_exame import TipoExame
from .parametro import Parametro
from .valor_referencia import ValorReferencia
from .exame_parametro import ExameParametro


@admin.register(TipoExame)
class TipoExameAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "departamento", "tipo_amostra", "tempo_estimado", "ativo")
    list_filter = ("departamento", "tipo_amostra", "metodo", "tipo_resultado", "ativo")
    search_fields = ("codigo", "codigo_padronizado", "nome", "nome_tecnico")
    ordering = ("nome",)
    list_editable = ("ativo",)
    readonly_fields = ("criado_em", "atualizado_em")


class ValorReferenciaInline(admin.TabularInline):
    model = ValorReferencia
    extra = 0


@admin.register(Parametro)
class ParametroAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "nome_abreviado", "tipo_resultado", "unidade", "ativo")
    list_filter = ("tipo_resultado", "ativo")
    search_fields = ("codigo", "nome", "nome_abreviado")
    ordering = ("nome",)
    list_editable = ("ativo",)
    readonly_fields = ("criado_em", "atualizado_em")
    inlines = [ValorReferenciaInline]


class ExameParametroInline(admin.TabularInline):
    model = ExameParametro
    extra = 0
    autocomplete_fields = ["parametro"]


# Acrescenta os parâmetros de cada exame directamente na página do
# TipoExame, para não teres de andar a saltar entre ecrãs no admin.
TipoExameAdmin.inlines = [ExameParametroInline]