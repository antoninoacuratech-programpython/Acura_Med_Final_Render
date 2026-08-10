from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.contrib.staticfiles import finders

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from io import BytesIO

from .permissoes import requer_permissao
from .paciente import Paciente
from .endereco import EnderecoPaciente
from .documento import DocumentoPaciente
from .contacto import ContactoPaciente
from .responsavel import ResponsavelPaciente


@login_required
@requer_permissao("paciente.cadastrar")
def cadastrar_paciente(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    if not request.user.hospital:
        return JsonResponse({
            "ok": False,
            "erro": "O seu utilizador não está vinculado a nenhum hospital."
        }, status=400)

    # --- Dados pessoais ---
    primeiro_nome = request.POST.get("paciente_primeiro_nome", "").strip()
    outros_nomes = request.POST.get("paciente_outros_nomes", "").strip()
    ultimo_nome = request.POST.get("paciente_ultimo_nome", "").strip()
    nome_social = request.POST.get("paciente_nome_social", "").strip()
    data_nascimento = request.POST.get("paciente_data_nascimento", "").strip()
    sexo = request.POST.get("paciente_sexo", "").strip().upper()
    estado_civil = request.POST.get("paciente_estado_civil", "").strip().upper()
    nacionalidade = request.POST.get("paciente_nacionalidade", "").strip() or "Angolana"
    profissao = request.POST.get("paciente_profissao", "").strip()
    bi = request.POST.get("paciente_bi", "").strip()
    contacto = request.POST.get("paciente_contacto", "").strip()
    fotografia = request.FILES.get("paciente_fotografia")

    # --- Endereço ---
    provincia = request.POST.get("paciente_provincia", "").strip()
    municipio = request.POST.get("paciente_municipio", "").strip()
    comuna = request.POST.get("paciente_comuna", "").strip()
    bairro = request.POST.get("paciente_bairro", "").strip()
    rua = request.POST.get("paciente_rua", "").strip()
    numero_casa = request.POST.get("paciente_numero_casa", "").strip()
    referencia = request.POST.get("paciente_referencia", "").strip()

    # --- Responsável ---
    responsavel_nome = request.POST.get("responsavel_nome", "").strip()
    responsavel_parentesco = request.POST.get("responsavel_parentesco", "").strip().upper()
    responsavel_contacto = request.POST.get("responsavel_contacto", "").strip()
    responsavel_endereco = request.POST.get("responsavel_endereco", "").strip()

    # NOTA: o campo "entidadeSelecionada" (autocomplete de Empresa/Seguradora/
    # Médico/Colaborador) é enviado pelo formulário mas ainda não é lido nem
    # persistido aqui, porque não existe model/relação definida para isso.
    # Quando decidires o model (ex.: EntidadeVinculadaPaciente), lê
    # request.POST.get("entidadeSelecionada") e associa ao paciente aqui.

    erros = []
    if not primeiro_nome:
        erros.append("Primeiro nome é obrigatório.")
    if not ultimo_nome:
        erros.append("Apelido é obrigatório.")
    if not data_nascimento:
        erros.append("Data de nascimento é obrigatória.")
    if sexo not in ("M", "F"):
        erros.append("Género inválido.")
    if estado_civil and estado_civil not in Paciente.EstadoCivil.values:
        erros.append("Estado civil inválido.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        with transaction.atomic():
            paciente = Paciente.objects.create(
                hospital=request.user.hospital,
                primeiro_nome=primeiro_nome,
                outros_nomes=outros_nomes,
                ultimo_nome=ultimo_nome,
                nome_social=nome_social,
                sexo=sexo,
                data_nascimento=data_nascimento,
                estado_civil=estado_civil,
                nacionalidade=nacionalidade,
                profissao=profissao,
                fotografia=fotografia,
            )

            if provincia or municipio or comuna or bairro or rua or numero_casa or referencia:
                EnderecoPaciente.objects.create(
                    paciente=paciente,
                    provincia=provincia,
                    municipio=municipio,
                    comuna=comuna,
                    bairro=bairro,
                    rua=rua,
                    numero_casa=numero_casa,
                    referencia=referencia,
                )

            if bi:
                DocumentoPaciente.objects.create(
                    paciente=paciente,
                    tipo=DocumentoPaciente.TipoDocumento.BI,
                    numero=bi,
                    principal=True,
                )

            if contacto:
                ContactoPaciente.objects.create(
                    paciente=paciente,
                    tipo=ContactoPaciente.TipoContacto.TELEFONE,
                    contacto=contacto,
                    principal=True,
                )

            if responsavel_nome:
                ResponsavelPaciente.objects.create(
                    paciente=paciente,
                    nome=responsavel_nome,
                    parentesco=responsavel_parentesco or ResponsavelPaciente.Parentesco.OUTRO,
                    telefone=responsavel_contacto,
                    endereco=responsavel_endereco,
                )

    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao salvar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Paciente {paciente.nome_completo} cadastrado com sucesso.",
        "codigo": paciente.codigo,
    })


