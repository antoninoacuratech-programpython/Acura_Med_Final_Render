from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from App_Usuarios.permissoes import requer_permissao
from App_Atendimentos.atendimento import Atendimento

from .tipo_exame import TipoExame
from .solicitacao_exame import SolicitacaoExame
from .item_solicitacao_exame import ItemSolicitacaoExame


def _contexto_painel_laboratorio(request):
    exames = TipoExame.objects.filter(ativo=True).order_by("nome")

    return {
        "exames": exames,
        "total_categorias": exames.values("categoria").distinct().count(),
        "exame_categorias": TipoExame.Categoria.choices,
        "exame_tipos_amostra": TipoExame.TipoAmostra.choices,
    }


@login_required
def modulo_laboratorio(request):
    """Fragmento SPA — painel do módulo de Laboratório."""
    return render(request, "laboratorio/painel.html", _contexto_painel_laboratorio(request))


@login_required
@requer_permissao("tipoexame.cadastrar")
def cadastrar_tipo_exame(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    codigo = request.POST.get("exame_codigo", "").strip()
    nome = request.POST.get("exame_nome", "").strip()
    categoria = request.POST.get("exame_categoria", "").strip().upper()
    tipo_amostra = request.POST.get("exame_tipo_amostra", "").strip().upper()
    valor_referencia = request.POST.get("exame_valor_referencia", "").strip()
    unidade_medida = request.POST.get("exame_unidade_medida", "").strip()
    tempo_estimado_str = request.POST.get("exame_tempo_estimado", "").strip()

    erros = []
    if not codigo:
        erros.append("Código é obrigatório.")
    elif TipoExame.objects.filter(codigo=codigo).exists():
        erros.append("Já existe um exame com este código.")
    if not nome:
        erros.append("Nome é obrigatório.")
    if categoria not in TipoExame.Categoria.values:
        erros.append("Categoria inválida.")
    if tipo_amostra not in TipoExame.TipoAmostra.values:
        erros.append("Tipo de amostra inválido.")

    tempo_estimado_horas = None
    if tempo_estimado_str:
        try:
            tempo_estimado_horas = int(tempo_estimado_str)
        except ValueError:
            erros.append("Tempo estimado inválido.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        exame = TipoExame.objects.create(
            codigo=codigo,
            nome=nome,
            categoria=categoria,
            tipo_amostra=tipo_amostra,
            valor_referencia=valor_referencia,
            unidade_medida=unidade_medida,
            tempo_estimado_horas=tempo_estimado_horas,
        )
    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao salvar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Exame {exame.nome} cadastrado com sucesso.",
        "id": exame.id,
    })


@login_required
@requer_permissao("tipoexame.gerir")
def detalhe_tipo_exame(request, id):
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        exame = TipoExame.objects.get(id=id)
    except TipoExame.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Exame não encontrado."}, status=404)

    return JsonResponse({
        "ok": True,
        "exame": {
            "id": exame.id,
            "codigo": exame.codigo,
            "nome": exame.nome,
            "categoria": exame.categoria,
            "tipo_amostra": exame.tipo_amostra,
            "valor_referencia": exame.valor_referencia,
            "unidade_medida": exame.unidade_medida,
            "tempo_estimado_horas": exame.tempo_estimado_horas,
            "ativo": exame.ativo,
        }
    })


