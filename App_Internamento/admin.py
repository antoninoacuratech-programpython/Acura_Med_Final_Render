from django.contrib import admin

from .nave import Nave
from .quarto import Quarto
from .internamento import Internamento


@admin.register(Nave)
class NaveAdmin(admin.ModelAdmin):
    list_display = ("nome", "hospital", "ativa")
    list_filter = ("hospital", "ativa")
    search_fields = ("nome",)
    ordering = ("nome",)


@admin.register(Quarto)
class QuartoAdmin(admin.ModelAdmin):
    list_display = ("nave", "numero", "tipo", "capacidade", "ativo")
    list_filter = ("nave", "tipo", "ativo")
    search_fields = ("numero", "nave__nome")
    ordering = ("nave__nome", "numero")


@admin.register(Internamento)
class InternamentoAdmin(admin.ModelAdmin):
    list_display = ("paciente", "quarto", "medico_responsavel", "status", "data_entrada", "data_alta")
    list_filter = ("status", "hospital", "quarto__nave")
    search_fields = ("paciente__primeiro_nome", "paciente__ultimo_nome", "paciente__codigo")
    ordering = ("-data_entrada",)
    readonly_fields = ("data_entrada", "criado_em", "atualizado_em")