from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError, Sum
from django.http import JsonResponse
from django.shortcuts import render

from App_Usuarios.permissoes import requer_permissao

from .nave import Nave
from .quarto import Quarto


def _contexto_painel_internamento(request):
    naves = Nave.objects.filter(hospital=request.user.hospital, ativa=True).order_by("nome") if request.user.hospital else Nave.objects.none()
    quartos = Quarto.objects.filter(nave__hospital=request.user.hospital, ativo=True).select_related("nave").order_by("nave__nome", "numero") if request.user.hospital else Quarto.objects.none()

    total_capacidade = quartos.aggregate(total=Sum("capacidade"))["total"] or 0
    total_ocupados = sum(q.ocupados for q in quartos)

    return {
        "naves": naves,
        "quartos": quartos,
        "total_naves": naves.count(),
        "total_quartos": quartos.count(),
        "total_capacidade": total_capacidade,
        "total_vagas": max(total_capacidade - total_ocupados, 0),
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