@login_required
@requer_permissao("tipoexame.gerir")
def atualizar_tipo_exame(request, id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        exame = TipoExame.objects.get(id=id)
    except TipoExame.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Exame não encontrado."}, status=404)

    codigo = request.POST.get("exame_codigo", "").strip()
    nome = request.POST.get("exame_nome", "").strip()
    categoria = request.POST.get("exame_categoria", "").strip().upper()
    tipo_amostra = request.POST.get("exame_tipo_amostra", "").strip().upper()
    valor_referencia = request.POST.get("exame_valor_referencia", "").strip()
    unidade_medida = request.POST.get("exame_unidade_medida", "").strip()
    tempo_estimado_str = request.POST.get("exame_tempo_estimado", "").strip()
    ativo = request.POST.get("exame_ativo") == "on"

    erros = []
    if not codigo:
        erros.append("Código é obrigatório.")
    elif TipoExame.objects.filter(codigo=codigo).exclude(id=exame.id).exists():
        erros.append("Já existe outro exame com este código.")
    if not nome:
        erros.append("Nome é obrigatório.")
    if categoria not in TipoExame.Categoria.values:
        erros.append("Categoria inválida.")
    if tipo_amostra not in TipoExame.TipoAmostra.values:
        erros.append("Tipo de amostra inválido.")

    tempo_estimado_horas = exame.tempo_estimado_horas
    if tempo_estimado_str:
        try:
            tempo_estimado_horas = int(tempo_estimado_str)
        except ValueError:
            erros.append("Tempo estimado inválido.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        exame.codigo = codigo
        exame.nome = nome
        exame.categoria = categoria
        exame.tipo_amostra = tipo_amostra
        exame.valor_referencia = valor_referencia
        exame.unidade_medida = unidade_medida
        exame.tempo_estimado_horas = tempo_estimado_horas
        exame.ativo = ativo
        exame.save()
    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao atualizar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Exame {exame.nome} atualizado com sucesso.",
        "id": exame.id,
    })


@login_required
@requer_permissao("tipoexame.gerir")
def eliminar_tipo_exame(request, id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        exame = TipoExame.objects.get(id=id)
    except TipoExame.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Exame não encontrado."}, status=404)

    nome = exame.nome

    from django.db.models import ProtectedError
    try:
        exame.delete()
    except ProtectedError:
        return JsonResponse({
            "ok": False,
            "erro": f"Não é possível eliminar {nome}: existem solicitações associadas a este exame. Desactive-o em vez de eliminar.",
        }, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Exame {nome} eliminado com sucesso.",
    })


# =========================================================================
# SOLICITAÇÃO DE EXAME (criada pelo médico, a partir do Atendimento)
# =========================================================================

