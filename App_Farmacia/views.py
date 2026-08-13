from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.db.models import ProtectedError, Sum
from django.http import JsonResponse
from django.shortcuts import render

from App_Usuarios.permissoes import requer_permissao

from .medicamento import Medicamento
from .lote import Lote


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


@login_required
@requer_permissao("medicamento.gerir")
def listar_medicamentos_pagina(request):
    medicamentos = Medicamento.objects.all().order_by("nome")

    return render(
        request,
        "farmacia/medicamentos.html",
        {
            "medicamentos": medicamentos,
        }
    )


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
    preco_custo_str = request.POST.get("lote_preco_custo", "").strip()

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

    preco_custo_unitario = None
    if preco_custo_str:
        try:
            preco_custo_unitario = float(preco_custo_str)
        except ValueError:
            erros.append("Preço de custo inválido.")

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
            preco_custo_unitario=preco_custo_unitario,
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
            "preco_custo_unitario": str(lote.preco_custo_unitario) if lote.preco_custo_unitario is not None else "",
            "vencido": lote.vencido,
            "dias_para_vencer": lote.dias_para_vencer,
        }
    })


@login_required
@requer_permissao("lote.gerir")
def atualizar_lote(request, id):
    """
    Só permite corrigir dados administrativos do lote (validade, fornecedor,
    preço). A quantidade NÃO se edita livremente aqui — ela só deve mudar
    através de movimentos de stock (entrada/saída/dispensação), para manter
    o histórico auditável. Se precisares de corrigir uma quantidade errada,
    isso deverá ser um movimento de ajuste, não um update directo.
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
    preco_custo_str = request.POST.get("lote_preco_custo", "").strip()

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

    preco_custo_unitario = lote.preco_custo_unitario
    if preco_custo_str:
        try:
            preco_custo_unitario = float(preco_custo_str)
        except ValueError:
            erros.append("Preço de custo inválido.")

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
        lote.preco_custo_unitario = preco_custo_unitario
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
def modulo_farmacia(request):
    """Entrada do módulo (fragmento carregado pela SPA via data-module='farmacia')."""

    medicamentos = Medicamento.objects.filter(ativo=True).order_by("nome")

    return render(
        request,
        "farmacia/painel.html",
        {
            "medicamentos": medicamentos,
        }
    )