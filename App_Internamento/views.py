from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError, Sum, Count, Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from App_Usuarios.permissoes import requer_permissao
from App_Atendimentos.atendimento import Atendimento
from App_Pacientes.documento import DocumentoPaciente
from .nave import Nave
from .quarto import Quarto
from .internamento import Internamento


def _contexto_painel_internamento(request):
    if not request.user.hospital:
        naves = Nave.objects.none()
        quartos = Quarto.objects.none()
        internados = Internamento.objects.none()
    else:
        naves = Nave.objects.filter(hospital=request.user.hospital, ativa=True).order_by("nome")
        quartos = Quarto.objects.filter(nave__hospital=request.user.hospital, ativo=True).select_related("nave").order_by("nave__nome", "numero")
        internados = Internamento.objects.filter(
            hospital=request.user.hospital,
            status=Internamento.Status.INTERNADO,
        ).select_related("paciente", "quarto", "quarto__nave", "medico_responsavel").order_by("-data_entrada")

    total_capacidade = quartos.aggregate(total=Sum("capacidade"))["total"] or 0
    total_ocupados = Internamento.objects.filter(
        hospital=request.user.hospital, status=Internamento.Status.INTERNADO
    ).count() if request.user.hospital else 0

    return {
        "naves": naves,
        "quartos": quartos,
        "internados": internados,
        "total_naves": naves.count(),
        "total_quartos": quartos.count(),
        "total_capacidade": total_capacidade,
        "total_vagas": max(total_capacidade - total_ocupados, 0),
        "total_internados": internados.count(),
        "quarto_tipos": Quarto.Tipo.choices,
    }


@login_required
def modulo_internamento(request):
    """Fragmento SPA — painel do módulo de Internamento."""
    return render(request, "internamento/painel.html", _contexto_painel_internamento(request))


# =========================================================================
# NAVE
# =========================================================================

