from django.urls import path
from . import views
from .views import (
    login_view,
    logout_view,
    registro_view,
    dashboard
)

from App_Agendamentos import views as agendamentos_views


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
        "modulos/configuracoes/",
        views.modulo_configuracoes,
        name="modulo_configuracoes"
    ),

]