@login_required
@requer_permissao("solicitacao.cadastrar")
@transaction.atomic
def cadastrar_solicitacao_exame(request):
    """
    Cria a solicitação (cabeçalho) e todos os seus itens numa só chamada
    — mesmo padrão de cadastrar_prescricao. O frontend envia os campos de
    cada linha como arrays paralelos: item_tipo_exame_id[], item_observacoes[].
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    if not request.user.hospital:
        return JsonResponse({
            "ok": False,
            "erro": "O seu utilizador não está vinculado a nenhum hospital."
        }, status=400)

    atendimento_id = request.POST.get("solicitacao_atendimento_id", "").strip()
    observacoes = request.POST.get("solicitacao_observacoes", "").strip()

    tipo_exame_ids = request.POST.getlist("item_tipo_exame_id[]")
    item_observacoes = request.POST.getlist("item_observacoes[]")

    erros = []

    atendimento = None
    if not atendimento_id:
        erros.append("Atendimento é obrigatório.")
    else:
        try:
            atendimento = Atendimento.objects.get(id=atendimento_id, hospital=request.user.hospital)
        except Atendimento.DoesNotExist:
            erros.append("Atendimento não encontrado.")

    if not tipo_exame_ids:
        erros.append("Adicione pelo menos um exame à solicitação.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    solicitacao = SolicitacaoExame.objects.create(
        hospital=request.user.hospital,
        atendimento=atendimento,
        paciente=atendimento.paciente,
        medico=request.user,
        observacoes=observacoes,
        status=SolicitacaoExame.Status.AGUARDANDO,
    )

    itens_erros = []
    itens_criados = 0

    for i, tipo_exame_id in enumerate(tipo_exame_ids):
        try:
            tipo_exame = TipoExame.objects.get(id=tipo_exame_id)
        except (TipoExame.DoesNotExist, ValueError):
            itens_erros.append(f"Exame inválido na linha {i + 1}.")
            continue

        ItemSolicitacaoExame.objects.create(
            solicitacao=solicitacao,
            tipo_exame=tipo_exame,
            observacoes=item_observacoes[i] if i < len(item_observacoes) else "",
        )
        itens_criados += 1

    if itens_erros or itens_criados == 0:
        transaction.set_rollback(True)
        return JsonResponse({
            "ok": False,
            "erro": " ".join(itens_erros) if itens_erros else "Nenhum exame válido foi enviado.",
        }, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Solicitação de exames criada para {solicitacao.paciente.nome_completo} e enviada ao laboratório.",
        "solicitacao_id": solicitacao.id,
    })


# =========================================================================
# TÉCNICO PROCESSA AS SOLICITAÇÕES (Recepção + Colheita + Resultado)
# =========================================================================

@login_required
@requer_permissao("solicitacao.gerir")
def listar_solicitacoes_laboratorio(request):
    """Fila do laboratório: solicitações ainda não concluídas nem canceladas."""
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    solicitacoes = SolicitacaoExame.objects.filter(
        hospital=request.user.hospital,
        status__in=[SolicitacaoExame.Status.AGUARDANDO, SolicitacaoExame.Status.COLETADO],
    ).select_related("paciente", "medico").order_by("criado_em")

    return JsonResponse({
        "ok": True,
        "solicitacoes": [
            {
                "id": s.id,
                "paciente": s.paciente.nome_completo,
                "paciente_codigo": s.paciente.codigo,
                "medico": s.medico.nome_completo,
                "status": s.status,
                "status_display": s.get_status_display(),
                "total_itens": s.itens.count(),
                "criado_em": s.criado_em.isoformat(),
            }
            for s in solicitacoes
        ]
    })


@login_required
@requer_permissao("solicitacao.gerir")
def detalhe_solicitacao_laboratorio(request, id):
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        solicitacao = SolicitacaoExame.objects.select_related("paciente", "medico").get(
            id=id, hospital=request.user.hospital
        )
    except SolicitacaoExame.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Solicitação não encontrada."}, status=404)

    return JsonResponse({
        "ok": True,
        "solicitacao": {
            "id": solicitacao.id,
            "paciente": solicitacao.paciente.nome_completo,
            "paciente_codigo": solicitacao.paciente.codigo,
            "medico": solicitacao.medico.nome_completo,
            "status": solicitacao.status,
            "status_display": solicitacao.get_status_display(),
            "observacoes": solicitacao.observacoes,
            "criado_em": solicitacao.criado_em.isoformat(),
            "itens": [
                {
                    "id": item.id,
                    "tipo_exame": item.tipo_exame.nome,
                    "categoria": item.tipo_exame.get_categoria_display(),
                    "tipo_amostra": item.tipo_exame.get_tipo_amostra_display(),
                    "valor_referencia": item.tipo_exame.valor_referencia,
                    "unidade_medida": item.tipo_exame.unidade_medida,
                    "observacoes": item.observacoes,
                    "resultado": item.resultado,
                    "data_colheita": item.data_colheita.isoformat() if item.data_colheita else None,
                    "data_resultado": item.data_resultado.isoformat() if item.data_resultado else None,
                }
                for item in solicitacao.itens.select_related("tipo_exame").all()
            ],
        }
    })


@login_required
@requer_permissao("solicitacao.gerir")
def registar_colheita(request, id):
    """
    Marca a amostra como colhida — fecha a fase Pré-analítica. Regista a
    data/hora em cada item que ainda não a tinha (não sobrescreve se já
    tiver sido colhida antes).
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        solicitacao = SolicitacaoExame.objects.get(id=id, hospital=request.user.hospital)
    except SolicitacaoExame.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Solicitação não encontrada."}, status=404)

    if solicitacao.status not in (SolicitacaoExame.Status.AGUARDANDO, SolicitacaoExame.Status.COLETADO):
        return JsonResponse({"ok": False, "erro": "Esta solicitação já foi concluída ou cancelada."}, status=400)

    agora = timezone.now()
    for item in solicitacao.itens.all():
        if not item.data_colheita:
            item.data_colheita = agora
            item.save(update_fields=["data_colheita"])

    solicitacao.status = SolicitacaoExame.Status.COLETADO
    solicitacao.save(update_fields=["status"])

    return JsonResponse({
        "ok": True,
        "mensagem": f"Colheita registada para {solicitacao.paciente.nome_completo}.",
    })


