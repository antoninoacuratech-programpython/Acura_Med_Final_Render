from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse

from App_Usuarios.permissoes import requer_permissao
from App_Farmacia.medicamento import Medicamento
from App_Atendimentos.atendimento import Atendimento

from .prescricao_medicamento import PrescricaoMedicamento
from .item_prescricao import ItemPrescricao


@login_required
@requer_permissao("prescricao.cadastrar")
@transaction.atomic
def cadastrar_prescricao(request):
    """
    Cria a receita (cabeçalho) e todos os seus itens numa só chamada. O
    frontend deve enviar os campos de cada linha como arrays paralelos:
    item_medicamento_id[], item_dosagem[], item_via[], item_frequencia[],
    item_duracao_dias[], item_quantidade[] — a linha N de cada array
    pertence ao mesmo medicamento.
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    if not request.user.hospital:
        return JsonResponse({
            "ok": False,
            "erro": "O seu utilizador não está vinculado a nenhum hospital."
        }, status=400)

    atendimento_id = request.POST.get("prescricao_atendimento_id", "").strip()
    observacoes = request.POST.get("prescricao_observacoes", "").strip()

    medicamento_ids = request.POST.getlist("item_medicamento_id[]")
    dosagens = request.POST.getlist("item_dosagem[]")
    vias = request.POST.getlist("item_via[]")
    frequencias = request.POST.getlist("item_frequencia[]")
    duracoes = request.POST.getlist("item_duracao_dias[]")
    quantidades = request.POST.getlist("item_quantidade[]")

    erros = []

    atendimento = None
    if not atendimento_id:
        erros.append("Atendimento é obrigatório.")
    else:
        try:
            atendimento = Atendimento.objects.get(id=atendimento_id, hospital=request.user.hospital)
        except Atendimento.DoesNotExist:
            erros.append("Atendimento não encontrado.")

    if not medicamento_ids:
        erros.append("Adicione pelo menos um medicamento à prescrição.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    prescricao = PrescricaoMedicamento.objects.create(
        hospital=request.user.hospital,
        atendimento=atendimento,
        paciente=atendimento.paciente,
        medico=request.user,
        observacoes=observacoes,
        status=PrescricaoMedicamento.Status.AGUARDANDO,
    )

    itens_erros = []
    itens_criados = 0

    for i, medicamento_id in enumerate(medicamento_ids):
        try:
            medicamento = Medicamento.objects.get(id=medicamento_id)
        except (Medicamento.DoesNotExist, ValueError):
            itens_erros.append(f"Medicamento inválido na linha {i + 1}.")
            continue

        try:
            quantidade = int(quantidades[i])
            if quantidade <= 0:
                raise ValueError
        except (ValueError, IndexError):
            itens_erros.append(f"Quantidade inválida na linha {i + 1}.")
            continue

        duracao_dias = None
        if i < len(duracoes) and duracoes[i].strip():
            try:
                duracao_dias = int(duracoes[i])
            except ValueError:
                itens_erros.append(f"Duração inválida na linha {i + 1}.")
                continue

        via = (vias[i] if i < len(vias) else "").strip().upper()
        if via not in ItemPrescricao.ViaAdministracao.values:
            via = ItemPrescricao.ViaAdministracao.ORAL

        ItemPrescricao.objects.create(
            prescricao=prescricao,
            medicamento=medicamento,
            dosagem=dosagens[i] if i < len(dosagens) else "",
            via_administracao=via,
            frequencia=frequencias[i] if i < len(frequencias) else "",
            duracao_dias=duracao_dias,
            quantidade=quantidade,
        )
        itens_criados += 1

    if itens_erros or itens_criados == 0:
        transaction.set_rollback(True)
        return JsonResponse({
            "ok": False,
            "erro": " ".join(itens_erros) if itens_erros else "Nenhum medicamento válido foi enviado.",
        }, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Prescrição criada para {prescricao.paciente.nome_completo} e enviada à farmácia.",
        "prescricao_id": prescricao.id,
    })


@login_required
@requer_permissao("prescricao.gerir")
def detalhe_prescricao(request, id):
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        prescricao = PrescricaoMedicamento.objects.get(id=id, hospital=request.user.hospital)
    except PrescricaoMedicamento.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Prescrição não encontrada."}, status=404)

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
            "itens": [
                {
                    "id": item.id,
                    "medicamento_id": item.medicamento_id,
                    "medicamento": item.medicamento.nome,
                    "dosagem": item.dosagem,
                    "via_administracao": item.get_via_administracao_display(),
                    "frequencia": item.frequencia,
                    "duracao_dias": item.duracao_dias,
                    "quantidade": item.quantidade,
                    "observacoes": item.observacoes,
                }
                for item in prescricao.itens.all()
            ],
        }
    })


@login_required
@requer_permissao("prescricao.gerir")
def listar_prescricoes_paciente(request, paciente_codigo):
    """Histórico de receitas de um paciente — útil no prontuário."""
    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    prescricoes = PrescricaoMedicamento.objects.filter(
        hospital=request.user.hospital,
        paciente__codigo=paciente_codigo,
    ).order_by("-criado_em")

    return JsonResponse({
        "ok": True,
        "prescricoes": [
            {
                "id": p.id,
                "status": p.status,
                "status_display": p.get_status_display(),
                "criado_em": p.criado_em.isoformat(),
                "total_itens": p.itens.count(),
            }
            for p in prescricoes
        ]
    })