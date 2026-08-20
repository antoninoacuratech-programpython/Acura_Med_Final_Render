

from io import BytesIO

from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

LOGO_ACURATEC_STATIC_PATH = "icons/acuratec-logo.png"

COR_LARANJA = colors.HexColor("#F36A2D")
COR_LINHA_ALTERNADA = colors.HexColor("#FBF3EE")
COR_GRELHA = colors.HexColor("#D0D0D0")
COR_CINZA = colors.HexColor("#6B6B6B")


def desenhar_rodape_acuratec(canvas_obj, doc):
    """
    Rodapé padrão (logo + 'Desenvolvido por AcuraTec' + nº de página) —
    igual em TODOS os relatórios PDF do sistema. Chamado automaticamente
    pelo reportlab via onFirstPage/onLaterPages — nunca directamente.
    """
    canvas_obj.saveState()
    largura_pagina, _altura_pagina = A4

    margem = 15 * mm
    y_linha = 14 * mm
    y_texto = 9 * mm

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
            # Ficheiro existe mas não é uma imagem válida — ignora o logo
            # em silêncio em vez de rebentar a geração do PDF.
            pass

    canvas_obj.setFont("Helvetica", 7.5)
    canvas_obj.setFillColor(colors.HexColor("#8A8A8A"))
    canvas_obj.drawString(x_texto, y_texto, "Desenvolvido por AcuraTec")
    canvas_obj.drawRightString(largura_pagina - margem, y_texto, f"Página {doc.page}")

    canvas_obj.restoreState()


def novo_documento_pdf():
    """
    Cria o buffer + SimpleDocTemplate com as margens padrão de todos os
    relatórios. Devolve (buffer, doc) — depois de montares os
    `elementos` (lista de flowables), passa tudo a finalizar_resposta_pdf().
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=24 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )
    return buffer, doc


def cabecalho_relatorio(titulo, request, total_label=None):
    """
    Lista de elementos do cabeçalho (Título + nome do hospital + linha de
    meta com data/hora e, opcionalmente, um resumo tipo "Total: 42").
    Igual em todos os relatórios — só muda o título e o total_label.
    """
    styles = getSampleStyleSheet()

    estilo_subtitulo = ParagraphStyle(
        "SubtituloRelatorio",
        parent=styles["Normal"],
        textColor=COR_CINZA,
        fontSize=9,
    )

    hospital_nome = request.user.hospital.nome if request.user.hospital else "—"
    agora = timezone.localtime(timezone.now()).strftime("%d/%m/%Y %H:%M")

    meta_texto = f"Gerado em {agora}"
    if total_label:
        meta_texto += f" &nbsp;•&nbsp; {total_label}"

    return [
        Paragraph(titulo, styles["Title"]),
        Paragraph(hospital_nome, estilo_subtitulo),
        Paragraph(meta_texto, estilo_subtitulo),
        Spacer(1, 14),
    ]


def estilo_tabela_padrao():
    """
    TableStyle igual em todos os relatórios — cabeçalho laranja, linhas
    alternadas em creme, grelha subtil. Passa isto ao Table.setStyle()
    depois de construíres a tua tabela.
    """
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COR_LARANJA),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, COR_GRELHA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COR_LINHA_ALTERNADA]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])


def finalizar_resposta_pdf(buffer, doc, elementos, nome_base):
    """
    Constrói o PDF (com o rodapé AcuraTec em todas as páginas) e devolve
    a HttpResponse já pronta para download, com nome de ficheiro
    carimbado com a data/hora.
    """
    doc.build(
        elementos,
        onFirstPage=desenhar_rodape_acuratec,
        onLaterPages=desenhar_rodape_acuratec,
    )
    buffer.seek(0)

    nome_ficheiro = f"{nome_base}_{timezone.localtime(timezone.now()).strftime('%Y%m%d_%H%M')}.pdf"
    resposta = HttpResponse(buffer, content_type="application/pdf")
    resposta["Content-Disposition"] = f'attachment; filename="{nome_ficheiro}"'
    return resposta