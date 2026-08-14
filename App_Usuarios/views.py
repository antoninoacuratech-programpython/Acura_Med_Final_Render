from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction, IntegrityError
from django.db.models import Prefetch, Q
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse

from .ultilizador import Utilizador
from .perfil import Perfil
from .permissao import Permissao
from .perfil_permissao import PerfilPermissao
from .permissoes import requer_permissao

from App_Hospital.hospital import Hospital
from App_Hospital.departamento import Departamento
from App_Hospital.especialidade import Especialidade

from App_Pacientes.paciente import Paciente
from App_Pacientes.documento import DocumentoPaciente


# LOGIN
def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            utilizador = Utilizador.objects.get(email=email)

            if check_password(password, utilizador.password):

                if not utilizador.is_active:
                    messages.error(
                        request,
                        "Este utilizador está desativado."
                    )
                    return redirect("login")

                login(request, utilizador)

                if utilizador.is_superuser:
                    #return redirect("admin:index")
                    return redirect("dashboard")

                return redirect("dashboard")

            else:
                messages.error(
                    request,
                    "Email ou senha inválidos."
                )

        except Utilizador.DoesNotExist:
            messages.error(
                request,
                "Email ou senha inválidos."
            )

    return render(
        request,
        "index.html"
    )


# LOGOUT
@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "Sessão encerrada com sucesso."
    )

    return redirect("login")

def registro_view(request):

    if request.method == "POST":

        nome = request.POST.get("nome")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:

            messages.error(
                request,
                "As senhas não coincidem."
            )

            return redirect("login")


        if Utilizador.objects.filter(email=email).exists():

            messages.error(
                request,
                "Este email já existe."
            )

            return redirect("login")


        utilizador = Utilizador(
            primeiro_nome=nome,
            ultimo_nome="",
            email=email,
            is_active=True
        )

        utilizador.set_password(password)

        utilizador.save()


        messages.success(
            request,
            "Conta criada com sucesso."
        )


        return redirect("login")


    return redirect("login")

@login_required
def dashboard(request):

    return render(
        request,
        "dashboard/dashboard.html"
    )


@login_required
def modulo_dashboard(request):

    return render(
        request,
        "dashboard/painel.html"
    )


@login_required
def modulo_pacientes(request):

    pacientes = Paciente.objects.filter(
        hospital=request.user.hospital
    ).select_related("endereco").prefetch_related(
        Prefetch(
            "documentos",
            queryset=DocumentoPaciente.objects.filter(tipo=DocumentoPaciente.TipoDocumento.BI),
            to_attr="documentos_bi",
        )
    ).order_by("-criado_em")

    return render(
        request,
        "pacientes/painel.html",
        {
            "pacientes": pacientes,
        }
    )


@login_required
def buscar_pacientes(request):
    """Autocomplete de pacientes — usado no modal de Atendimento."""
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    termo = request.GET.get("q", "").strip()
    if not termo:
        return JsonResponse({"ok": True, "pacientes": []})

    pacientes = Paciente.objects.filter(
        hospital=request.user.hospital
    ).filter(
        Q(primeiro_nome__icontains=termo) |
        Q(ultimo_nome__icontains=termo) |
        Q(codigo__icontains=termo)
    ).order_by("primeiro_nome")[:10]

    return JsonResponse({
        "ok": True,
        "pacientes": [
            {
                "codigo": p.codigo,
                "nome": p.nome_completo,
                "responsavel": (p.responsaveis.first().nome if p.responsaveis.exists() else ""),
            }
            for p in pacientes
        ]
    })


@login_required
def modulo_atendimento(request):

    profissionais = Utilizador.objects.filter(
        hospital=request.user.hospital,
        is_active=True,
    ).order_by("primeiro_nome")

    return render(
        request,
        "atendimento/painel.html",
        {
            "profissionais": profissionais,
        }
    )


@login_required
def modulo_encaminhamento(request):

    return render(
        request,
        "encaminhamento/painel.html"
    )


@login_required
def modulo_convenios(request):

    return render(
        request,
        "convenios/painel.html"
    )


