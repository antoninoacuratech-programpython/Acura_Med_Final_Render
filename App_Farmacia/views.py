from datetime import datetime, date, timedelta

from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.db.models import ProtectedError, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from reportlab.platypus import Table, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from App_Usuarios.permissoes import requer_permissao
from App_Usuarios.utils.pdf import (
    novo_documento_pdf, cabecalho_relatorio,
    estilo_tabela_padrao, finalizar_resposta_pdf,
)
from App_Prescricoes.prescricao_medicamento import PrescricaoMedicamento
from App_Pacientes.documento import DocumentoPaciente

from .medicamento import Medicamento
from .lote import Lote
from .movimento_stock import MovimentoStock
from .dispensacao import Dispensacao, ItemDispensacao
from .requisicao_interna import RequisicaoInterna
from .item_requisicao_interna import ItemRequisicaoInterna


# =========================================================================
# MEDICAMENTO (catálogo global — não tem hospital)
# =========================================================================

@login_required
@requer_permissao("medicamento.cadastrar")
def cadastrar_medicamento(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    codigo = request.POST.get("medicamento_codigo", "").strip()
    nome = request.POST.get("medicamento_nome", "").strip()
    principio_ativo = request.POST.get("medicamento_principio_ativo", "").strip()
    concentracao = request.POST.get("medicamento_concentracao", "").strip()
    forma_farmaceutica = request.POST.get("medicamento_forma_farmaceutica", "").strip().upper()
    unidade_medida = request.POST.get("medicamento_unidade_medida", "").strip().upper()
    classe_terapeutica = request.POST.get("medicamento_classe_terapeutica", "").strip()
    controlado = request.POST.get("medicamento_controlado") == "on"

    erros = []
    if not codigo:
        erros.append("Código é obrigatório.")
    if not nome:
        erros.append("Nome comercial é obrigatório.")
    if not principio_ativo:
        erros.append("Princípio activo é obrigatório.")
    if forma_farmaceutica not in Medicamento.FormaFarmaceutica.values:
        erros.append("Forma farmacêutica inválida.")
    if unidade_medida not in Medicamento.UnidadeMedida.values:
        erros.append("Unidade de medida inválida.")
    if codigo and Medicamento.objects.filter(codigo=codigo).exists():
        erros.append("Já existe um medicamento com este código.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        medicamento = Medicamento.objects.create(
            codigo=codigo,
            nome=nome,
            principio_ativo=principio_ativo,
            concentracao=concentracao,
            forma_farmaceutica=forma_farmaceutica,
            unidade_medida=unidade_medida,
            classe_terapeutica=classe_terapeutica,
            controlado=controlado,
        )
    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao salvar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Medicamento {medicamento.nome} cadastrado com sucesso.",
        "id": medicamento.id,
    })


@login_required
@requer_permissao("medicamento.gerir")
def detalhe_medicamento(request, id):
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        medicamento = Medicamento.objects.get(id=id)
    except Medicamento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Medicamento não encontrado."}, status=404)

    return JsonResponse({
        "ok": True,
        "medicamento": {
            "id": medicamento.id,
            "codigo": medicamento.codigo,
            "nome": medicamento.nome,
            "principio_ativo": medicamento.principio_ativo,
            "concentracao": medicamento.concentracao,
            "forma_farmaceutica": medicamento.forma_farmaceutica,
            "unidade_medida": medicamento.unidade_medida,
            "classe_terapeutica": medicamento.classe_terapeutica,
            "controlado": medicamento.controlado,
            "ativo": medicamento.ativo,
        }
    })