@login_required
@requer_permissao("solicitacao.gerir")
def concluir_solicitacao_laboratorio(request, id):
    """
    Guarda os resultados de cada item e conclui a solicitação (fase
    Analítica + Pós-analítica). Se a colheita ainda não tinha sido
    registada separadamente, é preenchida automaticamente aqui — o
    fluxo combinado permite ao técnico fazer tudo de uma vez.
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        solicitacao = SolicitacaoExame.objects.get(id=id, hospital=request.user.hospital)
    except SolicitacaoExame.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Solicitação não encontrada."}, status=404)

    if solicitacao.status not in (SolicitacaoExame.Status.AGUARDANDO, SolicitacaoExame.Status.COLETADO):
        return JsonResponse({"ok": False, "erro": "Esta solicitação já foi concluída ou cancelada."}, status=400)

    item_ids = request.POST.getlist("item_id[]")
    resultados = request.POST.getlist("item_resultado[]")

    if not item_ids:
        return JsonResponse({"ok": False, "erro": "Nenhum item recebido."}, status=400)

    agora = timezone.now()
    algum_vazio = False

    for i, item_id in enumerate(item_ids):
        try:
            item = solicitacao.itens.get(id=item_id)
        except ItemSolicitacaoExame.DoesNotExist:
            continue

        resultado_texto = resultados[i].strip() if i < len(resultados) else ""
        if not resultado_texto:
            algum_vazio = True
            continue

        item.resultado = resultado_texto
        if not item.data_colheita:
            item.data_colheita = agora
        item.data_resultado = agora
        item.save(update_fields=["resultado", "data_colheita", "data_resultado"])

    if algum_vazio:
        return JsonResponse({
            "ok": False,
            "erro": "Preencha o resultado de todos os exames antes de concluir.",
        }, status=400)

    solicitacao.status = SolicitacaoExame.Status.CONCLUIDO
    solicitacao.save(update_fields=["status"])

    return JsonResponse({
        "ok": True,
        "mensagem": f"Resultados de {solicitacao.paciente.nome_completo} registados e solicitação concluída.",
    })


# =========================================================================
# RESULTADOS (o médico vê os resultados das solicitações que ele criou)
# =========================================================================

@login_required
@requer_permissao("solicitacao.cadastrar")
def listar_resultados_exame(request):
    """
    Solicitações já concluídas, criadas por este médico — não mostra as
    de outros médicos, cada um só vê o que pediu.
    """
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    solicitacoes = SolicitacaoExame.objects.filter(
        hospital=request.user.hospital,
        medico=request.user,
        status=SolicitacaoExame.Status.CONCLUIDO,
    ).select_related("paciente").order_by("-atualizado_em")

    return JsonResponse({
        "ok": True,
        "solicitacoes": [
            {
                "id": s.id,
                "paciente": s.paciente.nome_completo,
                "paciente_codigo": s.paciente.codigo,
                "total_itens": s.itens.count(),
                "concluido_em": s.atualizado_em.isoformat(),
            }
            for s in solicitacoes
        ]
    })


@login_required
@requer_permissao("solicitacao.cadastrar")
def detalhe_resultado_exame(request, id):
    """Detalhe só-leitura — o médico não edita resultados, só consulta."""
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        solicitacao = SolicitacaoExame.objects.select_related("paciente").get(
            id=id, hospital=request.user.hospital, medico=request.user
        )
    except SolicitacaoExame.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Solicitação não encontrada."}, status=404)

    return JsonResponse({
        "ok": True,
        "solicitacao": {
            "id": solicitacao.id,
            "paciente": solicitacao.paciente.nome_completo,
            "paciente_codigo": solicitacao.paciente.codigo,
            "status_display": solicitacao.get_status_display(),
            "itens": [
                {
                    "tipo_exame": item.tipo_exame.nome,
                    "categoria": item.tipo_exame.get_categoria_display(),
                    "valor_referencia": item.tipo_exame.valor_referencia,
                    "unidade_medida": item.tipo_exame.unidade_medida,
                    "resultado": item.resultado,
                    "data_resultado": item.data_resultado.isoformat() if item.data_resultado else None,
                }
                for item in solicitacao.itens.select_related("tipo_exame").all()
            ]
        }
    })