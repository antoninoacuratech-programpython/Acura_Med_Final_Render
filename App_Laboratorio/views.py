from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.db import transaction, models
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from App_Usuarios.permissoes import requer_permissao
from App_Atendimentos.atendimento import Atendimento

from .tipo_exame import TipoExame
from .parametro import Parametro
from .valor_referencia import ValorReferencia
from .exame_parametro import ExameParametro
from .solicitacao_exame import SolicitacaoExame
from .item_solicitacao_exame import ItemSolicitacaoExame
from .resultado_parametro import ResultadoParametro


def _contexto_painel_laboratorio(request):
    exames = TipoExame.objects.filter(ativo=True).order_by("nome")

    return {
        "exames": exames,
        "total_departamentos": exames.values("departamento").distinct().count(),
        "exame_departamentos": TipoExame.Departamento.choices,
        "exame_metodos": TipoExame.Metodo.choices,
        "exame_tipos_amostra": TipoExame.TipoAmostra.choices,
        "exame_tipos_resultado": TipoExame.TipoResultado.choices,
        "parametro_tipos_resultado": Parametro.TipoResultado.choices,
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
    codigo_padronizado = request.POST.get("exame_codigo_padronizado", "").strip()
    departamento = request.POST.get("exame_departamento", "").strip().upper()
    nome = request.POST.get("exame_nome", "").strip()
    nome_tecnico = request.POST.get("exame_nome_tecnico", "").strip()
    metodo = request.POST.get("exame_metodo", "").strip().upper()
    tipo_amostra = request.POST.get("exame_tipo_amostra", "").strip().upper()
    tipo_resultado = request.POST.get("exame_tipo_resultado", "").strip().upper()
    tempo_estimado = request.POST.get("exame_tempo_estimado", "").strip()
    instrucoes_preparacao = request.POST.get("exame_instrucoes_preparacao", "").strip()

    erros = []
    if not codigo:
        erros.append("Código é obrigatório.")
    elif TipoExame.objects.filter(codigo=codigo).exists():
        erros.append("Já existe um exame com este código.")
    if not nome:
        erros.append("Nome é obrigatório.")
    if departamento not in TipoExame.Departamento.values:
        erros.append("Departamento inválido.")
    if tipo_amostra not in TipoExame.TipoAmostra.values:
        erros.append("Tipo de amostra inválido.")
    if tipo_resultado not in TipoExame.TipoResultado.values:
        erros.append("Tipo de resultado inválido.")
    if metodo and metodo not in TipoExame.Metodo.values:
        erros.append("Método inválido.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        exame = TipoExame.objects.create(
            codigo=codigo,
            codigo_padronizado=codigo_padronizado,
            departamento=departamento,
            nome=nome,
            nome_tecnico=nome_tecnico,
            metodo=metodo,
            tipo_amostra=tipo_amostra,
            tipo_resultado=tipo_resultado,
            tempo_estimado=tempo_estimado,
            instrucoes_preparacao=instrucoes_preparacao,
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
            "codigo_padronizado": exame.codigo_padronizado,
            "departamento": exame.departamento,
            "nome": exame.nome,
            "nome_tecnico": exame.nome_tecnico,
            "metodo": exame.metodo,
            "tipo_amostra": exame.tipo_amostra,
            "tipo_resultado": exame.tipo_resultado,
            "tempo_estimado": exame.tempo_estimado,
            "instrucoes_preparacao": exame.instrucoes_preparacao,
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
    codigo_padronizado = request.POST.get("exame_codigo_padronizado", "").strip()
    departamento = request.POST.get("exame_departamento", "").strip().upper()
    nome = request.POST.get("exame_nome", "").strip()
    nome_tecnico = request.POST.get("exame_nome_tecnico", "").strip()
    metodo = request.POST.get("exame_metodo", "").strip().upper()
    tipo_amostra = request.POST.get("exame_tipo_amostra", "").strip().upper()
    tipo_resultado = request.POST.get("exame_tipo_resultado", "").strip().upper()
    tempo_estimado = request.POST.get("exame_tempo_estimado", "").strip()
    instrucoes_preparacao = request.POST.get("exame_instrucoes_preparacao", "").strip()
    ativo = request.POST.get("exame_ativo") == "on"

    erros = []
    if not codigo:
        erros.append("Código é obrigatório.")
    elif TipoExame.objects.filter(codigo=codigo).exclude(id=exame.id).exists():
        erros.append("Já existe outro exame com este código.")
    if not nome:
        erros.append("Nome é obrigatório.")
    if departamento not in TipoExame.Departamento.values:
        erros.append("Departamento inválido.")
    if tipo_amostra not in TipoExame.TipoAmostra.values:
        erros.append("Tipo de amostra inválido.")
    if tipo_resultado not in TipoExame.TipoResultado.values:
        erros.append("Tipo de resultado inválido.")
    if metodo and metodo not in TipoExame.Metodo.values:
        erros.append("Método inválido.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        exame.codigo = codigo
        exame.codigo_padronizado = codigo_padronizado
        exame.departamento = departamento
        exame.nome = nome
        exame.nome_tecnico = nome_tecnico
        exame.metodo = metodo
        exame.tipo_amostra = tipo_amostra
        exame.tipo_resultado = tipo_resultado
        exame.tempo_estimado = tempo_estimado
        exame.instrucoes_preparacao = instrucoes_preparacao
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


def _referencia_para_paciente(parametro, paciente):
    """
    Escolhe a linha de ValorReferencia mais adequada ao sexo/idade do
    paciente. Prefere uma linha específica do sexo do paciente a uma
    linha "Ambos", se ambas existirem e a idade encaixar nas duas.
    """
    idade = paciente.idade
    sexo_paciente = paciente.sexo

    melhor = None
    for vr in parametro.valores_referencia.filter(
        models.Q(sexo=sexo_paciente) | models.Q(sexo=ValorReferencia.Sexo.AMBOS)
    ):
        if vr.idade_minima is not None and idade < vr.idade_minima:
            continue
        if vr.idade_maxima is not None and idade > vr.idade_maxima:
            continue
        if melhor is None:
            melhor = vr
        if vr.sexo == sexo_paciente:
            melhor = vr
            break

    return melhor


def _formatar_referencia(vr):
    if not vr:
        return ""
    if vr.valor_texto:
        return vr.valor_texto

    tem_min = vr.valor_minimo is not None
    tem_max = vr.valor_maximo is not None

    if tem_min and tem_max and vr.sinal_minimo == ValorReferencia.Sinal.NENHUM and vr.sinal_maximo == ValorReferencia.Sinal.NENHUM:
        return f"{vr.valor_minimo} – {vr.valor_maximo}"
    if tem_min:
        sinal = vr.sinal_minimo if vr.sinal_minimo != ValorReferencia.Sinal.NENHUM else "≥"
        return f"{sinal} {vr.valor_minimo}"
    if tem_max:
        sinal = vr.sinal_maximo if vr.sinal_maximo != ValorReferencia.Sinal.NENHUM else "≤"
        return f"{sinal} {vr.valor_maximo}"
    return ""


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

    itens_json = []
    for item in solicitacao.itens.select_related("tipo_exame").all():
        item_data = {
            "id": item.id,
            "tipo_exame": item.tipo_exame.nome,
            "departamento": item.tipo_exame.get_departamento_display(),
            "tipo_amostra": item.tipo_exame.get_tipo_amostra_display(),
            "tipo_resultado_exame": item.tipo_exame.tipo_resultado,
            "observacoes": item.observacoes,
            "resultado": item.resultado,
            "data_colheita": item.data_colheita.isoformat() if item.data_colheita else None,
            "data_resultado": item.data_resultado.isoformat() if item.data_resultado else None,
        }

        if item.tipo_exame.tipo_resultado == TipoExame.TipoResultado.MULTIPARAMETRO:
            resultados_existentes = {
                rp.parametro_id: rp.valor for rp in item.resultados_parametro.all()
            }
            ligacoes = ExameParametro.objects.filter(
                tipo_exame=item.tipo_exame
            ).select_related("parametro").order_by("ordem")

            item_data["parametros"] = [
                {
                    "parametro_id": lig.parametro.id,
                    "nome": lig.parametro.nome,
                    "unidade": lig.unidade or lig.parametro.unidade,
                    "subgrupo": lig.subgrupo,
                    "referencia": _formatar_referencia(_referencia_para_paciente(lig.parametro, solicitacao.paciente)),
                    "valor": resultados_existentes.get(lig.parametro.id, ""),
                }
                for lig in ligacoes
            ]

        itens_json.append(item_data)

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
            "itens": itens_json,
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
    param_item_ids = request.POST.getlist("resultado_parametro_item_id[]")
    param_ids = request.POST.getlist("resultado_parametro_parametro_id[]")
    param_valores = request.POST.getlist("resultado_parametro_valor[]")

    if not item_ids and not param_item_ids:
        return JsonResponse({"ok": False, "erro": "Nenhum item recebido."}, status=400)

    # Agrupa as linhas de parâmetro por item, para as processar de uma vez.
    parametros_por_item = {}
    for i, item_id in enumerate(param_item_ids):
        parametros_por_item.setdefault(item_id, []).append(
            (param_ids[i] if i < len(param_ids) else None, param_valores[i] if i < len(param_valores) else "")
        )

    agora = timezone.now()
    algum_vazio = False

    # Itens simples (Numérico/Qualitativo/Texto Livre) — resultado único.
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

    # Itens Multiparâmetro — um ResultadoParametro por linha.
    for item_id, linhas in parametros_por_item.items():
        try:
            item = solicitacao.itens.get(id=item_id)
        except ItemSolicitacaoExame.DoesNotExist:
            continue

        if not linhas:
            algum_vazio = True
            continue

        item_tem_vazio = False
        for parametro_id, valor in linhas:
            valor = (valor or "").strip()
            if not valor or not parametro_id:
                item_tem_vazio = True
                continue
            ResultadoParametro.objects.update_or_create(
                item_solicitacao=item, parametro_id=parametro_id,
                defaults={"valor": valor},
            )

        if item_tem_vazio:
            algum_vazio = True

        if not item.data_colheita:
            item.data_colheita = agora
        item.data_resultado = agora
        item.save(update_fields=["data_colheita", "data_resultado"])

    if algum_vazio:
        return JsonResponse({
            "ok": False,
            "erro": "Preencha o resultado de todos os exames/parâmetros antes de concluir.",
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
                    "departamento": item.tipo_exame.get_departamento_display(),
                    "resultado": item.resultado,
                    "data_resultado": item.data_resultado.isoformat() if item.data_resultado else None,
                }
                for item in solicitacao.itens.select_related("tipo_exame").all()
            ]
        }
    })