@login_required
@requer_permissao("medicamento.gerir")
def atualizar_medicamento(request, id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        medicamento = Medicamento.objects.get(id=id)
    except Medicamento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Medicamento não encontrado."}, status=404)

    codigo = request.POST.get("medicamento_codigo", "").strip()
    nome = request.POST.get("medicamento_nome", "").strip()
    principio_ativo = request.POST.get("medicamento_principio_ativo", "").strip()
    concentracao = request.POST.get("medicamento_concentracao", "").strip()
    forma_farmaceutica = request.POST.get("medicamento_forma_farmaceutica", "").strip().upper()
    unidade_medida = request.POST.get("medicamento_unidade_medida", "").strip().upper()
    classe_terapeutica = request.POST.get("medicamento_classe_terapeutica", "").strip()
    controlado = request.POST.get("medicamento_controlado") == "on"
    ativo = request.POST.get("medicamento_ativo") == "on"

    erros = []
    if not codigo:
        erros.append("Código é obrigatório.")
    if not nome:
        erros.append("Nome comercial é obrigatório.")
    if not principio_ativo:
        erros.append("Princípio activo é obrigatório.")
    if forma_farmaceutica not in Medicamento.FormaFarmaceutica.values:
        erros.append("Forma farmacêutica inválida.")
    if unidade_medida not in Medicamento.UnidadeMedida.values:
        erros.append("Unidade de medida inválida.")
    if codigo and Medicamento.objects.filter(codigo=codigo).exclude(id=medicamento.id).exists():
        erros.append("Já existe outro medicamento com este código.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        medicamento.codigo = codigo
        medicamento.nome = nome
        medicamento.principio_ativo = principio_ativo
        medicamento.concentracao = concentracao
        medicamento.forma_farmaceutica = forma_farmaceutica
        medicamento.unidade_medida = unidade_medida
        medicamento.classe_terapeutica = classe_terapeutica
        medicamento.controlado = controlado
        medicamento.ativo = ativo
        medicamento.save()
    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao atualizar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Medicamento {medicamento.nome} atualizado com sucesso.",
        "id": medicamento.id,
    })


@login_required
@requer_permissao("medicamento.gerir")
def eliminar_medicamento(request, id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        medicamento = Medicamento.objects.get(id=id)
    except Medicamento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Medicamento não encontrado."}, status=404)

    nome = medicamento.nome

    try:
        medicamento.delete()
    except ProtectedError:
        return JsonResponse({
            "ok": False,
            "erro": (
                f"Não é possível eliminar {nome}: existem lotes de stock associados a este "
                "medicamento. Desative-o em vez de eliminar, ou remova primeiro os lotes."
            ),
        }, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Medicamento {nome} eliminado com sucesso.",
    })


# Limiar fixo para "stock crítico" enquanto não existe um valor de stock
# mínimo configurável por medicamento/hospital (fica para quando esse
# model existir — por agora é um número simples, fácil de trocar aqui).
LIMIAR_STOCK_CRITICO = 10


def _contexto_painel_farmacia(request):
    medicamentos = Medicamento.objects.filter(ativo=True).order_by("nome")
    total_controlados = medicamentos.filter(controlado=True).count()

    if request.user.hospital:
        lotes_hospital = Lote.objects.filter(hospital=request.user.hospital, quantidade__gt=0)
    else:
        lotes_hospital = Lote.objects.none()

    total_lotes_ativos = lotes_hospital.count()
    limite_vencimento = timezone.localdate() + timedelta(days=30)
    lotes_a_vencer = lotes_hospital.filter(validade__lte=limite_vencimento).count()

    # Stock total por medicamento (soma de todos os lotes com quantidade > 0)
    # para calcular quantos medicamentos estão esgotados ou em stock crítico.
    stock_por_medicamento = (
        lotes_hospital.values("medicamento_id")
        .annotate(total=Sum("quantidade"))
    )
    stock_map = {item["medicamento_id"]: item["total"] for item in stock_por_medicamento}

    total_esgotados = 0
    total_criticos = 0
    for medicamento in medicamentos:
        total = stock_map.get(medicamento.id, 0)
        if total == 0:
            total_esgotados += 1
        elif total <= LIMIAR_STOCK_CRITICO:
            total_criticos += 1

    return {
        "medicamentos": medicamentos,
        "total_controlados": total_controlados,
        "total_lotes_ativos": total_lotes_ativos,
        "lotes_a_vencer": lotes_a_vencer,
        "total_esgotados": total_esgotados,
        "total_criticos": total_criticos,
        "medicamento_formas": Medicamento.FormaFarmaceutica.choices,
        "medicamento_unidades": Medicamento.UnidadeMedida.choices,
    }


@login_required
@requer_permissao("medicamento.gerir")
def listar_medicamentos_pagina(request):
    return render(request, "farmacia/painel.html", _contexto_painel_farmacia(request))


# =========================================================================
# LOTE (stock — sempre vinculado ao hospital do utilizador)
# =========================================================================