@login_required
@requer_permissao("utilizador.gerir")
def modulo_colaboradores(request):

    utilizadores = Utilizador.objects.select_related(
        "hospital",
        "perfil",
        "departamento",
        "especialidade",
    ).all()

    return render(
        request,
        "colaboradores/painel.html",
        {
            "utilizadores": utilizadores,
            "hospitais": Hospital.objects.all(),
            "perfis": Perfil.objects.filter(ativo=True),
            "departamentos": Departamento.objects.all(),
            "especialidades": Especialidade.objects.all(),
        },
    )


@login_required
@requer_permissao("perfil.gerir")
def modulo_perfis(request):

    perfis = Perfil.objects.all().prefetch_related("permissoes__permissao")

    return render(
        request,
        "perfis/painel.html",
        {"perfis": perfis},
    )


@login_required
@requer_permissao("permissao.gerir")
def modulo_permissoes(request):

    permissoes = Permissao.objects.all()

    return render(
        request,
        "permissoes/painel.html",
        {"permissoes": permissoes},
    )


@login_required
def modulo_agendamentos(request):

    return render(
        request,
        "agendamentos/painel.html"
    )


@login_required
def modulo_configuracoes(request):

    return render(
        request,
        "configuracoes/painel.html"
    )




def _serializar_perfil(perfil):
    permissoes_ids = list(
        perfil.permissoes.values_list("permissao_id", flat=True)
    )
    return {
        "id": perfil.id,
        "nome": perfil.nome,
        "descricao": perfil.descricao,
        "ativo": perfil.ativo,
        "permissoes_ids": permissoes_ids,
    }


def _sincronizar_permissoes_perfil(perfil, permissoes_ids_selecionadas):
    """Cria/remove linhas de PerfilPermissao para o perfil ficar exatamente
    com o conjunto de permissões submetido no formulário."""

    atuais = set(
        perfil.permissoes.values_list("permissao_id", flat=True)
    )
    selecionadas = {int(pid) for pid in permissoes_ids_selecionadas if pid.strip().isdigit()}

    a_remover = atuais - selecionadas
    a_adicionar = selecionadas - atuais

    if a_remover:
        PerfilPermissao.objects.filter(
            perfil=perfil, permissao_id__in=a_remover
        ).delete()

    if a_adicionar:
        PerfilPermissao.objects.bulk_create([
            PerfilPermissao(perfil=perfil, permissao_id=pid) for pid in a_adicionar
        ])


@login_required
@requer_permissao("perfil.gerir")
def cadastrar_perfil(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    nome = request.POST.get("perfil_nome", "").strip()
    descricao = request.POST.get("perfil_descricao", "").strip()
    ativo = request.POST.get("perfil_ativo") == "on"
    permissoes_ids = request.POST.getlist("permissoes")

    if not nome:
        return JsonResponse({"ok": False, "erro": "Nome do perfil é obrigatório."}, status=400)

    if Perfil.objects.filter(nome__iexact=nome).exists():
        return JsonResponse({"ok": False, "erro": "Já existe um perfil com esse nome."}, status=400)

    try:
        with transaction.atomic():
            perfil = Perfil.objects.create(
                nome=nome,
                descricao=descricao,
                ativo=ativo,
            )
            _sincronizar_permissoes_perfil(perfil, permissoes_ids)
    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao salvar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Perfil '{perfil.nome}' criado com sucesso.",
    })


@login_required
@requer_permissao("perfil.gerir")
def detalhe_perfil(request, perfil_id):
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        perfil = Perfil.objects.get(id=perfil_id)
    except Perfil.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Perfil não encontrado."}, status=404)

    return JsonResponse({"ok": True, "perfil": _serializar_perfil(perfil)})


@login_required
@requer_permissao("perfil.gerir")
def atualizar_perfil(request, perfil_id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        perfil = Perfil.objects.get(id=perfil_id)
    except Perfil.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Perfil não encontrado."}, status=404)

    nome = request.POST.get("perfil_nome", "").strip()
    descricao = request.POST.get("perfil_descricao", "").strip()
    ativo = request.POST.get("perfil_ativo") == "on"
    permissoes_ids = request.POST.getlist("permissoes")

    if not nome:
        return JsonResponse({"ok": False, "erro": "Nome do perfil é obrigatório."}, status=400)

    if Perfil.objects.filter(nome__iexact=nome).exclude(id=perfil.id).exists():
        return JsonResponse({"ok": False, "erro": "Já existe um perfil com esse nome."}, status=400)

    try:
        with transaction.atomic():
            perfil.nome = nome
            perfil.descricao = descricao
            perfil.ativo = ativo
            perfil.save()
            _sincronizar_permissoes_perfil(perfil, permissoes_ids)
    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao atualizar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Perfil '{perfil.nome}' atualizado com sucesso.",
    })


