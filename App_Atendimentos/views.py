from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from django.utils import timezone

from App_Usuarios.permissoes import requer_permissao
from App_Usuarios.ultilizador import Utilizador
from App_Usuarios.entidade_vinculada import EntidadeVinculada
from App_Pacientes.paciente import Paciente
from App_Pacientes.documento import DocumentoPaciente
from App_Agendamentos.agendamento import Agendamento
from App_Farmacia.medicamento import Medicamento

from .atendimento import Atendimento
from .consulta import Consulta


def _parse_int(valor):
    valor = (valor or "").strip()
    if not valor:
        return None
    try:
        return int(valor)
    except ValueError:
        return None


def _parse_decimal(valor):
    valor = (valor or "").strip()
    if not valor:
        return None
    try:
        return Decimal(valor)
    except InvalidOperation:
        return None


# =========================================================================
# ATENDIMENTO (fila da recepção)
# =========================================================================

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
@requer_permissao("atendimento.cadastrar")
def cadastrar_atendimento(request):
    """
    Walk-in: paciente chega directamente, sem marcação prévia.
    'agendamento' fica NULL neste registo.
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    if not request.user.hospital:
        return JsonResponse({
            "ok": False,
            "erro": "O seu utilizador não está vinculado a nenhum hospital."
        }, status=400)

    paciente_codigo = request.POST.get("atendimento_paciente_codigo", "").strip()
    profissional_id = request.POST.get("atendimento_profissional_id", "").strip()
    entidade_id = request.POST.get("entidadeSelecionada", "").strip()
    tipo_plano = request.POST.get("tipo_plano", "").strip()
    subtipo_convenio = request.POST.get("subtipo_convenio", "").strip()
    prioridade = request.POST.get("prioridade", "").strip()
    tipo_atendimento = request.POST.get("tipo_atendimento", "").strip()

    erros = []

    paciente = None
    if not paciente_codigo:
        erros.append("Paciente é obrigatório.")
    else:
        try:
            paciente = Paciente.objects.get(codigo=paciente_codigo, hospital=request.user.hospital)
        except Paciente.DoesNotExist:
            erros.append("Paciente não encontrado neste hospital.")

    profissional = None
    if profissional_id:
        try:
            profissional = Utilizador.objects.get(id=profissional_id, hospital=request.user.hospital)
        except Utilizador.DoesNotExist:
            erros.append("Profissional não encontrado.")
    else:
        # Sem profissional definido ainda (vai para triagem/fila geral) —
        # aceite como válido; ajusta-se depois quando for chamado.
        pass

    if tipo_plano not in Atendimento.TipoPlano.values:
        erros.append("Tipo de plano inválido.")
    if prioridade not in Atendimento.Prioridade.values:
        erros.append("Prioridade inválida.")
    if tipo_atendimento not in Atendimento.TipoAtendimento.values:
        erros.append("Tipo de atendimento inválido.")

    entidade_vinculada = None
    if entidade_id:
        try:
            entidade_vinculada = EntidadeVinculada.objects.get(id=entidade_id)
        except EntidadeVinculada.DoesNotExist:
            pass  # ignora id inválido, não bloqueia o atendimento

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    atendimento = Atendimento.objects.create(
        hospital=request.user.hospital,
        paciente=paciente,
        agendamento=None,
        profissional=profissional or request.user,  # placeholder até haver triagem para reatribuir
        entidade_vinculada=entidade_vinculada,
        tipo_plano=tipo_plano,
        subtipo_convenio=subtipo_convenio,
        prioridade=prioridade,
        tipo_atendimento=tipo_atendimento,
        status=Atendimento.Status.AGUARDANDO,
        criado_por=request.user,
    )

    return JsonResponse({
        "ok": True,
        "mensagem": f"Atendimento de {paciente.nome_completo} registado na fila.",
        "atendimento_id": atendimento.id,
    })


@login_required
@requer_permissao("atendimento.cadastrar")
def iniciar_atendimento_de_agendamento(request, agendamento_id):
    """
    Check-in: o paciente marcou (Agendamento existe) e chegou fisicamente.
    Cria o Atendimento copiando os dados do agendamento e liga os dois.
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        agendamento = Agendamento.objects.get(id=agendamento_id, hospital=request.user.hospital)
    except Agendamento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Agendamento não encontrado."}, status=404)

    if Atendimento.objects.filter(agendamento=agendamento).exists():
        return JsonResponse({"ok": False, "erro": "Este agendamento já tem um atendimento associado."}, status=400)

    atendimento = Atendimento.objects.create(
        hospital=agendamento.hospital,
        paciente=agendamento.paciente,
        agendamento=agendamento,
        profissional=agendamento.profissional,
        tipo_plano=Atendimento.TipoPlano.PARTICULAR,
        prioridade=Atendimento.Prioridade.NORMAL,
        tipo_atendimento=Atendimento.TipoAtendimento.CONSULTA_GERAL,
        status=Atendimento.Status.AGUARDANDO,
        criado_por=request.user,
    )

    agendamento.status = Agendamento.Status.EM_ATENDIMENTO
    agendamento.save(update_fields=["status"])

    return JsonResponse({
        "ok": True,
        "mensagem": f"Check-in de {agendamento.paciente.nome_completo} feito com sucesso.",
        "atendimento_id": atendimento.id,
    })