@login_required
@requer_permissao("lote.cadastrar")
def cadastrar_lote(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    if not request.user.hospital:
        return JsonResponse({
            "ok": False,
            "erro": "O seu utilizador não está vinculado a nenhum hospital."
        }, status=400)

    medicamento_id = request.POST.get("lote_medicamento_id", "").strip()
    numero_lote = request.POST.get("lote_numero", "").strip()
    validade_str = request.POST.get("lote_validade", "").strip()
    quantidade_str = request.POST.get("lote_quantidade", "").strip()
    fornecedor = request.POST.get("lote_fornecedor", "").strip()

    erros = []

    medicamento = None
    if not medicamento_id:
        erros.append("Medicamento é obrigatório.")
    else:
        try:
            medicamento = Medicamento.objects.get(id=medicamento_id)
        except Medicamento.DoesNotExist:
            erros.append("Medicamento não encontrado.")

    if not numero_lote:
        erros.append("Número do lote é obrigatório.")

    validade = None
    if not validade_str:
        erros.append("Data de validade é obrigatória.")
    else:
        try:
            validade = datetime.strptime(validade_str, "%Y-%m-%d").date()
            if validade <= date.today():
                erros.append("A data de validade tem de ser futura — não é possível dar entrada de stock já vencido.")
        except ValueError:
            erros.append("Data de validade inválida.")

    quantidade = None
    if not quantidade_str:
        erros.append("Quantidade é obrigatória.")
    else:
        try:
            quantidade = int(quantidade_str)
            if quantidade <= 0:
                erros.append("Quantidade tem de ser maior que zero.")
        except ValueError:
            erros.append("Quantidade inválida.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        lote = Lote.objects.create(
            hospital=request.user.hospital,
            medicamento=medicamento,
            numero_lote=numero_lote,
            validade=validade,
            quantidade=quantidade,
            fornecedor=fornecedor,
        )
        MovimentoStock.objects.create(
            lote=lote,
            tipo=MovimentoStock.Tipo.ENTRADA,
            quantidade=quantidade,
            utilizador=request.user,
            referencia=f"Entrada inicial — lote {lote.numero_lote}",
        )
    except IntegrityError:
        return JsonResponse({
            "ok": False,
            "erro": "Já existe um lote com este número para este medicamento neste hospital.",
        }, status=400)
    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao salvar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Lote {lote.numero_lote} de {medicamento.nome} cadastrado com sucesso.",
        "id": lote.id,
    })


@login_required
@requer_permissao("lote.gerir")
def detalhe_lote(request, id):
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        lote = Lote.objects.get(id=id, hospital=request.user.hospital)
    except Lote.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Lote não encontrado."}, status=404)

    return JsonResponse({
        "ok": True,
        "lote": {
            "id": lote.id,
            "medicamento_id": lote.medicamento_id,
            "medicamento_nome": lote.medicamento.nome,
            "numero_lote": lote.numero_lote,
            "validade": lote.validade.isoformat(),
            "quantidade": lote.quantidade,
            "fornecedor": lote.fornecedor,
            "vencido": lote.vencido,
            "dias_para_vencer": lote.dias_para_vencer,
        }
    })


