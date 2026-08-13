from django.urls import path
from . import views
from .views import (
    login_view,
    logout_view,
    registro_view,
    dashboard
)

from App_Agendamentos import views as agendamentos_views
from App_Farmacia import views as farmacia_views


urlpatterns = [

    path(
        "",
        login_view,
        name="login"
    ),

    path(
        "logout/",
        logout_view,
        name="logout"
    ),

    path(
        "registro/",
        registro_view,
        name="registro"
    ),

    path(
        "dashboard/",
        dashboard,
        name="dashboard"
    ),

    path(
        "modulos/dashboard/",
        views.modulo_dashboard,
        name="modulo_dashboard"
    ),

    path(
        "modulos/pacientes/",
        views.modulo_pacientes,
        name="modulo_pacientes"
    ),

    path(
        "modulos/atendimento/",
        views.modulo_atendimento,
        name="modulo_atendimento"
    ),

    path(
        "modulos/encaminhamento/",
        views.modulo_encaminhamento,
        name="modulo_encaminhamento"
    ),

    path(
        "modulos/convenios/",
        views.modulo_convenios,
        name="modulo_convenios"
    ),

    path(
        "modulos/colaboradores/",
        views.modulo_colaboradores,
        name="modulo_colaboradores"
    ),

    # --- CRUD de Utilizador (colaboradores) ---

    path(
        "modulos/colaboradores/cadastrar/",
        views.cadastrar_utilizador,
        name="cadastrar_utilizador"
    ),

    path(
        "modulos/colaboradores/<int:utilizador_id>/",
        views.detalhe_utilizador,
        name="detalhe_utilizador"
    ),

    path(
        "modulos/colaboradores/<int:utilizador_id>/atualizar/",
        views.atualizar_utilizador,
        name="atualizar_utilizador"
    ),

    path(
        "modulos/colaboradores/<int:utilizador_id>/status/",
        views.alternar_status_utilizador,
        name="alternar_status_utilizador"
    ),

    path(
        "modulos/colaboradores/<int:utilizador_id>/eliminar/",
        views.eliminar_utilizador,
        name="eliminar_utilizador"
    ),

    path(
        "modulos/perfis/",
        views.modulo_perfis,
        name="modulo_perfis"
    ),

    path(
        "modulos/permissoes/",
        views.modulo_permissoes,
        name="modulo_permissoes"
    ),

    path(
        "modulos/agendamentos/",
        agendamentos_views.modulo_agendamentos,
        name="modulo_agendamentos"
    ),

    # --- CRUD de Agendamento ---

    path(
        "modulos/agendamentos/cadastrar/",
        agendamentos_views.cadastrar_agendamento,
        name="cadastrar_agendamento"
    ),

    path(
        "modulos/agendamentos/<int:agendamento_id>/",
        agendamentos_views.detalhe_agendamento,
        name="detalhe_agendamento"
    ),

    path(
        "modulos/agendamentos/<int:agendamento_id>/atualizar/",
        agendamentos_views.atualizar_agendamento,
        name="atualizar_agendamento"
    ),

    path(
        "modulos/agendamentos/<int:agendamento_id>/status/",
        agendamentos_views.atualizar_status_agendamento,
        name="atualizar_status_agendamento"
    ),

    path(
        "modulos/agendamentos/<int:agendamento_id>/eliminar/",
        agendamentos_views.eliminar_agendamento,
        name="eliminar_agendamento"
    ),

    path(
        "modulos/farmacia/",
        farmacia_views.modulo_farmacia,
        name="modulo_farmacia"
    ),

    # --- CRUD de Medicamento (farmácia) ---

    path(
        "modulos/farmacia/medicamentos/cadastrar/",
        farmacia_views.cadastrar_medicamento,
        name="cadastrar_medicamento"
    ),

    path(
        "modulos/farmacia/medicamentos/<int:id>/",
        farmacia_views.detalhe_medicamento,
        name="detalhe_medicamento"
    ),

    path(
        "modulos/farmacia/medicamentos/<int:id>/atualizar/",
        farmacia_views.atualizar_medicamento,
        name="atualizar_medicamento"
    ),

    path(
        "modulos/farmacia/medicamentos/<int:id>/eliminar/",
        farmacia_views.eliminar_medicamento,
        name="eliminar_medicamento"
    ),

    path(
        "modulos/farmacia/medicamentos/<int:medicamento_id>/lotes/",
        farmacia_views.listar_lotes_por_medicamento,
        name="listar_lotes_por_medicamento"
    ),

    # --- CRUD de Lote (stock da farmácia) ---

    path(
        "modulos/farmacia/lotes/cadastrar/",
        farmacia_views.cadastrar_lote,
        name="cadastrar_lote"
    ),

    path(
        "modulos/farmacia/lotes/<int:id>/",
        farmacia_views.detalhe_lote,
        name="detalhe_lote"
    ),

    path(
        "modulos/farmacia/lotes/<int:id>/atualizar/",
        farmacia_views.atualizar_lote,
        name="atualizar_lote"
    ),

    path(
        "modulos/farmacia/lotes/<int:id>/eliminar/",
        farmacia_views.eliminar_lote,
        name="eliminar_lote"
    ),

    path(
        "modulos/configuracoes/",
        views.modulo_configuracoes,
        name="modulo_configuracoes"
    ),

]