@login_required
@requer_permissao("atendimento.gerir")
def listar_fila_atendimento(request):
    """
    Fila do dia: atendimentos já criados (walk-in ou check-in feito) +
    agendamentos de hoje que ainda não fizeram check-in.
    """
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    hoje = timezone.localdate()

    atendimentos = Atendimento.objects.filter(
        hospital=request.user.hospital,
        criado_em__date=hoje,
    ).exclude(status=Atendimento.Status.CANCELADO).select_related("paciente", "profissional")

    agendamentos_pendentes = Agendamento.objects.filter(
        hospital=request.user.hospital,
        data_hora__date=hoje,
        status__in=[Agendamento.Status.AGENDADO, Agendamento.Status.CONFIRMADO],
    ).exclude(
        id__in=Atendimento.objects.filter(agendamento__isnull=False).values_list("agendamento_id", flat=True)
    ).select_related("paciente", "profissional")

    fila = [
        {
            "tipo": "atendimento",
            "id": a.id,
            "paciente": a.paciente.nome_completo,
            "paciente_codigo": a.paciente.codigo,
            "profissional": a.profissional.nome_completo,
            "status": a.status,
            "status_display": a.get_status_display(),
            "tipo_atendimento": a.tipo_atendimento,
            "prioridade": a.prioridade,
            "criado_em": a.criado_em.isoformat(),
        }
        for a in atendimentos
    ] + [
        {
            "tipo": "agendamento_pendente",
            "id": ag.id,
            "paciente": ag.paciente.nome_completo,
            "paciente_codigo": ag.paciente.codigo,
            "profissional": ag.profissional.nome_completo,
            "status": "aguardando_chegada",
            "status_display": "Aguardando chegada",
            "tipo_atendimento": None,
            "prioridade": None,
            "criado_em": ag.data_hora.isoformat(),
        }
        for ag in agendamentos_pendentes
    ]

    return JsonResponse({"ok": True, "fila": fila})


@login_required
@requer_permissao("atendimento.atender")
def iniciar_atendimento(request, id):
    """Marca o atendimento como Em Atendimento — só o profissional atribuído pode iniciar."""
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        atendimento = Atendimento.objects.get(id=id, hospital=request.user.hospital)
    except Atendimento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Atendimento não encontrado."}, status=404)

    if atendimento.profissional_id != request.user.id:
        return JsonResponse({"ok": False, "erro": "Este atendimento não está atribuído a si."}, status=403)

    atendimento.status = Atendimento.Status.EM_ATENDIMENTO
    atendimento.save(update_fields=["status"])

    return JsonResponse({
        "ok": True,
        "mensagem": f"Atendimento de {atendimento.paciente.nome_completo} iniciado.",
        "atendimento_id": atendimento.id,
    })


