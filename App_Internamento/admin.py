from django.contrib import admin

from .nave import Nave
from .quarto import Quarto


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
