from django.contrib import admin

from .models import (
    TipoExame,
    Requisicao,
    Amostra,
    ExameSolicitado,
    Resultado,
    LivroSaida,
)


@admin.register(TipoExame)
class TipoExameAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "codigo",
        "categoria",
        "tipo_amostra",
        "tempo_estimado_horas",
        "ativo",
    )

    list_filter = (
        "categoria",
        "tipo_amostra",
        "ativo",
    )

    search_fields = (
        "nome",
        "codigo",
    )

    ordering = (
        "nome",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )


class AmostraInline(admin.TabularInline):
    model = Amostra
    extra = 0
    fields = (
        "codigo",
        "tipo_amostra",
        "local_colheita",
        "condicao",
        "colhida_por",
        "colhida_em",
    )
    show_change_link = True


class ExameSolicitadoInline(admin.TabularInline):
    model = ExameSolicitado
    extra = 0
    fields = (
        "tipo_exame",
        "amostra",
        "status",
        "tecnico_responsavel",
    )
    show_change_link = True


@admin.register(Requisicao)
class RequisicaoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "paciente",
        "medico_solicitante",
        "hospital",
        "status",
        "criado_em",
    )

    list_filter = (
        "status",
        "hospital",
    )

    search_fields = (
        "paciente__nome",
        "medico_solicitante__primeiro_nome",
        "medico_solicitante__ultimo_nome",
        "suspeita_clinica",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    ordering = (
        "-criado_em",
    )

    inlines = [
        AmostraInline,
        ExameSolicitadoInline,
    ]


@admin.register(Amostra)
class AmostraAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "requisicao",
        "tipo_amostra",
        "local_colheita",
        "condicao",
        "colhida_em",
    )

    list_filter = (
        "tipo_amostra",
        "local_colheita",
        "condicao",
    )

    search_fields = (
        "codigo",
        "requisicao__paciente__nome",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    ordering = (
        "-criado_em",
    )


class ResultadoInline(admin.StackedInline):
    model = Resultado
    extra = 0
    fields = (
        "valores",
        "interpretacao",
        "arquivo_laudo",
        "tecnico_responsavel",
        "validado_por",
        "data_liberacao",
    )


@admin.register(ExameSolicitado)
class ExameSolicitadoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tipo_exame",
        "requisicao",
        "amostra",
        "status",
        "tecnico_responsavel",
    )

    list_filter = (
        "status",
        "tipo_exame__categoria",
    )

    search_fields = (
        "tipo_exame__nome",
        "requisicao__paciente__nome",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    ordering = (
        "-criado_em",
    )

    inlines = [
        ResultadoInline,
    ]


@admin.register(Resultado)
class ResultadoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "exame_solicitado",
        "tecnico_responsavel",
        "validado_por",
        "data_liberacao",
    )

    list_filter = (
        "data_liberacao",
    )

    search_fields = (
        "exame_solicitado__tipo_exame__nome",
        "exame_solicitado__requisicao__paciente__nome",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    ordering = (
        "-criado_em",
    )


@admin.register(LivroSaida)
class LivroSaidaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "requisicao",
        "recebido_por",
        "entregue_por",
        "entregue_em",
    )

    search_fields = (
        "recebido_por",
        "requisicao__paciente__nome",
    )

    readonly_fields = (
        "entregue_em",
    )

    ordering = (
        "-entregue_em",
    )