@login_required
@requer_permissao("paciente.cadastrar")
def detalhe_paciente(request, codigo):
    """Devolve os dados de um paciente em JSON, para pré-preencher o modal em modo edição."""

    if request.method != "GET":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        paciente = Paciente.objects.get(codigo=codigo, hospital=request.user.hospital)
    except Paciente.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Paciente não encontrado."}, status=404)

    endereco = getattr(paciente, "endereco", None)
    documento_bi = paciente.documentos.filter(tipo=DocumentoPaciente.TipoDocumento.BI).first()

    contacto = paciente.contactos.filter(principal=True).first()
    responsavel = paciente.responsaveis.first()

    return JsonResponse({
        "ok": True,
        "paciente": {
            "codigo": paciente.codigo,
            "primeiro_nome": paciente.primeiro_nome,
            "outros_nomes": paciente.outros_nomes,
            "ultimo_nome": paciente.ultimo_nome,
            "nome_social": paciente.nome_social,
            "data_nascimento": paciente.data_nascimento.isoformat() if paciente.data_nascimento else "",
            "sexo": paciente.sexo,
            "estado_civil": paciente.estado_civil,
            "nacionalidade": paciente.nacionalidade,
            "profissao": paciente.profissao,
            "fotografia_url": paciente.fotografia.url if paciente.fotografia else "",
            "bi": documento_bi.numero if documento_bi else "",
            "contacto": contacto.contacto if contacto else "",
            "provincia": endereco.provincia if endereco else "",
            "municipio": endereco.municipio if endereco else "",
            "comuna": endereco.comuna if endereco else "",
            "bairro": endereco.bairro if endereco else "",
            "rua": endereco.rua if endereco else "",
            "numero_casa": endereco.numero_casa if endereco else "",
            "referencia": endereco.referencia if endereco else "",
            "responsavel_nome": responsavel.nome if responsavel else "",
            "responsavel_parentesco": responsavel.parentesco if responsavel else "",
            "responsavel_contacto": responsavel.telefone if responsavel else "",
            "responsavel_endereco": responsavel.endereco if responsavel else "",
        }
    })