@login_required
@requer_permissao("lote.gerir")
def atualizar_lote(request, id):
    """
    Só permite corrigir dados administrativos do lote (validade,
    fornecedor). A quantidade NÃO se edita livremente aqui — ela só deve
    mudar através de movimentos de stock (entrada/saída/dispensação),
    para manter o histórico auditável.
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        lote = Lote.objects.get(id=id, hospital=request.user.hospital)
    except Lote.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Lote não encontrado."}, status=404)

    numero_lote = request.POST.get("lote_numero", "").strip()
    validade_str = request.POST.get("lote_validade", "").strip()
    fornecedor = request.POST.get("lote_fornecedor", "").strip()

    erros = []

    if not numero_lote:
        erros.append("Número do lote é obrigatório.")

    validade = None
    if not validade_str:
        erros.append("Data de validade é obrigatória.")
    else:
        try:
            validade = datetime.strptime(validade_str, "%Y-%m-%d").date()
        except ValueError:
            erros.append("Data de validade inválida.")

    if numero_lote and Lote.objects.filter(
        hospital=request.user.hospital,
        medicamento=lote.medicamento,
        numero_lote=numero_lote,
    ).exclude(id=lote.id).exists():
        erros.append("Já existe outro lote com este número para este medicamento neste hospital.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        lote.numero_lote = numero_lote
        lote.validade = validade
        lote.fornecedor = fornecedor
        lote.save()
    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao atualizar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Lote {lote.numero_lote} atualizado com sucesso.",
        "id": lote.id,
    })


@login_required
@requer_permissao("lote.gerir")
def eliminar_lote(request, id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        lote = Lote.objects.get(id=id, hospital=request.user.hospital)
    except Lote.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Lote não encontrado."}, status=404)

    numero_lote = lote.numero_lote
    lote.delete()

    return JsonResponse({
        "ok": True,
        "mensagem": f"Lote {numero_lote} eliminado com sucesso.",
    })


@login_required
@requer_permissao("lote.gerir")
def listar_lotes_por_medicamento(request, medicamento_id):
    """
    Devolve os lotes de um medicamento no hospital do utilizador, já
    ordenados por validade (FEFO) — pensado para alimentar tanto o painel
    de stock como, mais tarde, a etapa de separação por lote na dispensação.
    """
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        medicamento = Medicamento.objects.get(id=medicamento_id)
    except Medicamento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Medicamento não encontrado."}, status=404)

    lotes = Lote.objects.filter(
        hospital=request.user.hospital,
        medicamento=medicamento,
        quantidade__gt=0,
    )

    total_disponivel = lotes.aggregate(total=Sum("quantidade"))["total"] or 0

    return JsonResponse({
        "ok": True,
        "medicamento": medicamento.nome,
        "total_disponivel": total_disponivel,
        "lotes": [
            {
                "id": lote.id,
                "numero_lote": lote.numero_lote,
                "validade": lote.validade.isoformat(),
                "quantidade": lote.quantidade,
                "vencido": lote.vencido,
                "dias_para_vencer": lote.dias_para_vencer,
            }
            for lote in lotes
        ]
    })


@login_required
@requer_permissao("lote.gerir")
def listar_movimentos_stock(request):
    """
    Histórico de movimentos (entradas/saídas/ajustes), filtrável por
    medicamento, tipo e período. Limitado aos 200 mais recentes para não
    sobrecarregar — para históricos maiores, seria caso de paginação.
    """
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    movimentos = MovimentoStock.objects.filter(
        lote__hospital=request.user.hospital
    ).select_related("lote", "lote__medicamento", "utilizador").order_by("-criado_em")

    medicamento_id = request.GET.get("medicamento_id", "").strip()
    tipo = request.GET.get("tipo", "").strip().upper()
    data_inicio = request.GET.get("data_inicio", "").strip()
    data_fim = request.GET.get("data_fim", "").strip()

    if medicamento_id:
        movimentos = movimentos.filter(lote__medicamento_id=medicamento_id)
    if tipo in MovimentoStock.Tipo.values:
        movimentos = movimentos.filter(tipo=tipo)
    if data_inicio:
        movimentos = movimentos.filter(criado_em__date__gte=data_inicio)
    if data_fim:
        movimentos = movimentos.filter(criado_em__date__lte=data_fim)

    movimentos = movimentos[:200]

    return JsonResponse({
        "ok": True,
        "movimentos": [
            {
                "id": m.id,
                "medicamento": m.lote.medicamento.nome,
                "numero_lote": m.lote.numero_lote,
                "tipo": m.tipo,
                "tipo_display": m.get_tipo_display(),
                "quantidade": m.quantidade,
                "utilizador": m.utilizador.nome_completo,
                "referencia": m.referencia,
                "criado_em": m.criado_em.isoformat(),
            }
            for m in movimentos
        ]
    })


@login_required
def modulo_farmacia(request):
    """Entrada do módulo (fragmento carregado pela SPA via data-module='farmacia')."""
    return render(request, "farmacia/painel.html", _contexto_painel_farmacia(request))


# =========================================================================
# FARMÁCIA PROCESSA AS RECEITAS DIGITAIS
# =========================================================================

@login_required
@requer_permissao("prescricao.gerir")
def listar_prescricoes_farmacia(request):
    """Fila da farmácia: receitas digitais ainda por processar (AGUARDANDO)."""
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    prescricoes = PrescricaoMedicamento.objects.filter(
        hospital=request.user.hospital,
        status=PrescricaoMedicamento.Status.AGUARDANDO,
    ).select_related("paciente", "medico").order_by("criado_em")

    resultado = []
    for p in prescricoes:
        documento_bi = p.paciente.documentos.filter(tipo=DocumentoPaciente.TipoDocumento.BI).first()
        resultado.append({
            "id": p.id,
            "paciente": p.paciente.nome_completo,
            "paciente_codigo": p.paciente.codigo,
            "bi": documento_bi.numero if documento_bi else "",
            "medico": p.medico.nome_completo,
            "total_itens": p.itens.count(),
            "criado_em": p.criado_em.isoformat(),
        })

    return JsonResponse({"ok": True, "prescricoes": resultado})


@login_required
@requer_permissao("prescricao.gerir")
def detalhe_prescricao_farmacia(request, id):
    """
    Detalhe da receita para a farmácia — cada item já vem com o stock
    disponível verificado, para o farmacêutico ver logo se pode dispensar
    sem ter de ir confirmar manualmente medicamento a medicamento.
    """
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        prescricao = PrescricaoMedicamento.objects.select_related("paciente", "medico").get(
            id=id, hospital=request.user.hospital
        )
    except PrescricaoMedicamento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Prescrição não encontrada."}, status=404)

    itens = []
    for item in prescricao.itens.select_related("medicamento").all():
        stock_disponivel = Lote.objects.filter(
            hospital=request.user.hospital,
            medicamento=item.medicamento,
            quantidade__gt=0,
        ).aggregate(total=Sum("quantidade"))["total"] or 0

        itens.append({
            "id": item.id,
            "medicamento": item.medicamento.nome,
            "dosagem": item.dosagem,
            "via_administracao": item.get_via_administracao_display(),
            "frequencia": item.frequencia,
            "duracao_dias": item.duracao_dias,
            "quantidade": item.quantidade,
            "stock_disponivel": stock_disponivel,
            "stock_suficiente": stock_disponivel >= item.quantidade,
        })

    return JsonResponse({
        "ok": True,
        "prescricao": {
            "id": prescricao.id,
            "paciente": prescricao.paciente.nome_completo,
            "paciente_codigo": prescricao.paciente.codigo,
            "medico": prescricao.medico.nome_completo,
            "status": prescricao.status,
            "status_display": prescricao.get_status_display(),
            "observacoes": prescricao.observacoes,
            "criado_em": prescricao.criado_em.isoformat(),
            "itens": itens,
            "pode_dispensar": bool(itens) and all(i["stock_suficiente"] for i in itens),
        }
    })


@login_required
@requer_permissao("dispensacao.cadastrar")
@transaction.atomic
def dispensar_prescricao(request, id):
    """
    Dispensa TODOS os itens da receita de uma vez, tudo-ou-nada: se
    faltar stock nalgum item, nada é dispensado. Segue exactamente o
    mesmo padrão FEFO + select_for_update da dispensação manual, só que
    aplicado a vários medicamentos (um por ItemPrescricao) na mesma
    transacção.
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        prescricao = PrescricaoMedicamento.objects.select_related("paciente").get(
            id=id, hospital=request.user.hospital
        )
    except PrescricaoMedicamento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Prescrição não encontrada."}, status=404)

    if prescricao.status != PrescricaoMedicamento.Status.AGUARDANDO:
        return JsonResponse({"ok": False, "erro": "Esta prescrição já foi processada."}, status=400)

    itens = list(prescricao.itens.select_related("medicamento").all())
    if not itens:
        return JsonResponse({"ok": False, "erro": "Esta receita não tem nenhum medicamento."}, status=400)

    faltas = []
    lotes_por_item = {}

    # Primeiro valida tudo, sem mexer em nada — só avança para a baixa
    # se TODOS os itens tiverem stock suficiente.
    for item in itens:
        lotes = list(
            Lote.objects.select_for_update()
            .filter(hospital=request.user.hospital, medicamento=item.medicamento, quantidade__gt=0)
            .order_by("validade")
        )
        total = sum(l.quantidade for l in lotes)
        if total < item.quantidade:
            faltas.append(f"{item.medicamento.nome} (disponível {total}, necessário {item.quantidade})")
        lotes_por_item[item.id] = lotes

    if faltas:
        return JsonResponse({
            "ok": False,
            "erro": "Stock insuficiente para: " + "; ".join(faltas) + ". Nada foi dispensado.",
        }, status=400)

    for item in itens:
        dispensacao = Dispensacao.objects.create(
            hospital=request.user.hospital,
            paciente=prescricao.paciente,
            medicamento=item.medicamento,
            quantidade=item.quantidade,
            farmaceutico=request.user,
            observacao=f"Prescrição #{prescricao.id}",
        )

        restante = item.quantidade
        for lote in lotes_por_item[item.id]:
            if restante <= 0:
                break
            retirar = min(lote.quantidade, restante)
            lote.quantidade -= retirar
            lote.save(update_fields=["quantidade"])

            ItemDispensacao.objects.create(dispensacao=dispensacao, lote=lote, quantidade=retirar)
            MovimentoStock.objects.create(
                lote=lote,
                tipo=MovimentoStock.Tipo.SAIDA,
                quantidade=retirar,
                utilizador=request.user,
                referencia=f"Dispensação de Prescrição #{prescricao.id} — {prescricao.paciente.nome_completo}",
            )
            restante -= retirar

    prescricao.status = PrescricaoMedicamento.Status.DISPENSADO
    prescricao.save(update_fields=["status"])

    return JsonResponse({
        "ok": True,
        "mensagem": f"Prescrição de {prescricao.paciente.nome_completo} dispensada com sucesso.",
    })