@login_required
@requer_permissao("perfil.gerir")
def eliminar_perfil(request, perfil_id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        perfil = Perfil.objects.get(id=perfil_id)
    except Perfil.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Perfil não encontrado."}, status=404)

    if Utilizador.objects.filter(perfil=perfil).exists():
        return JsonResponse({
            "ok": False,
            "erro": "Não é possível eliminar: existem utilizadores com este perfil atribuído.",
        }, status=400)

    nome = perfil.nome
    perfil.delete()

    return JsonResponse({"ok": True, "mensagem": f"Perfil '{nome}' eliminado com sucesso."})

@login_required
def listar_permissoes_json(request):
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    permissoes = Permissao.objects.all().order_by("nome")

    return JsonResponse({
        "ok": True,
        "permissoes": [
            {
                "id": p.id,
                "nome": p.nome,
                "codigo": p.codigo,
                "ativo": p.ativo,
            }
            for p in permissoes
        ],
    })


@login_required
@requer_permissao("permissao.gerir")
def cadastrar_permissao(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    nome = request.POST.get("permissao_nome", "").strip()
    codigo = request.POST.get("permissao_codigo", "").strip().lower()
    descricao = request.POST.get("permissao_descricao", "").strip()
    ativo = request.POST.get("permissao_ativo") == "on"

    erros = []
    if not nome:
        erros.append("Nome da permissão é obrigatório.")
    if not codigo:
        erros.append("Código é obrigatório.")
    elif Permissao.objects.filter(codigo__iexact=codigo).exists():
        erros.append("Já existe uma permissão com esse código.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        permissao = Permissao.objects.create(
            nome=nome,
            codigo=codigo,
            descricao=descricao,
            ativo=ativo,
        )
    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao salvar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Permissão '{permissao.nome}' criada com sucesso.",
    })


@login_required
@requer_permissao("permissao.gerir")
def detalhe_permissao(request, permissao_id):
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        permissao = Permissao.objects.get(id=permissao_id)
    except Permissao.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Permissão não encontrada."}, status=404)

    return JsonResponse({
        "ok": True,
        "permissao": {
            "id": permissao.id,
            "nome": permissao.nome,
            "codigo": permissao.codigo,
            "descricao": permissao.descricao,
            "ativo": permissao.ativo,
        }
    })


@login_required
@requer_permissao("permissao.gerir")
def atualizar_permissao(request, permissao_id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        permissao = Permissao.objects.get(id=permissao_id)
    except Permissao.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Permissão não encontrada."}, status=404)

    nome = request.POST.get("permissao_nome", "").strip()
    codigo = request.POST.get("permissao_codigo", "").strip().lower()
    descricao = request.POST.get("permissao_descricao", "").strip()
    ativo = request.POST.get("permissao_ativo") == "on"

    erros = []
    if not nome:
        erros.append("Nome da permissão é obrigatório.")
    if not codigo:
        erros.append("Código é obrigatório.")
    elif Permissao.objects.filter(codigo__iexact=codigo).exclude(id=permissao.id).exists():
        erros.append("Já existe uma permissão com esse código.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        permissao.nome = nome
        permissao.codigo = codigo
        permissao.descricao = descricao
        permissao.ativo = ativo
        permissao.save()
    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao atualizar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Permissão '{permissao.nome}' atualizada com sucesso.",
    })