@login_required
@requer_permissao("paciente.cadastrar")
def atualizar_paciente(request, codigo):
    """Atualiza um paciente existente (mesmos campos do cadastro)."""

    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        paciente = Paciente.objects.get(codigo=codigo, hospital=request.user.hospital)
    except Paciente.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Paciente não encontrado."}, status=404)

    primeiro_nome = request.POST.get("paciente_primeiro_nome", "").strip()
    outros_nomes = request.POST.get("paciente_outros_nomes", "").strip()
    ultimo_nome = request.POST.get("paciente_ultimo_nome", "").strip()
    nome_social = request.POST.get("paciente_nome_social", "").strip()
    data_nascimento = request.POST.get("paciente_data_nascimento", "").strip()
    sexo = request.POST.get("paciente_sexo", "").strip().upper()
    estado_civil = request.POST.get("paciente_estado_civil", "").strip().upper()
    nacionalidade = request.POST.get("paciente_nacionalidade", "").strip() or "Angolana"
    profissao = request.POST.get("paciente_profissao", "").strip()
    bi = request.POST.get("paciente_bi", "").strip()
    contacto = request.POST.get("paciente_contacto", "").strip()
    # Input type="file" nunca vem pré-preenchido no browser por razões de
    # segurança — se o campo vier vazio, mantém-se a fotografia já guardada.
    fotografia = request.FILES.get("paciente_fotografia")

    provincia = request.POST.get("paciente_provincia", "").strip()
    municipio = request.POST.get("paciente_municipio", "").strip()
    comuna = request.POST.get("paciente_comuna", "").strip()
    bairro = request.POST.get("paciente_bairro", "").strip()
    rua = request.POST.get("paciente_rua", "").strip()
    numero_casa = request.POST.get("paciente_numero_casa", "").strip()
    referencia = request.POST.get("paciente_referencia", "").strip()

    responsavel_nome = request.POST.get("responsavel_nome", "").strip()
    responsavel_parentesco = request.POST.get("responsavel_parentesco", "").strip().upper()
    responsavel_contacto = request.POST.get("responsavel_contacto", "").strip()
    responsavel_endereco = request.POST.get("responsavel_endereco", "").strip()

    erros = []
    if not primeiro_nome:
        erros.append("Primeiro nome é obrigatório.")
    if not ultimo_nome:
        erros.append("Apelido é obrigatório.")
    if not data_nascimento:
        erros.append("Data de nascimento é obrigatória.")
    if sexo not in ("M", "F"):
        erros.append("Género inválido.")
    if estado_civil and estado_civil not in Paciente.EstadoCivil.values:
        erros.append("Estado civil inválido.")

    if erros:
        return JsonResponse({"ok": False, "erro": " ".join(erros)}, status=400)

    try:
        with transaction.atomic():
            paciente.primeiro_nome = primeiro_nome
            paciente.outros_nomes = outros_nomes
            paciente.ultimo_nome = ultimo_nome
            paciente.nome_social = nome_social
            paciente.sexo = sexo
            paciente.data_nascimento = data_nascimento
            paciente.estado_civil = estado_civil
            paciente.nacionalidade = nacionalidade
            paciente.profissao = profissao
            if fotografia:
                paciente.fotografia = fotografia
            paciente.save()

            if provincia or municipio or comuna or bairro or rua or numero_casa or referencia:
                EnderecoPaciente.objects.update_or_create(
                    paciente=paciente,
                    defaults={
                        "provincia": provincia,
                        "municipio": municipio,
                        "comuna": comuna,
                        "bairro": bairro,
                        "rua": rua,
                        "numero_casa": numero_casa,
                        "referencia": referencia,
                    },
                )

            if bi:
                DocumentoPaciente.objects.update_or_create(
                    paciente=paciente,
                    tipo=DocumentoPaciente.TipoDocumento.BI,
                    defaults={"numero": bi, "principal": True},
                )

            if contacto:
                ContactoPaciente.objects.update_or_create(
                    paciente=paciente,
                    tipo=ContactoPaciente.TipoContacto.TELEFONE,
                    principal=True,
                    defaults={"contacto": contacto},
                )

            if responsavel_nome:
                ResponsavelPaciente.objects.update_or_create(
                    paciente=paciente,
                    defaults={
                        "nome": responsavel_nome,
                        "parentesco": responsavel_parentesco or ResponsavelPaciente.Parentesco.OUTRO,
                        "telefone": responsavel_contacto,
                        "endereco": responsavel_endereco,
                    },
                )

    except Exception as e:
        return JsonResponse({"ok": False, "erro": f"Erro ao atualizar: {e}"}, status=400)

    return JsonResponse({
        "ok": True,
        "mensagem": f"Paciente {paciente.nome_completo} atualizado com sucesso.",
        "codigo": paciente.codigo,
    })


@login_required
@requer_permissao("paciente.cadastrar")
def eliminar_paciente(request, codigo):
    """Elimina um paciente (e, por cascade, os seus documentos/endereço/contactos/responsável)."""

    if request.method != "POST":
        return JsonResponse({"ok": False, "erro": "Método não permitido."}, status=405)

    try:
        paciente = Paciente.objects.get(codigo=codigo, hospital=request.user.hospital)
    except Paciente.DoesNotExist:
        return JsonResponse({"ok": False, "erro": "Paciente não encontrado."}, status=404)

    nome = paciente.nome_completo
    paciente.delete()

    return JsonResponse({
        "ok": True,
        "mensagem": f"Paciente {nome} eliminado com sucesso.",
    })


# Caminho estático do logótipo da AcuraTec, usado no rodapé de todos os
# relatórios PDF. Coloca o ficheiro em: <app>/static/icons/acuratec-logo.png
# (ou ajusta o caminho abaixo para o nome/local real do ficheiro).
LOGO_ACURATEC_STATIC_PATH = "icons/acuratec-logo.png"


def _desenhar_rodape_acuratec(canvas_obj, doc):
    """Desenha o rodapé (logo + 'Desenvolvido por AcuraTec' + nº de página)
    em todas as páginas do PDF. Chamado automaticamente pelo reportlab
    via onFirstPage/onLaterPages — não chamar diretamente."""

    canvas_obj.saveState()
    largura_pagina, _altura_pagina = A4

    margem = 15 * mm
    y_linha = 14 * mm
    y_texto = 9 * mm

    # Linha separadora fina acima do rodapé
    canvas_obj.setStrokeColor(colors.HexColor("#E0E0E0"))
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(margem, y_linha, largura_pagina - margem, y_linha)

    x_texto = margem
    logo_caminho = finders.find(LOGO_ACURATEC_STATIC_PATH)

    if logo_caminho:
        try:
            logo_altura = 6 * mm
            logo_reader = ImageReader(logo_caminho)
            logo_largura_original, logo_altura_original = logo_reader.getSize()
            logo_largura = logo_altura * (logo_largura_original / logo_altura_original)

            canvas_obj.drawImage(
                logo_reader,
                margem,
                y_texto - 1 * mm,
                width=logo_largura,
                height=logo_altura,
                mask="auto",
                preserveAspectRatio=True,
            )
            x_texto = margem + logo_largura + 3 * mm
        except Exception:
            # Se o ficheiro existir mas não for uma imagem válida, ignora o
            # logo silenciosamente em vez de rebentar a geração do PDF.
            pass

    canvas_obj.setFont("Helvetica", 7.5)
    canvas_obj.setFillColor(colors.HexColor("#8A8A8A"))
    canvas_obj.drawString(x_texto, y_texto, "Desenvolvido por AcuraTec")

    canvas_obj.drawRightString(largura_pagina - margem, y_texto, f"Página {doc.page}")

    canvas_obj.restoreState()