@login_required
@requer_permissao("dispensacao.cadastrar")
def marcar_pendencia_prescricao(request, id):
    """
    Regista que a receita ficou em pendência (ex.: falta de stock que não
    se resolve na hora) — sai da fila de "por processar" sem ser
    dispensada, com o motivo anotado nas observações para auditoria.
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        prescricao = PrescricaoMedicamento.objects.get(id=id, hospital=request.user.hospital)
    except PrescricaoMedicamento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Prescrição não encontrada."}, status=404)

    motivo = request.POST.get("motivo", "").strip()
    prescricao.status = PrescricaoMedicamento.Status.PENDENCIA
    if motivo:
        prescricao.observacoes = (prescricao.observacoes + f"\n[Pendência] {motivo}").strip()
    prescricao.save(update_fields=["status", "observacoes"])

    return JsonResponse({"ok": True, "mensagem": "Prescrição marcada como pendência."})


# =========================================================================
# REQUISIÇÕES INTERNAS (sector → Farmácia, sem paciente/prescrição)
# =========================================================================

@login_required
@requer_permissao("requisicao_interna.cadastrar")
def cadastrar_requisicao_interna(request):
    """
    Qualquer sector do hospital (enfermaria, internamento, etc.) pode
    pedir medicamentos directamente à Farmácia. Mesmo padrão de
    cadastrar_prescricao: cabeçalho + itens via arrays paralelos.
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    if not request.user.hospital:
        return JsonResponse({"ok": False, "erro": "O seu utilizador não está vinculado a nenhum hospital."}, status=400)

    origem = request.POST.get("requisicao_origem", "").strip()
    observacoes = request.POST.get("requisicao_observacoes", "").strip()

    medicamento_ids = request.POST.getlist("item_medicamento_id[]")
    quantidades = request.POST.getlist("item_quantidade[]")

    erros = []
    if not origem:
        erros.append("Sector de origem é obrigatório.")
    if not medicamento_ids:
        erros.append("Adicione pelo menos um medicamento à requisição.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    requisicao = RequisicaoInterna.objects.create(
        hospital=request.user.hospital,
        origem=origem,
        solicitante=request.user,
        observacoes=observacoes,
        status=RequisicaoInterna.Status.PENDENTE,
    )

    itens_criados = 0
    for i, medicamento_id in enumerate(medicamento_ids):
        try:
            medicamento = Medicamento.objects.get(id=medicamento_id)
            quantidade = int(quantidades[i])
            if quantidade <= 0:
                continue
        except (Medicamento.DoesNotExist, ValueError, IndexError):
            continue

        ItemRequisicaoInterna.objects.create(
            requisicao=requisicao,
            medicamento=medicamento,
            quantidade_solicitada=quantidade,
        )
        itens_criados += 1

    if itens_criados == 0:
        requisicao.delete()
        return JsonResponse({"ok": False, "erro": "Nenhum item válido foi enviado."}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Requisição de {requisicao.origem} enviada à Farmácia.",
        "requisicao_id": requisicao.id,
    })


