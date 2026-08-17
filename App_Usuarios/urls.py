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
from App_Atendimentos import views as atendimento_views
from App_Prescricoes import views as prescricoes_views
from App_Laboratorio import views as laboratorio_views


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
        "modulos/pacientes/buscar/",
        views.buscar_pacientes,
        name="buscar_pacientes"
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
        "modulos/farmacia/movimentos/",
        farmacia_views.listar_movimentos_stock,
        name="listar_movimentos_stock"
    ),

    # --- Farmácia processa Receitas digitais ---

    path(
        "modulos/farmacia/prescricoes/",
        farmacia_views.listar_prescricoes_farmacia,
        name="listar_prescricoes_farmacia"
    ),

    path(
        "modulos/farmacia/prescricoes/<int:id>/",
        farmacia_views.detalhe_prescricao_farmacia,
        name="detalhe_prescricao_farmacia"
    ),

    path(
        "modulos/farmacia/prescricoes/<int:id>/dispensar/",
        farmacia_views.dispensar_prescricao,
        name="dispensar_prescricao"
    ),

    path(
        "modulos/farmacia/prescricoes/<int:id>/pendencia/",
        farmacia_views.marcar_pendencia_prescricao,
        name="marcar_pendencia_prescricao"
    ),

    path(
        "modulos/configuracoes/",
        views.modulo_configuracoes,
        name="modulo_configuracoes"
    ),

    # --- Atendimento (fila da recepção) ---

    path(
        "modulos/atendimento/cadastrar/",
        atendimento_views.cadastrar_atendimento,
        name="cadastrar_atendimento"
    ),

    path(
        "modulos/atendimento/checkin/<int:agendamento_id>/",
        atendimento_views.iniciar_atendimento_de_agendamento,
        name="iniciar_atendimento_de_agendamento"
    ),

    path(
        "modulos/atendimento/fila/",
        atendimento_views.listar_fila_atendimento,
        name="listar_fila_atendimento"
    ),

    path(
        "modulos/atendimento/<int:id>/iniciar/",
        atendimento_views.iniciar_atendimento,
        name="iniciar_atendimento"
    ),

    path(
        "modulos/atendimento/<int:id>/concluir/",
        atendimento_views.concluir_atendimento,
        name="concluir_atendimento"
    ),

    path(
        "modulos/atendimento/<int:atendimento_id>/consulta/",
        atendimento_views.cadastrar_consulta,
        name="cadastrar_consulta"
    ),

    path(
        "modulos/atendimento/<int:atendimento_id>/sinais-vitais/",
        atendimento_views.salvar_sinais_vitais,
        name="salvar_sinais_vitais"
    ),

    # --- Meus Atendimentos (fila do médico + ficha completa) ---

    path(
        "modulos/meus_atendimentos/",
        atendimento_views.modulo_meus_atendimentos,
        name="modulo_meus_atendimentos"
    ),

    path(
        "modulos/meus_atendimentos/fila/",
        atendimento_views.listar_meus_atendimentos,
        name="listar_meus_atendimentos"
    ),

    path(
        "modulos/meus_atendimentos/ficha/<int:id>/",
        atendimento_views.ficha_atendimento,
        name="ficha_atendimento"
    ),

    # --- Triagem (fila do enfermeiro — sinais vitais) ---

    path(
        "modulos/triagem/",
        atendimento_views.modulo_triagem,
        name="modulo_triagem"
    ),

    path(
        "modulos/triagem/fila/",
        atendimento_views.listar_fila_triagem,
        name="listar_fila_triagem"
    ),

    # --- Prescrição digital ---

    path(
        "modulos/prescricoes/cadastrar/",
        prescricoes_views.cadastrar_prescricao,
        name="cadastrar_prescricao"
    ),

    path(
        "modulos/prescricoes/<int:id>/",
        prescricoes_views.detalhe_prescricao,
        name="detalhe_prescricao"
    ),

    path(
        "modulos/prescricoes/paciente/<str:paciente_codigo>/",
        prescricoes_views.listar_prescricoes_paciente,
        name="listar_prescricoes_paciente"
    ),

    path(
        "modulos/laboratorio/",
        laboratorio_views.modulo_laboratorio,
        name="modulo_laboratorio"
    ),

    path(
        "modulos/laboratorio/exames/cadastrar/",
        laboratorio_views.cadastrar_tipo_exame,
        name="cadastrar_tipo_exame"
    ),

    path(
        "modulos/laboratorio/exames/<int:id>/",
        laboratorio_views.detalhe_tipo_exame,
        name="detalhe_tipo_exame"
    ),

    path(
        "modulos/laboratorio/exames/<int:id>/atualizar/",
        laboratorio_views.atualizar_tipo_exame,
        name="atualizar_tipo_exame"
    ),

    path(
        "modulos/laboratorio/exames/<int:id>/eliminar/",
        laboratorio_views.eliminar_tipo_exame,
        name="eliminar_tipo_exame"
    ),




]