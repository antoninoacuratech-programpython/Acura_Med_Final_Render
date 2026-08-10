from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from App_Usuarios.permissoes import requer_permissao
from App_Usuarios.ultilizador import Utilizador
from App_Hospital.departamento import Departamento
from App_Hospital.especialidade import Especialidade
from App_Pacientes.paciente import Paciente

from .models import Agendamento

@login_required
@requer_permissao("agendamento.gerir")
def modulo_agendamentos(request):

    hospital_id = request.user.hospital_id

    agendamentos = Agendamento.objects.select_related(
        "paciente",
        "profissional",
        "hospital",
        "departamento",
        "especialidade",
    )

    if hospital_id:
        agendamentos = agendamentos.filter(hospital_id=hospital_id)
    else:
        agendamentos = agendamentos.none()

    pacientes = Paciente.objects.filter(hospital_id=hospital_id) if hospital_id else Paciente.objects.none()
    profissionais = (
        Utilizador.objects.filter(is_active=True, hospital_id=hospital_id)
        if hospital_id
        else Utilizador.objects.none()
    )

    return render(
        request,
        "agendamentos/painel.html",
        {
            "agendamentos": agendamentos,
            "pacientes": pacientes,
            "profissionais": profissionais,
            "departamentos": Departamento.objects.all(),
            "especialidades": Especialidade.objects.all(),
            "status_choices": Agendamento.Status.choices,
            "sem_hospital": not hospital_id,
        },
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _serializar_agendamento(agendamento):
    return {
        "id": agendamento.id,
        "paciente_id": agendamento.paciente_id,
        "profissional_id": agendamento.profissional_id,
        "hospital_id": agendamento.hospital_id,
        "departamento_id": agendamento.departamento_id,
        "especialidade_id": agendamento.especialidade_id,
        "data_hora": timezone.localtime(agendamento.data_hora).strftime("%Y-%m-%dT%H:%M"),
        "duracao_minutos": agendamento.duracao_minutos,
        "status": agendamento.status,
        "motivo": agendamento.motivo,
        "observacoes": agendamento.observacoes,
    }


def _validar_dados_agendamento(request):
    """Valida os campos comuns ao criar/atualizar um agendamento.
    Retorna (dados_limpos, erros).

    O hospital NUNCA vem do formulário — é sempre o hospital do
    utilizador autenticado. paciente e profissional são validados
    como pertencentes a esse mesmo hospital, para impedir que um
    pedido adulterado misture dados de hospitais diferentes.
    """

    paciente_id = request.POST.get("paciente") or None
    profissional_id = request.POST.get("profissional") or None
    departamento_id = request.POST.get("departamento") or None
    especialidade_id = request.POST.get("especialidade") or None
    data_hora_raw = request.POST.get("data_hora", "").strip()
    duracao_raw = request.POST.get("duracao_minutos", "30").strip()
    status = request.POST.get("status", Agendamento.Status.AGENDADO).strip()
    motivo = request.POST.get("motivo", "").strip()
    observacoes = request.POST.get("observacoes", "").strip()

    erros = []

    hospital_id = request.user.hospital_id
    if not hospital_id:
        erros.append("A sua conta não tem um hospital associado — não é possível marcar agendamentos.")

    if not paciente_id:
        erros.append("Paciente é obrigatório.")
    elif hospital_id and not Paciente.objects.filter(id=paciente_id, hospital_id=hospital_id).exists():
        erros.append("Paciente inválido para o seu hospital.")

    if not profissional_id:
        erros.append("Profissional é obrigatório.")
    elif hospital_id and not Utilizador.objects.filter(id=profissional_id, hospital_id=hospital_id).exists():
        erros.append("Profissional inválido para o seu hospital.")

    if not motivo:
        erros.append("Motivo é obrigatório.")

    data_hora = None
    if not data_hora_raw:
        erros.append("Data e hora são obrigatórias.")
    else:
        data_hora = parse_datetime(data_hora_raw)
        if not data_hora:
            erros.append("Data e hora inválidas.")
        elif timezone.is_naive(data_hora):
            data_hora = timezone.make_aware(data_hora, timezone.get_current_timezone())

    try:
        duracao_minutos = int(duracao_raw)
        if duracao_minutos <= 0:
            erros.append("Duração deve ser maior que zero.")
            duracao_minutos = 30
    except ValueError:
        erros.append("Duração inválida.")
        duracao_minutos = 30

    status_validos = {codigo for codigo, _ in Agendamento.Status.choices}
    if status not in status_validos:
        status = Agendamento.Status.AGENDADO

    dados = {
        "paciente_id": paciente_id,
        "profissional_id": profissional_id,
        "hospital_id": hospital_id,
        "departamento_id": departamento_id,
        "especialidade_id": especialidade_id,
        "data_hora": data_hora,
        "duracao_minutos": duracao_minutos,
        "status": status,
        "motivo": motivo,
        "observacoes": observacoes,
    }

    return dados, erros


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@login_required
@requer_permissao("agendamento.gerir")
def cadastrar_agendamento(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    dados, erros = _validar_dados_agendamento(request)

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        with transaction.atomic():
            agendamento = Agendamento.objects.create(
                criado_por=request.user,
                **dados,
            )
    except IntegrityError:
        return JsonResponse({"ok": False, "erro": "Não foi possível salvar o agendamento."}, status=400)
    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao salvar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Agendamento de '{agendamento.paciente}' criado com sucesso.",
    })