@login_required
@requer_permissao("requisicao_interna.gerir")
def listar_requisicoes_internas(request):
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    requisicoes = RequisicaoInterna.objects.filter(
        hospital=request.user.hospital,
        status=RequisicaoInterna.Status.PENDENTE,
    ).select_related("solicitante").order_by("criado_em")

    return JsonResponse({
        "ok": True,
        "requisicoes": [
            {
                "id": r.id,
                "origem": r.origem,
                "solicitante": r.solicitante.nome_completo,
                "total_itens": r.itens.count(),
                "criado_em": r.criado_em.isoformat(),
            }
            for r in requisicoes
        ]
    })


@login_required
@requer_permissao("requisicao_interna.gerir")
def detalhe_requisicao_interna(request, id):
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        requisicao = RequisicaoInterna.objects.select_related("solicitante").get(
            id=id, hospital=request.user.hospital
        )
    except RequisicaoInterna.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Requisição não encontrada."}, status=404)

    itens = []
    for item in requisicao.itens.select_related("medicamento").all():
        stock_disponivel = Lote.objects.filter(
            hospital=request.user.hospital,
            medicamento=item.medicamento,
            quantidade__gt=0,
        ).aggregate(total=Sum("quantidade"))["total"] or 0

        itens.append({
            "id": item.id,
            "medicamento": item.medicamento.nome,
            "quantidade_solicitada": item.quantidade_solicitada,
            "stock_disponivel": stock_disponivel,
            "stock_suficiente": stock_disponivel >= item.quantidade_solicitada,
        })

    return JsonResponse({
        "ok": True,
        "requisicao": {
            "id": requisicao.id,
            "origem": requisicao.origem,
            "solicitante": requisicao.solicitante.nome_completo,
            "status": requisicao.status,
            "status_display": requisicao.get_status_display(),
            "observacoes": requisicao.observacoes,
            "criado_em": requisicao.criado_em.isoformat(),
            "itens": itens,
            "pode_entregar": bool(itens) and all(i["stock_suficiente"] for i in itens),
        }
    })