# =========================================================================
# PARÂMETROS DE UM TIPO DE EXAME (Multiparâmetro)
# =========================================================================

@login_required
@requer_permissao("tipoexame.gerir")
def listar_parametros_exame(request, tipo_exame_id):
    """Lista os parâmetros já associados a um exame, na ordem definida."""
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        exame = TipoExame.objects.get(id=tipo_exame_id)
    except TipoExame.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Exame não encontrado."}, status=404)

    ligacoes = ExameParametro.objects.filter(tipo_exame=exame).select_related("parametro").order_by("ordem")

    return JsonResponse({
        "ok": True,
        "exame_nome": exame.nome,
        "parametros": [
            {
                "id": lig.id,
                "parametro_id": lig.parametro.id,
                "nome": lig.parametro.nome,
                "unidade": lig.parametro.unidade,
                "tipo_resultado": lig.parametro.tipo_resultado,
                "tipo_resultado_display": lig.parametro.get_tipo_resultado_display(),
                "subgrupo": lig.subgrupo,
                "ordem": lig.ordem,
                "total_referencias": lig.parametro.valores_referencia.count(),
            }
            for lig in ligacoes
        ]
    })


@login_required
@requer_permissao("tipoexame.gerir")
def detalhe_parametro_exame(request, id):
    """Detalhe completo para edição — Parametro + ExameParametro + todas as ValorReferencia."""
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        ligacao = ExameParametro.objects.select_related("parametro").get(id=id)
    except ExameParametro.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Parâmetro não encontrado."}, status=404)

    parametro = ligacao.parametro

    return JsonResponse({
        "ok": True,
        "ligacao_id": ligacao.id,
        "parametro": {
            "id": parametro.id,
            "nome": parametro.nome,
            "unidade": parametro.unidade,
            "tipo_resultado": parametro.tipo_resultado,
            "descricao": parametro.descricao,
        },
        "subgrupo": ligacao.subgrupo,
        "ordem": ligacao.ordem,
        "grupos": [
            {
                "id": vr.id,
                "grupo": vr.grupo,
                "sexo": vr.sexo,
                "idade_minima": str(vr.idade_minima) if vr.idade_minima is not None else "",
                "idade_maxima": str(vr.idade_maxima) if vr.idade_maxima is not None else "",
                "sinal_minimo": vr.sinal_minimo,
                "valor_minimo": str(vr.valor_minimo) if vr.valor_minimo is not None else "",
                "sinal_maximo": vr.sinal_maximo,
                "valor_maximo": str(vr.valor_maximo) if vr.valor_maximo is not None else "",
                "critico_minimo": str(vr.critico_minimo) if vr.critico_minimo is not None else "",
                "critico_maximo": str(vr.critico_maximo) if vr.critico_maximo is not None else "",
                "valor_texto": vr.valor_texto,
            }
            for vr in parametro.valores_referencia.all()
        ],
    })


