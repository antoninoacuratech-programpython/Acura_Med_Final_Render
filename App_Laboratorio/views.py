from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from App_Usuarios.permissoes import requer_permissao

from .tipo_exame import TipoExame


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