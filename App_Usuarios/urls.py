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
from App_Internamento import views as internamento_views


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
    path(
        "modulos/laboratorio/solicitacoes/cadastrar/",
        laboratorio_views.cadastrar_solicitacao_exame,
        name="cadastrar_solicitacao_exame"
    ),
    path(
        "modulos/laboratorio/solicitacoes/",
        laboratorio_views.listar_solicitacoes_laboratorio,
        name="listar_solicitacoes_laboratorio"
    ),

    path(
        "modulos/laboratorio/solicitacoes/<int:id>/",
        laboratorio_views.detalhe_solicitacao_laboratorio,
        name="detalhe_solicitacao_laboratorio"
    ),

    path(
        "modulos/laboratorio/solicitacoes/<int:id>/colher/",
        laboratorio_views.registar_colheita,
        name="registar_colheita"
    ),

    path(
        "modulos/laboratorio/solicitacoes/<int:id>/concluir/",
        laboratorio_views.concluir_solicitacao_laboratorio,
        name="concluir_solicitacao_laboratorio"
    ),
    path(
        "modulos/laboratorio/resultados/",
        laboratorio_views.listar_resultados_exame,
        name="listar_resultados_exame"
    ),

    path(
        "modulos/laboratorio/resultados/<int:id>/",
        laboratorio_views.detalhe_resultado_exame,
        name="detalhe_resultado_exame"
    ),
    path(
        "modulos/laboratorio/exames/<int:tipo_exame_id>/parametros/",
        laboratorio_views.listar_parametros_exame,
        name="listar_parametros_exame"
    ),

    path(
        "modulos/laboratorio/exames/<int:tipo_exame_id>/parametros/salvar/",
        laboratorio_views.salvar_parametro_exame,
        name="salvar_parametro_exame"
    ),

    path(
        "modulos/laboratorio/parametros/<int:id>/",
        laboratorio_views.detalhe_parametro_exame,
        name="detalhe_parametro_exame"
    ),

    path(
        "modulos/laboratorio/parametros/<int:id>/eliminar/",
        laboratorio_views.eliminar_parametro_exame,
        name="eliminar_parametro_exame"
    ),
    # 1) urls.py — no topo:
#    
#
# Dentro de urlpatterns:

    path(
        "modulos/internamento/",
        internamento_views.modulo_internamento,
        name="modulo_internamento"
    ),

    path(
        "modulos/internamento/naves/cadastrar/",
        internamento_views.cadastrar_nave,
        name="cadastrar_nave"
    ),

    path(
        "modulos/internamento/naves/<int:id>/eliminar/",
        internamento_views.eliminar_nave,
        name="eliminar_nave"
    ),

    path(
        "modulos/internamento/quartos/cadastrar/",
        internamento_views.cadastrar_quarto,
        name="cadastrar_quarto"
    ),

    path(
        "modulos/internamento/quartos/<int:id>/eliminar/",
        internamento_views.eliminar_quarto,
        name="eliminar_quarto"
    ),
    path(
        "modulos/internamento/quartos/disponiveis/",
        internamento_views.listar_quartos_disponiveis,
        name="listar_quartos_disponiveis"
    ),

    path(
        "modulos/internamento/cadastrar/",
        internamento_views.cadastrar_internamento,
        name="cadastrar_internamento"
    ),

    path(
        "modulos/internamento/internados/",
        internamento_views.listar_internados,
        name="listar_internados"
    ),

    path(
        "modulos/internamento/<int:id>/alta/",
        internamento_views.dar_alta,
        name="dar_alta"
    ),


# 2) Sidebar:
#
# {% if request.user|tem_permissao:"nave.gerir" %}
# <li><a href="#" data-module="internamento" data-title="Internamento"><i class="fa-solid fa-bed-pulse"></i><span>Internamento</span></a></li>
# {% endif %}


# 3) navigation.js — acrescentar "internamento" aos dois objectos:
#
# moduleMap: ..., internamento: "Internamento", ...
# moduleScripts: ..., internamento: "/static/js/modules/internamento.js", ...


# 4) Permissões novas: nave.cadastrar, nave.gerir




]