@login_required
@requer_permissao("agendamento.gerir")
def detalhe_agendamento(request, agendamento_id):
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        agendamento = Agendamento.objects.get(id=agendamento_id)
    except Agendamento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Agendamento não encontrado."}, status=404)

    return JsonResponse({"ok": True, "agendamento": _serializar_agendamento(agendamento)})


@login_required
@requer_permissao("agendamento.gerir")
def atualizar_agendamento(request, agendamento_id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        agendamento = Agendamento.objects.get(id=agendamento_id)
    except Agendamento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Agendamento não encontrado."}, status=404)

    dados, erros = _validar_dados_agendamento(request)

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        with transaction.atomic():
            for campo, valor in dados.items():
                setattr(agendamento, campo, valor)
            agendamento.save()
    except IntegrityError:
        return JsonResponse({"ok": False, "erro": "Não foi possível atualizar o agendamento."}, status=400)
    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao atualizar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Agendamento de '{agendamento.paciente}' atualizado com sucesso.",
    })


@login_required
@requer_permissao("agendamento.gerir")
def atualizar_status_agendamento(request, agendamento_id):
    """Alteração rápida de status (ex.: a partir de um select na tabela),
    sem precisar abrir o modal completo de edição."""

    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        agendamento = Agendamento.objects.get(id=agendamento_id)
    except Agendamento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Agendamento não encontrado."}, status=404)

    status = request.POST.get("status", "").strip()
    status_validos = {codigo for codigo, _ in Agendamento.Status.choices}

    if status not in status_validos:
        return JsonResponse({"ok": False, "erro": "Status inválido."}, status=400)

    agendamento.status = status
    agendamento.save(update_fields=["status", "atualizado_em"])

    return JsonResponse({
        "ok": True,
        "status": agendamento.status,
        "mensagem": "Status atualizado com sucesso.",
    })


@login_required
@requer_permissao("agendamento.gerir")
def eliminar_agendamento(request, agendamento_id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        agendamento = Agendamento.objects.get(id=agendamento_id)
    except Agendamento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Agendamento não encontrado."}, status=404)

    descricao = str(agendamento)

    try:
        agendamento.delete()
    except ProtectedError:
        return JsonResponse({
            "ok": False,
            "erro": "Não é possível eliminar: este agendamento tem registos associados.",
        }, status=400)

    return JsonResponse({"ok": True, "mensagem": f"Agendamento '{descricao}' eliminado com sucesso."})