def _gerar_codigo_parametro(nome):
    """Gera um código único a partir do nome (ex.: 'Hemoglobina' → 'HEMOGLOBINA')."""
    base = "".join(c for c in nome.upper() if c.isalnum())[:10] or "PARAM"
    codigo = base
    contador = 1
    while Parametro.objects.filter(codigo=codigo).exists():
        contador += 1
        codigo = f"{base}{contador}"
    return codigo


@login_required
@requer_permissao("tipoexame.gerir")
@transaction.atomic
def salvar_parametro_exame(request, tipo_exame_id):
    """
    Guarda o formulário composto do mockup — cria/actualiza o Parametro,
    a ligação ExameParametro, e substitui todas as linhas de
    ValorReferencia pelas que vierem no POST (apaga as antigas e recria,
    mais simples do que tentar casar cada linha individualmente).
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        exame = TipoExame.objects.get(id=tipo_exame_id)
    except TipoExame.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Exame não encontrado."}, status=404)

    ligacao_id = request.POST.get("ligacao_id", "").strip()
    nome = request.POST.get("parametro_nome", "").strip()
    unidade = request.POST.get("parametro_unidade", "").strip()
    tipo_resultado = request.POST.get("parametro_tipo_resultado", "").strip().upper()
    descricao = request.POST.get("parametro_observacoes", "").strip()
    subgrupo = request.POST.get("exameparametro_subgrupo", "").strip()
    ordem_str = request.POST.get("exameparametro_ordem", "0").strip()

    erros = []
    if not nome:
        erros.append("Nome do parâmetro é obrigatório.")
    if tipo_resultado not in Parametro.TipoResultado.values:
        erros.append("Tipo de resultado inválido.")

    try:
        ordem = int(ordem_str) if ordem_str else 0
    except ValueError:
        ordem = 0

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    # Reaproveita o Parametro se já estivermos a editar uma ligação
    # existente; senão cria um novo (com código gerado automaticamente).
    if ligacao_id:
        try:
            ligacao = ExameParametro.objects.select_related("parametro").get(id=ligacao_id, tipo_exame=exame)
            parametro = ligacao.parametro
        except ExameParametro.DoesNotExist:
            return JsonResponse({"ok": False, "erro": "Ligação não encontrada."}, status=404)

        parametro.nome = nome
        parametro.unidade = unidade
        parametro.tipo_resultado = tipo_resultado
        parametro.descricao = descricao
        parametro.save()
    else:
        parametro = Parametro.objects.create(
            codigo=_gerar_codigo_parametro(nome),
            nome=nome,
            unidade=unidade,
            tipo_resultado=tipo_resultado,
            descricao=descricao,
        )
        ligacao, _ = ExameParametro.objects.get_or_create(tipo_exame=exame, parametro=parametro)

    ligacao.subgrupo = subgrupo
    ligacao.ordem = ordem
    ligacao.save()

    # Substitui todas as referências pelas que vieram agora do formulário.
    parametro.valores_referencia.all().delete()

    grupos_nome = request.POST.getlist("grupo_nome[]")
    grupos_sexo = request.POST.getlist("grupo_sexo[]")
    grupos_idade_min = request.POST.getlist("grupo_idade_min[]")
    grupos_idade_max = request.POST.getlist("grupo_idade_max[]")
    grupos_sinal_min = request.POST.getlist("grupo_sinal_min[]")
    grupos_ref_min = request.POST.getlist("grupo_ref_min[]")
    grupos_sinal_max = request.POST.getlist("grupo_sinal_max[]")
    grupos_ref_max = request.POST.getlist("grupo_ref_max[]")
    grupos_critico_min = request.POST.getlist("grupo_critico_min[]")
    grupos_critico_max = request.POST.getlist("grupo_critico_max[]")
    grupos_ref_textual = request.POST.getlist("grupo_ref_textual[]")

    def _dec(valor):
        valor = (valor or "").strip()
        if not valor:
            return None
        try:
            return Decimal(valor)
        except InvalidOperation:
            return None

    for i, grupo_nome in enumerate(grupos_nome):
        ValorReferencia.objects.create(
            parametro=parametro,
            grupo=grupo_nome.strip() or "Adulto",
            sexo=grupos_sexo[i] if i < len(grupos_sexo) else ValorReferencia.Sexo.AMBOS,
            idade_minima=_dec(grupos_idade_min[i]) if i < len(grupos_idade_min) else None,
            idade_maxima=_dec(grupos_idade_max[i]) if i < len(grupos_idade_max) else None,
            sinal_minimo=grupos_sinal_min[i] if i < len(grupos_sinal_min) else ValorReferencia.Sinal.NENHUM,
            valor_minimo=_dec(grupos_ref_min[i]) if i < len(grupos_ref_min) else None,
            sinal_maximo=grupos_sinal_max[i] if i < len(grupos_sinal_max) else ValorReferencia.Sinal.NENHUM,
            valor_maximo=_dec(grupos_ref_max[i]) if i < len(grupos_ref_max) else None,
            critico_minimo=_dec(grupos_critico_min[i]) if i < len(grupos_critico_min) else None,
            critico_maximo=_dec(grupos_critico_max[i]) if i < len(grupos_critico_max) else None,
            valor_texto=grupos_ref_textual[i].strip() if i < len(grupos_ref_textual) else "",
        )

    return JsonResponse({
        "ok": True,
        "mensagem": f"Parâmetro {parametro.nome} guardado com sucesso.",
        "ligacao_id": ligacao.id,
    })


@login_required
@requer_permissao("tipoexame.gerir")
def eliminar_parametro_exame(request, id):
    """
    Remove só a ligação a ESTE exame — o Parametro em si continua a
    existir (pode estar ligado a outros exames).
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        ligacao = ExameParametro.objects.select_related("parametro").get(id=id)
    except ExameParametro.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Parâmetro não encontrado."}, status=404)

    nome = ligacao.parametro.nome
    ligacao.delete()

    return JsonResponse({"ok": True, "mensagem": f"Parâmetro {nome} removido deste exame."})