@login_required
@requer_permissao("nave.cadastrar")
def cadastrar_nave(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    if not request.user.hospital:
        return JsonResponse({"ok": False, "erro": "O seu utilizador não está vinculado a nenhum hospital."}, status=400)

    nome = request.POST.get("nave_nome", "").strip()
    descricao = request.POST.get("nave_descricao", "").strip()

    erros = []
    if not nome:
        erros.append("Nome é obrigatório.")
    elif Nave.objects.filter(hospital=request.user.hospital, nome__iexact=nome).exists():
        erros.append("Já existe uma nave com este nome neste hospital.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    nave = Nave.objects.create(
        hospital=request.user.hospital,
        nome=nome,
        descricao=descricao,
    )

    return JsonResponse({
        "ok": True,
        "mensagem": f"Nave {nave.nome} cadastrada com sucesso.",
        "id": nave.id,
    })


@login_required
@requer_permissao("nave.gerir")
def eliminar_nave(request, id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        nave = Nave.objects.get(id=id, hospital=request.user.hospital)
    except Nave.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Nave não encontrada."}, status=404)

    nome = nave.nome
    try:
        nave.delete()
    except ProtectedError:
        return JsonResponse({
            "ok": False,
            "erro": f"Não é possível eliminar {nome}: existem quartos associados. Elimine-os primeiro ou desactive a nave.",
        }, status=400)

    return JsonResponse({"ok": True, "mensagem": f"Nave {nome} eliminada com sucesso."})


# =========================================================================
# QUARTO
# =========================================================================

@login_required
@requer_permissao("nave.cadastrar")
def cadastrar_quarto(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    nave_id = request.POST.get("quarto_nave_id", "").strip()
    numero = request.POST.get("quarto_numero", "").strip()
    tipo = request.POST.get("quarto_tipo", "").strip().upper()
    capacidade_str = request.POST.get("quarto_capacidade", "").strip()

    erros = []

    nave = None
    if not nave_id:
        erros.append("Nave é obrigatória.")
    else:
        try:
            nave = Nave.objects.get(id=nave_id, hospital=request.user.hospital)
        except Nave.DoesNotExist:
            erros.append("Nave não encontrada.")

    if not numero:
        erros.append("Número do quarto é obrigatório.")
    if tipo not in Quarto.Tipo.values:
        erros.append("Tipo de quarto inválido.")

    capacidade = None
    if not capacidade_str:
        erros.append("Capacidade é obrigatória.")
    else:
        try:
            capacidade = int(capacidade_str)
            if capacidade <= 0:
                erros.append("Capacidade tem de ser maior que zero.")
        except ValueError:
            erros.append("Capacidade inválida.")

    if nave and numero and Quarto.objects.filter(nave=nave, numero=numero).exists():
        erros.append("Já existe um quarto com este número nesta nave.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    quarto = Quarto.objects.create(
        nave=nave,
        numero=numero,
        tipo=tipo,
        capacidade=capacidade,
    )

    return JsonResponse({
        "ok": True,
        "mensagem": f"Quarto {quarto.numero} cadastrado em {nave.nome}.",
        "id": quarto.id,
    })


@login_required
@requer_permissao("nave.gerir")
def eliminar_quarto(request, id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        quarto = Quarto.objects.get(id=id, nave__hospital=request.user.hospital)
    except Quarto.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Quarto não encontrado."}, status=404)

    if quarto.ocupados > 0:
        return JsonResponse({"ok": False, "erro": "Não é possível eliminar: existem pacientes internados neste quarto."}, status=400)

    identificacao = f"{quarto.nave.nome} — Quarto {quarto.numero}"
    try:
        quarto.delete()
    except ProtectedError:
        return JsonResponse({
            "ok": False,
            "erro": f"Não é possível eliminar {identificacao}: existem registos associados.",
        }, status=400)

    return JsonResponse({"ok": True, "mensagem": f"{identificacao} eliminado com sucesso."})


@login_required
@requer_permissao("internamento.cadastrar")
def listar_quartos_disponiveis(request):
    """
    Quartos com vagas — usado pelo formulário de internamento na Ficha de
    Atendimento, para o médico só ver opções onde ainda cabe alguém.
    """
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    quartos = Quarto.objects.filter(
        nave__hospital=request.user.hospital, ativo=True
    ).select_related("nave").annotate(
        ocupados_count=Count(
            "internamentos",
            filter=Q(internamentos__status=Internamento.Status.INTERNADO),
        )
    ).order_by("nave__nome", "numero")

    return JsonResponse({
        "ok": True,
        "quartos": [
            {
                "id": q.id,
                "nave": q.nave.nome,
                "numero": q.numero,
                "tipo": q.get_tipo_display(),
                "vagas_disponiveis": max(q.capacidade - q.ocupados_count, 0),
            }
            for q in quartos if q.capacidade > q.ocupados_count
        ]
    })


# =========================================================================
# INTERNAMENTO (admissão, a partir do Atendimento)
# =========================================================================

@login_required
@requer_permissao("internamento.cadastrar")
def cadastrar_internamento(request):
    """
    Cria o internamento a partir de um Atendimento — mesmo padrão de
    cadastrar_prescricao/cadastrar_solicitacao_exame. Verifica vaga no
    quarto antes de criar; nunca interna acima da capacidade.
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    if not request.user.hospital:
        return JsonResponse({"ok": False, "erro": "O seu utilizador não está vinculado a nenhum hospital."}, status=400)

    atendimento_id = request.POST.get("internamento_atendimento_id", "").strip()
    quarto_id = request.POST.get("internamento_quarto_id", "").strip()
    motivo = request.POST.get("internamento_motivo", "").strip()
    observacoes = request.POST.get("internamento_observacoes", "").strip()

    erros = []

    atendimento = None
    if not atendimento_id:
        erros.append("Atendimento é obrigatório.")
    else:
        try:
            atendimento = Atendimento.objects.get(id=atendimento_id, hospital=request.user.hospital)
        except Atendimento.DoesNotExist:
            erros.append("Atendimento não encontrado.")
        else:
            if Internamento.objects.filter(atendimento=atendimento).exists():
                erros.append("Este atendimento já tem um internamento associado.")

    quarto = None
    if not quarto_id:
        erros.append("Quarto é obrigatório.")
    else:
        try:
            quarto = Quarto.objects.get(id=quarto_id, nave__hospital=request.user.hospital)
        except Quarto.DoesNotExist:
            erros.append("Quarto não encontrado.")
        else:
            if quarto.vagas_disponiveis <= 0:
                erros.append(f"O quarto {quarto.numero} não tem vagas disponíveis.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    internamento = Internamento.objects.create(
        hospital=request.user.hospital,
        atendimento=atendimento,
        paciente=atendimento.paciente,
        quarto=quarto,
        medico_responsavel=request.user,
        motivo=motivo,
        observacoes=observacoes,
        status=Internamento.Status.INTERNADO,
    )

    return JsonResponse({
        "ok": True,
        "mensagem": f"{internamento.paciente.nome_completo} internado no Quarto {quarto.numero} ({quarto.nave.nome}).",
        "internamento_id": internamento.id,
    })


@login_required
@requer_permissao("internamento.gerir")
def listar_internados(request):
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    internamentos = Internamento.objects.filter(
        hospital=request.user.hospital,
        status=Internamento.Status.INTERNADO,
    ).select_related("paciente", "quarto", "quarto__nave", "medico_responsavel").order_by("-data_entrada")

    resultado = []
    for i in internamentos:
        documento_bi = i.paciente.documentos.filter(tipo=DocumentoPaciente.TipoDocumento.BI).first()
        resultado.append({
            "id": i.id,
            "paciente": i.paciente.nome_completo,
            "paciente_codigo": i.paciente.codigo,
            "bi": documento_bi.numero if documento_bi else "",
            "nave": i.quarto.nave.nome,
            "quarto": i.quarto.numero,
            "medico": i.medico_responsavel.nome_completo,
            "data_entrada": i.data_entrada.isoformat(),
            "motivo": i.motivo,
        })

    return JsonResponse({"ok": True, "internamentos": resultado})


@login_required
@requer_permissao("internamento.gerir")
def dar_alta(request, id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        internamento = Internamento.objects.get(id=id, hospital=request.user.hospital)
    except Internamento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Internamento não encontrado."}, status=404)

    if internamento.status != Internamento.Status.INTERNADO:
        return JsonResponse({"ok": False, "erro": "Este internamento já não está activo."}, status=400)

    internamento.status = Internamento.Status.ALTA
    internamento.data_alta = timezone.now()
    internamento.save(update_fields=["status", "data_alta"])

    return JsonResponse({
        "ok": True,
        "mensagem": f"Alta registada para {internamento.paciente.nome_completo}.",
    })