@login_required
@requer_permissao("requisicao_interna.gerir")
@transaction.atomic
def entregar_requisicao_interna(request, id):
    """
    Entrega TODOS os itens de uma vez, tudo-ou-nada — mesmo padrão de
    dispensar_prescricao, mas sem paciente: a saída de stock fica
    registada em nome do sector de origem (referência do MovimentoStock).
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        requisicao = RequisicaoInterna.objects.get(id=id, hospital=request.user.hospital)
    except RequisicaoInterna.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Requisição não encontrada."}, status=404)

    if requisicao.status != RequisicaoInterna.Status.PENDENTE:
        return JsonResponse({"ok": False, "erro": "Esta requisição já foi processada."}, status=400)

    itens = list(requisicao.itens.select_related("medicamento").all())
    if not itens:
        return JsonResponse({"ok": False, "erro": "Esta requisição não tem nenhum item."}, status=400)

    faltas = []
    lotes_por_item = {}

    for item in itens:
        lotes = list(
            Lote.objects.select_for_update()
            .filter(hospital=request.user.hospital, medicamento=item.medicamento, quantidade__gt=0)
            .order_by("validade")
        )
        total = sum(l.quantidade for l in lotes)
        if total < item.quantidade_solicitada:
            faltas.append(f"{item.medicamento.nome} (disponível {total}, necessário {item.quantidade_solicitada})")
        lotes_por_item[item.id] = lotes

    if faltas:
        return JsonResponse({
            "ok": False,
            "erro": "Stock insuficiente para: " + "; ".join(faltas) + ". Nada foi entregue.",
        }, status=400)

    for item in itens:
        restante = item.quantidade_solicitada
        for lote in lotes_por_item[item.id]:
            if restante <= 0:
                break
            retirar = min(lote.quantidade, restante)
            lote.quantidade -= retirar
            lote.save(update_fields=["quantidade"])

            MovimentoStock.objects.create(
                lote=lote,
                tipo=MovimentoStock.Tipo.SAIDA,
                quantidade=retirar,
                utilizador=request.user,
                referencia=f"Requisição Interna #{requisicao.id} — {requisicao.origem}",
            )
            restante -= retirar

        item.quantidade_entregue = item.quantidade_solicitada
        item.save(update_fields=["quantidade_entregue"])

    requisicao.status = RequisicaoInterna.Status.ENTREGUE
    requisicao.save(update_fields=["status"])

    return JsonResponse({
        "ok": True,
        "mensagem": f"Requisição de {requisicao.origem} entregue com sucesso.",
    })


@login_required
@requer_permissao("requisicao_interna.gerir")
def rejeitar_requisicao_interna(request, id):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        requisicao = RequisicaoInterna.objects.get(id=id, hospital=request.user.hospital)
    except RequisicaoInterna.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Requisição não encontrada."}, status=404)

    if requisicao.status != RequisicaoInterna.Status.PENDENTE:
        return JsonResponse({"ok": False, "erro": "Esta requisição já foi processada."}, status=400)

    motivo = request.POST.get("motivo", "").strip()
    requisicao.status = RequisicaoInterna.Status.REJEITADA
    if motivo:
        requisicao.observacoes = (requisicao.observacoes + f"\n[Rejeitada] {motivo}").strip()
    requisicao.save(update_fields=["status", "observacoes"])

    return JsonResponse({"ok": True, "mensagem": "Requisição rejeitada."})


# =========================================================================
# RELATÓRIOS PDF
# =========================================================================

@login_required
@requer_permissao("lote.gerir")
def relatorio_stock_pdf(request):
    """Relatório de stock actual — um medicamento por linha, com estado (Ok/Crítico/Esgotado)."""

    limiar_critico = 10

    medicamentos = Medicamento.objects.filter(ativo=True).order_by("nome")
    lotes_hospital = Lote.objects.filter(hospital=request.user.hospital, quantidade__gt=0)

    stock_map = {}
    for item in lotes_hospital.values("medicamento_id").annotate(total=Sum("quantidade")):
        stock_map[item["medicamento_id"]] = item["total"]

    styles = getSampleStyleSheet()

    buffer, doc = novo_documento_pdf()
    elementos = cabecalho_relatorio(
        "Relatório de Stock — Farmácia",
        request,
        f"Total: {medicamentos.count()} medicamento(s)",
    )

    cabecalho_tabela = ["Nome", "Forma", "Concentração", "Stock Total", "Lotes Activos", "Estado"]
    dados = [cabecalho_tabela]

    for m in medicamentos:
        total = stock_map.get(m.id, 0)
        total_lotes = lotes_hospital.filter(medicamento=m).count()

        if total == 0:
            estado = "Esgotado"
        elif total <= limiar_critico:
            estado = "Crítico"
        else:
            estado = "Ok"

        dados.append([
            Paragraph(m.nome, styles["Normal"]),
            m.get_forma_farmaceutica_display() if hasattr(m, "get_forma_farmaceutica_display") else "—",
            m.concentracao or "—",
            str(total),
            str(total_lotes),
            estado,
        ])

    if len(dados) == 1:
        elementos.append(Paragraph("Nenhum medicamento cadastrado.", styles["Normal"]))
    else:
        tabela = Table(dados, repeatRows=1, colWidths=[55 * 3, 25 * 3, 25 * 3, 22 * 3, 22 * 3, 20 * 3])
        tabela.setStyle(estilo_tabela_padrao())
        elementos.append(tabela)

    return finalizar_resposta_pdf(buffer, doc, elementos, "relatorio_stock_farmacia")


@login_required
@requer_permissao("lote.gerir")
def relatorio_movimentos_pdf(request):
    """
    Relatório de movimentos de stock — mesmos filtros do modal
    "Histórico" (medicamento/tipo/período), agora exportável em PDF.
    """
    movimentos = MovimentoStock.objects.filter(
        lote__hospital=request.user.hospital
    ).select_related("lote", "lote__medicamento", "utilizador").order_by("-criado_em")

    medicamento_id = request.GET.get("medicamento_id", "").strip()
    tipo = request.GET.get("tipo", "").strip().upper()
    data_inicio = request.GET.get("data_inicio", "").strip()
    data_fim = request.GET.get("data_fim", "").strip()

    if medicamento_id:
        movimentos = movimentos.filter(lote__medicamento_id=medicamento_id)
    if tipo in MovimentoStock.Tipo.values:
        movimentos = movimentos.filter(tipo=tipo)
    if data_inicio:
        movimentos = movimentos.filter(criado_em__date__gte=data_inicio)
    if data_fim:
        movimentos = movimentos.filter(criado_em__date__lte=data_fim)

    movimentos = movimentos[:500]

    styles = getSampleStyleSheet()

    buffer, doc = novo_documento_pdf()
    elementos = cabecalho_relatorio(
        "Relatório de Movimentos — Farmácia",
        request,
        f"Total: {len(movimentos)} movimento(s)",
    )

    cabecalho_tabela = ["Data", "Medicamento", "Lote", "Tipo", "Qtd", "Utilizador", "Referência"]
    dados = [cabecalho_tabela]

    for m in movimentos:
        dados.append([
            timezone.localtime(m.criado_em).strftime("%d/%m/%Y %H:%M"),
            Paragraph(m.lote.medicamento.nome, styles["Normal"]),
            m.lote.numero_lote,
            m.get_tipo_display(),
            str(m.quantidade),
            Paragraph(m.utilizador.nome_completo, styles["Normal"]),
            Paragraph(m.referencia or "—", styles["Normal"]),
        ])

    if len(dados) == 1:
        elementos.append(Paragraph("Nenhum movimento encontrado para os filtros aplicados.", styles["Normal"]))
    else:
        tabela = Table(dados, repeatRows=1, colWidths=[26 * 3, 30 * 3, 16 * 3, 14 * 3, 8 * 3, 26 * 3, 30 * 3])
        tabela.setStyle(estilo_tabela_padrao())
        elementos.append(tabela)

    return finalizar_resposta_pdf(buffer, doc, elementos, "relatorio_movimentos_farmacia")