@login_required
@requer_permissao("atendimento.atender")
def concluir_atendimento(request, id):
    """Marca o atendimento como Concluído — chamado depois de a receita ser enviada."""
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        atendimento = Atendimento.objects.get(id=id, hospital=request.user.hospital, profissional=request.user)
    except Atendimento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Atendimento não encontrado."}, status=404)

    atendimento.status = Atendimento.Status.CONCLUIDO
    atendimento.save(update_fields=["status"])

    return JsonResponse({"ok": True, "mensagem": "Atendimento concluído."})


@login_required
@requer_permissao("atendimento.atender")
def cadastrar_consulta(request, atendimento_id):
    """
    Guarda a ficha clínica. finalizar=1 marca o atendimento como
    Concluído; qualquer outro valor guarda como rascunho.
    Sinais vitais NÃO são tocados aqui — são exclusivamente da Triagem.
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        atendimento = Atendimento.objects.get(
            id=atendimento_id, hospital=request.user.hospital, profissional=request.user
        )
    except Atendimento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Atendimento não encontrado."}, status=404)

    consulta, _ = Consulta.objects.get_or_create(atendimento=atendimento)

    conduta = request.POST.get("conduta", "").strip().upper()
    if conduta and conduta not in Consulta.Conduta.values:
        return JsonResponse({"ok": False, "erro": "Conduta inválida."}, status=400)

    finalizar = request.POST.get("finalizar") == "1"

    if finalizar and not conduta:
        return JsonResponse({"ok": False, "erro": "Selecione uma conduta antes de finalizar."}, status=400)

    consulta.queixa_historia_atual = request.POST.get("queixa_historia_atual", "").strip()
    consulta.exame_fisico = request.POST.get("exame_fisico", "").strip()
    consulta.diagnostico_clinico = request.POST.get("diagnostico_clinico", "").strip()
    consulta.conduta = conduta
    consulta.observacoes_condutas = request.POST.get("observacoes_condutas", "").strip()
    consulta.rascunho = not finalizar
    consulta.save()

    if finalizar:
        atendimento.status = Atendimento.Status.CONCLUIDO
        atendimento.save(update_fields=["status"])

    return JsonResponse({
        "ok": True,
        "mensagem": "Atendimento finalizado." if finalizar else "Rascunho guardado.",
        "conduta": consulta.conduta,
        "finalizado": finalizar,
    })


# =========================================================================
# MEUS ATENDIMENTOS (fila do médico + ficha completa)
# =========================================================================

@login_required
@requer_permissao("atendimento.atender")
def modulo_meus_atendimentos(request):
    """Fragmento SPA — painel do médico com a fila só dele."""
    medicamentos = Medicamento.objects.filter(ativo=True).order_by("nome")
    return render(
        request,
        "meus_atendimentos/painel.html",
        {"medicamentos": medicamentos},
    )


@login_required
@requer_permissao("atendimento.atender")
def listar_meus_atendimentos(request):
    """Fila de hoje, filtrada só pelos atendimentos atribuídos a este profissional."""
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    hoje = timezone.localdate()

    atendimentos = Atendimento.objects.filter(
        hospital=request.user.hospital,
        profissional=request.user,
        criado_em__date=hoje,
    ).exclude(status=Atendimento.Status.CANCELADO).select_related("paciente").order_by("criado_em")

    return JsonResponse({
        "ok": True,
        "atendimentos": [
            {
                "id": a.id,
                "paciente": a.paciente.nome_completo,
                "paciente_codigo": a.paciente.codigo,
                "tipo_atendimento": a.tipo_atendimento,
                "prioridade": a.prioridade,
                "status": a.status,
                "status_display": a.get_status_display(),
                "criado_em": a.criado_em.isoformat(),
            }
            for a in atendimentos
        ]
    })


@login_required
@requer_permissao("atendimento.atender")
def ficha_atendimento(request, id):
    try:
        atendimento = Atendimento.objects.select_related("paciente").get(
            id=id, hospital=request.user.hospital, profissional=request.user
        )
    except Atendimento.DoesNotExist:
        return HttpResponseNotFound("Atendimento não encontrado ou não atribuído a si.")

    consulta, _ = Consulta.objects.get_or_create(atendimento=atendimento)
    medicamentos = Medicamento.objects.filter(ativo=True).order_by("nome")

    documento_bi = atendimento.paciente.documentos.filter(
        tipo=DocumentoPaciente.TipoDocumento.BI
    ).first()

    return render(
        request,
        "meus_atendimentos/ficha.html",
        {
            "atendimento": atendimento,
            "consulta": consulta,
            "medicamentos": medicamentos,
            "documento_bi": documento_bi,
        },
    )


# =========================================================================
# TRIAGEM (fila do enfermeiro — sinais vitais)
# =========================================================================

@login_required
@requer_permissao("atendimento.triagem")
def modulo_triagem(request):
    """Fragmento SPA — fila de triagem (enfermeiro)."""
    return render(request, "triagem/painel.html", {})


@login_required
@requer_permissao("atendimento.triagem")
def listar_fila_triagem(request):
    """
    Todos os atendimentos de hoje ainda em Aguardando — não filtrado por
    profissional, porque o enfermeiro atende toda a fila.
    """
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    hoje = timezone.localdate()

    atendimentos = Atendimento.objects.filter(
        hospital=request.user.hospital,
        status__in=[Atendimento.Status.AGUARDANDO, Atendimento.Status.EM_ATENDIMENTO],
        criado_em__date=hoje,
    ).select_related("paciente", "consulta").order_by("criado_em")

    return JsonResponse({
        "ok": True,
        "atendimentos": [
            {
                "id": a.id,
                "paciente": a.paciente.nome_completo,
                "paciente_codigo": a.paciente.codigo,
                "prioridade": a.prioridade,
                "sinais_preenchidos": hasattr(a, "consulta") and bool(a.consulta.pressao_arterial),
                "criado_em": a.criado_em.isoformat(),
            }
            for a in atendimentos
        ]
    })


@login_required
@requer_permissao("atendimento.triagem")
def salvar_sinais_vitais(request, atendimento_id):
    """
    GET: devolve os sinais vitais já registados (para pré-preencher o
    modal em modo edição). POST: grava os 6 campos.

    Só toca nos 6 campos de sinais vitais — nunca em queixa, exame
    físico, diagnóstico ou conduta, que pertencem exclusivamente ao
    médico.
    """
    try:
        atendimento = Atendimento.objects.get(id=atendimento_id, hospital=request.user.hospital)
    except Atendimento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Atendimento não encontrado."}, status=404)

    consulta, _ = Consulta.objects.get_or_create(atendimento=atendimento)

    if request.method == "GET":
        documento_bi = atendimento.paciente.documentos.filter(
            tipo=DocumentoPaciente.TipoDocumento.BI
        ).first()

        return JsonResponse({
            "ok": True,
            "paciente": {
                "nome": atendimento.paciente.nome_completo,
                "bi": documento_bi.numero if documento_bi else "",
                "idade": atendimento.paciente.idade,
            },
            "sinais_vitais": {
                "pressao_arterial": consulta.pressao_arterial,
                "frequencia_cardiaca": consulta.frequencia_cardiaca,
                "frequencia_respiratoria": consulta.frequencia_respiratoria,
                "temperatura": str(consulta.temperatura) if consulta.temperatura is not None else "",
                "saturacao_o2": consulta.saturacao_o2,
                "glicemia_capilar": consulta.glicemia_capilar,
            }
        })

    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    consulta.pressao_arterial = request.POST.get("pressao_arterial", "").strip()
    consulta.frequencia_cardiaca = _parse_int(request.POST.get("frequencia_cardiaca"))
    consulta.frequencia_respiratoria = _parse_int(request.POST.get("frequencia_respiratoria"))
    consulta.temperatura = _parse_decimal(request.POST.get("temperatura"))
    consulta.saturacao_o2 = _parse_int(request.POST.get("saturacao_o2"))
    consulta.glicemia_capilar = _parse_int(request.POST.get("glicemia_capilar"))
    consulta.save()

    return JsonResponse({
        "ok": True,
        "mensagem": f"Sinais vitais de {atendimento.paciente.nome_completo} registados.",
    })