@login_required
@requer_permissao("permissao.gerir")
def eliminar_permissao(request, permissao_id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        permissao = Permissao.objects.get(id=permissao_id)
    except Permissao.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Permissão não encontrada."}, status=404)

    if PerfilPermissao.objects.filter(permissao=permissao).exists():
        return JsonResponse({
            "ok": False,
            "erro": "Não é possível eliminar: esta permissão está atribuída a um ou mais perfis. Remova-a dos perfis primeiro.",
        }, status=400)

    nome = permissao.nome
    permissao.delete()

    return JsonResponse({"ok": True, "mensagem": f"Permissão '{nome}' eliminada com sucesso."})


# ---------------------------------------------------------------------------
# CRUD de UTILIZADOR (colaboradores)
# ---------------------------------------------------------------------------

def _serializar_utilizador(utilizador):
    return {
        "id": utilizador.id,
        "uuid": str(utilizador.uuid),
        "primeiro_nome": utilizador.primeiro_nome,
        "ultimo_nome": utilizador.ultimo_nome,
        "email": utilizador.email,
        "telefone": utilizador.telefone,
        "cargo": utilizador.cargo,
        "hospital_id": utilizador.hospital_id,
        "perfil_id": utilizador.perfil_id,
        "departamento_id": utilizador.departamento_id,
        "especialidade_id": utilizador.especialidade_id,
        "is_active": utilizador.is_active,
        "is_staff": utilizador.is_staff,
    }


def _validar_dados_utilizador(request, utilizador_atual=None):
    """Valida os campos comuns ao criar/atualizar um utilizador.
    Retorna (dados_limpos, erros)."""

    primeiro_nome = request.POST.get("primeiro_nome", "").strip()
    ultimo_nome = request.POST.get("ultimo_nome", "").strip()
    email = request.POST.get("email", "").strip().lower()
    telefone = request.POST.get("telefone", "").strip()
    cargo = request.POST.get("cargo", "").strip()
    hospital_id = request.POST.get("hospital") or None
    perfil_id = request.POST.get("perfil") or None
    departamento_id = request.POST.get("departamento") or None
    especialidade_id = request.POST.get("especialidade") or None
    is_active = request.POST.get("is_active") == "on"

    erros = []

    if not primeiro_nome:
        erros.append("Primeiro nome é obrigatório.")

    if not ultimo_nome:
        erros.append("Apelido é obrigatório.")

    if not email:
        erros.append("E-mail é obrigatório.")
    else:
        duplicados = Utilizador.objects.filter(email__iexact=email)
        if utilizador_atual is not None:
            duplicados = duplicados.exclude(id=utilizador_atual.id)
        if duplicados.exists():
            erros.append("Já existe um utilizador com esse e-mail.")

    # Impede que um utilizador se desative a si próprio.
    if utilizador_atual is not None and utilizador_atual.id == request.user.id and not is_active:
        erros.append("Não pode desativar a sua própria conta.")

    dados = {
        "primeiro_nome": primeiro_nome,
        "ultimo_nome": ultimo_nome,
        "email": email,
        "telefone": telefone,
        "cargo": cargo,
        "hospital_id": hospital_id,
        "perfil_id": perfil_id,
        "departamento_id": departamento_id,
        "especialidade_id": especialidade_id,
        "is_active": is_active,
    }

    return dados, erros


@login_required
@requer_permissao("utilizador.gerir")
def cadastrar_utilizador(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    dados, erros = _validar_dados_utilizador(request)

    senha = request.POST.get("senha", "")
    confirmar_senha = request.POST.get("confirmar_senha", "")

    if not senha:
        erros.append("Senha é obrigatória.")
    elif senha != confirmar_senha:
        erros.append("As senhas não coincidem.")
    else:
        try:
            validate_password(senha)
        except DjangoValidationError as e:
            erros.extend(e.messages)

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        with transaction.atomic():
            utilizador = Utilizador.objects.create_user(
                email=dados["email"],
                password=senha,
                primeiro_nome=dados["primeiro_nome"],
                ultimo_nome=dados["ultimo_nome"],
                telefone=dados["telefone"],
                cargo=dados["cargo"],
                hospital_id=dados["hospital_id"],
                perfil_id=dados["perfil_id"],
                departamento_id=dados["departamento_id"],
                especialidade_id=dados["especialidade_id"],
                is_active=dados["is_active"],
            )

            if request.FILES.get("fotografia"):
                utilizador.fotografia = request.FILES["fotografia"]
                utilizador.save(update_fields=["fotografia"])

    except IntegrityError:
        return JsonResponse({"ok": False, "erro": "Já existe um utilizador com esse e-mail."}, status=400)
    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao salvar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Utilizador '{utilizador.nome_completo}' criado com sucesso.",
    })


