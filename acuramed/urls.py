from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect
from App_Pacientes import views as pacientes_views
from App_Usuarios import views as usuarios_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('App_Usuarios.urls')),
    path(
        "pacientes/cadastrar/",
        pacientes_views.cadastrar_paciente,
        name="cadastrar_paciente"
    ),
    path(
        "pacientes/<str:codigo>/detalhe/",
        pacientes_views.detalhe_paciente,
        name="detalhe_paciente"
    ),
    path(
        "pacientes/<str:codigo>/atualizar/",
        pacientes_views.atualizar_paciente,
        name="atualizar_paciente"
    ),
    path(
        "pacientes/<str:codigo>/eliminar/",
        pacientes_views.eliminar_paciente,
        name="eliminar_paciente"
    ),
    path(
        "pacientes/relatorio/pdf/",
        pacientes_views.relatorio_pacientes_pdf,
        name="relatorio_pacientes_pdf"
    ),
    path(
        "perfis/cadastrar/",
        usuarios_views.cadastrar_perfil,
        name="cadastrar_perfil"
    ),
    path(
        "perfis/<int:perfil_id>/detalhe/",
        usuarios_views.detalhe_perfil,
        name="detalhe_perfil"
    ),
    path(
        "perfis/<int:perfil_id>/atualizar/",
        usuarios_views.atualizar_perfil,
        name="atualizar_perfil"
    ),
    path(
        "perfis/<int:perfil_id>/eliminar/",
        usuarios_views.eliminar_perfil,
        name="eliminar_perfil"
    ),
    path(
        "permissoes/listar/",
        usuarios_views.listar_permissoes_json,
        name="listar_permissoes_json"
    ),
    path(
        "permissoes/cadastrar/",
        usuarios_views.cadastrar_permissao,
        name="cadastrar_permissao"
    ),
    path(
        "permissoes/<int:permissao_id>/detalhe/",
        usuarios_views.detalhe_permissao,
        name="detalhe_permissao"
    ),
    path(
        "permissoes/<int:permissao_id>/atualizar/",
        usuarios_views.atualizar_permissao,
        name="atualizar_permissao"
    ),
    path(
        "permissoes/<int:permissao_id>/eliminar/",
        usuarios_views.eliminar_permissao,
        name="eliminar_permissao"
    ),
]