@login_required
@requer_permissao("paciente.cadastrar")
def relatorio_pacientes_pdf(request):
    """Gera um PDF com a lista de todos os pacientes do hospital do utilizador."""

    pacientes = Paciente.objects.filter(
        hospital=request.user.hospital
    ).select_related("endereco").order_by("primeiro_nome", "ultimo_nome")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=24 * mm,  # espaço extra para o rodapé não sobrepor a tabela
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )
    styles = getSampleStyleSheet()

    estilo_subtitulo = ParagraphStyle(
        "SubtituloRelatorio",
        parent=styles["Normal"],
        textColor=colors.HexColor("#6B6B6B"),
        fontSize=9,
    )
    estilo_meta_direita = ParagraphStyle(
        "MetaDireita",
        parent=estilo_subtitulo,
        alignment=TA_RIGHT,
    )

    elementos = []

    hospital_nome = request.user.hospital.nome if request.user.hospital else "—"
    agora = timezone.localtime(timezone.now()).strftime("%d/%m/%Y %H:%M")

    elementos.append(Paragraph("Relatório de Pacientes", styles["Title"]))
    elementos.append(Paragraph(hospital_nome, estilo_subtitulo))
    elementos.append(Paragraph(
        f"Gerado em {agora} &nbsp;•&nbsp; Total: {pacientes.count()} paciente(s)",
        estilo_subtitulo,
    ))
    elementos.append(Spacer(1, 14))

    cabecalho = ["Código", "Nome Completo", "Género", "Data Nasc.", "Idade", "Contacto", "Província"]
    dados = [cabecalho]

    for p in pacientes:
        genero = "Masculino" if p.sexo == "M" else "Feminino" if p.sexo == "F" else "—"
        nascimento = p.data_nascimento.strftime("%d/%m/%Y") if p.data_nascimento else "—"
        idade = str(p.idade) if p.data_nascimento else "—"
        contacto = p.contactos.filter(principal=True).first()
        contacto_texto = contacto.contacto if contacto else "—"
        provincia = p.endereco.provincia if getattr(p, "endereco", None) else "—"

        dados.append([
            p.codigo,
            Paragraph(p.nome_completo, styles["Normal"]),
            genero,
            nascimento,
            idade,
            contacto_texto,
            provincia,
        ])

    if len(dados) == 1:
        elementos.append(Paragraph("Nenhum paciente cadastrado.", styles["Normal"]))
    else:
        tabela = Table(
            dados,
            repeatRows=1,
            colWidths=[24 * mm, 42 * mm, 20 * mm, 22 * mm, 14 * mm, 30 * mm, 24 * mm],
        )
        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F36A2D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D0D0D0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FBF3EE")]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elementos.append(tabela)

    doc.build(
        elementos,
        onFirstPage=_desenhar_rodape_acuratec,
        onLaterPages=_desenhar_rodape_acuratec,
    )
    buffer.seek(0)

    nome_ficheiro = f"relatorio_pacientes_{timezone.localtime(timezone.now()).strftime('%Y%m%d_%H%M')}.pdf"
    resposta = HttpResponse(buffer, content_type="application/pdf")
    resposta["Content-Disposition"] = f'attachment; filename="{nome_ficheiro}"'
    return resposta


@login_required
@requer_permissao("paciente.cadastrar")
def cadastrar_paciente_pagina(request):

    pacientes = Paciente.objects.filter(
        hospital=request.user.hospital
    ).order_by("-criado_em")

    return render(
        request,
        "pacientes/painel.html",
        {
            "pacientes": pacientes,
        }
    )


@login_required
def modulo_pacientes(request):

    pacientes = Paciente.objects.filter(
        hospital=request.user.hospital
    ).order_by("-criado_em")

    return render(
        request,
        "pacientes/painel.html",
        {
            "pacientes": pacientes,
        }
    )