@login_required
@requer_permissao("utilizador.gerir")
def detalhe_utilizador(request, utilizador_id):
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        utilizador = Utilizador.objects.get(id=utilizador_id)
    except Utilizador.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Utilizador não encontrado."}, status=404)

    return JsonResponse({"ok": True, "utilizador": _serializar_utilizador(utilizador)})


@login_required
@requer_permissao("utilizador.gerir")
def atualizar_utilizador(request, utilizador_id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        utilizador = Utilizador.objects.get(id=utilizador_id)
    except Utilizador.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Utilizador não encontrado."}, status=404)

    dados, erros = _validar_dados_utilizador(request, utilizador_atual=utilizador)

    senha = request.POST.get("senha", "")
    confirmar_senha = request.POST.get("confirmar_senha", "")
    nova_senha = None

    # A senha só é alterada se o campo for preenchido; deixá-lo em branco
    # mantém a senha atual.
    if senha or confirmar_senha:
        if senha != confirmar_senha:
            erros.append("As senhas não coincidem.")
        else:
            try:
                validate_password(senha)
                nova_senha = senha
            except DjangoValidationError as e:
                erros.extend(e.messages)

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        with transaction.atomic():
            utilizador.primeiro_nome = dados["primeiro_nome"]
            utilizador.ultimo_nome = dados["ultimo_nome"]
            utilizador.email = dados["email"]
            utilizador.telefone = dados["telefone"]
            utilizador.cargo = dados["cargo"]
            utilizador.hospital_id = dados["hospital_id"]
            utilizador.perfil_id = dados["perfil_id"]
            utilizador.departamento_id = dados["departamento_id"]
            utilizador.especialidade_id = dados["especialidade_id"]
            utilizador.is_active = dados["is_active"]

            if nova_senha:
                utilizador.set_password(nova_senha)

            if request.FILES.get("fotografia"):
                utilizador.fotografia = request.FILES["fotografia"]

            utilizador.save()

    except IntegrityError:
        return JsonResponse({"ok": False, "erro": "Já existe um utilizador com esse e-mail."}, status=400)
    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao atualizar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Utilizador '{utilizador.nome_completo}' atualizado com sucesso.",
    })


@login_required
@requer_permissao("utilizador.gerir")
def alternar_status_utilizador(request, utilizador_id):
    """Ativa/desativa um utilizador sem o eliminar. É a ação recomendada
    para o dia-a-dia — eliminar deve ser reservado para correção de erros
    de cadastro."""

    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        utilizador = Utilizador.objects.get(id=utilizador_id)
    except Utilizador.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Utilizador não encontrado."}, status=404)

    if utilizador.id == request.user.id:
        return JsonResponse({"ok": False, "erro": "Não pode desativar a sua própria conta."}, status=400)

    utilizador.is_active = not utilizador.is_active
    utilizador.save(update_fields=["is_active"])

    estado = "ativado" if utilizador.is_active else "desativado"

    return JsonResponse({
        "ok": True,
        "is_active": utilizador.is_active,
        "mensagem": f"Utilizador '{utilizador.nome_completo}' {estado} com sucesso.",
    })


@login_required
@requer_permissao("utilizador.gerir")
def eliminar_utilizador(request, utilizador_id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        utilizador = Utilizador.objects.get(id=utilizador_id)
    except Utilizador.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Utilizador não encontrado."}, status=404)

    if utilizador.id == request.user.id:
        return JsonResponse({"ok": False, "erro": "Não pode eliminar a sua própria conta."}, status=400)

    if utilizador.is_superuser and not request.user.is_superuser:
        return JsonResponse({
            "ok": False,
            "erro": "Apenas um superutilizador pode eliminar outro superutilizador.",
        }, status=403)

    nome = utilizador.nome_completo

    try:
        utilizador.delete()
    except ProtectedError:
        return JsonResponse({
            "ok": False,
            "erro": (
                "Não é possível eliminar: este utilizador tem registos associados "
                "(ex.: atendimentos, agendamentos, pacientes cadastrados por ele). "
                "Considere desativá-lo em vez de eliminar."
            ),
        }, status=400)

    return JsonResponse({"ok": True, "mensagem": f"Utilizador '{nome}' eliminado com sucesso."})