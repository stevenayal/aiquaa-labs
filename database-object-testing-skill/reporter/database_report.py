"""Generar un informe PDF desde db-test-report.json."""

import argparse
import json
from datetime import datetime
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

NAVY = colors.HexColor("#0D1B40")
BLUE = colors.HexColor("#2563EB")
GREEN = colors.HexColor("#15803D")
GREEN_BG = colors.HexColor("#F0FDF4")
RED = colors.HexColor("#B91C1C")
RED_BG = colors.HexColor("#FEF2F2")
AMBER = colors.HexColor("#B45309")
AMBER_BG = colors.HexColor("#FFFBEB")
INK = colors.HexColor("#172033")
MUTED = colors.HexColor("#5D6678")
LIGHT = colors.HexColor("#F4F6FA")
BORDER = colors.HexColor("#D9DEE8")
WHITE = colors.white
PAGE_W, PAGE_H = A4
MARGIN = 18 * mm


def safe(value):
    return escape(str(value if value is not None else "-"))


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("Title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=23, leading=28, textColor=NAVY, alignment=TA_LEFT),
        "subtitle": ParagraphStyle("Subtitle", parent=base["BodyText"], fontSize=10, leading=15, textColor=MUTED),
        "section": ParagraphStyle("Section", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=NAVY, spaceBefore=6, spaceAfter=7),
        "case": ParagraphStyle("Case", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=11, leading=15, textColor=INK),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontSize=8.5, leading=12, textColor=INK),
        "small": ParagraphStyle("Small", parent=base["BodyText"], fontSize=7.5, leading=10, textColor=MUTED),
        "stat": ParagraphStyle("Stat", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=19, leading=22, alignment=TA_CENTER, textColor=NAVY),
        "stat_label": ParagraphStyle("StatLabel", parent=base["BodyText"], fontSize=7.5, leading=10, alignment=TA_CENTER, textColor=MUTED),
        "verdict": ParagraphStyle("Verdict", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=14, leading=18, alignment=TA_CENTER),
    }


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 13 * mm, PAGE_W - MARGIN, 13 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(NAVY)
    canvas.drawString(MARGIN, 8 * mm, "Pruebas de objetos de base de datos - aiquaa")
    canvas.setFillColor(MUTED)
    canvas.drawRightString(PAGE_W - MARGIN, 8 * mm, f"Pagina {doc.page}")
    canvas.restoreState()


def status_label(status):
    return "APROBADO" if status == "passed" else "FALLIDO"


def status_color(status):
    return GREEN if status == "passed" else RED


def stat_cell(number, label, style):
    return [Paragraph(str(number), style["stat"]), Paragraph(label, style["stat_label"])]


def table_style(header=True):
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [WHITE, LIGHT]),
    ]
    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
        ])
    return TableStyle(commands)


def build_story(report):
    style = styles()
    metadata = report.get("metadata", {})
    summary = report["summary"]
    story = [
        Spacer(1, 8 * mm),
        Paragraph("Informe de pruebas funcionales", style["title"]),
        Paragraph("Objetos de bases de datos relacionales via API REST", style["subtitle"]),
        Spacer(1, 4 * mm),
        HRFlowable(width="100%", thickness=1, color=BLUE),
        Spacer(1, 6 * mm),
    ]

    def meta_value(value):
        return Paragraph(safe(value), style["body"])

    meta_rows = [
        ["Suite", meta_value(report.get("suite")), "Ambiente", meta_value(metadata.get("environment", "Comparativo"))],
        ["Generado", meta_value(report.get("generatedAt")), "Version", meta_value(metadata.get("version", "No informada"))],
        ["Autor", meta_value(metadata.get("author", "No informado")), "Repositorio", meta_value(metadata.get("repoUrl", "No informado"))],
    ]
    meta = Table(meta_rows, colWidths=[25 * mm, 60 * mm, 25 * mm, 65 * mm])
    meta.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([meta, Spacer(1, 7 * mm)])

    verdict_color = status_color(report["status"])
    verdict_bg = GREEN_BG if report["status"] == "passed" else RED_BG
    verdict = Table([[Paragraph(status_label(report["status"]), ParagraphStyle("VerdictColor", parent=style["verdict"], textColor=verdict_color))]], colWidths=[175 * mm])
    verdict.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), verdict_bg), ("BOX", (0, 0), (-1, -1), 1, verdict_color), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story.extend([verdict, Spacer(1, 7 * mm)])

    stats = Table([[
        stat_cell(summary["total"], "CASOS", style),
        stat_cell(summary["passed"], "APROBADOS", style),
        stat_cell(summary["failed"], "FALLIDOS", style),
        stat_cell(f"{sum(case.get('durationMs', 0) for case in report['cases'])} ms", "DURACION ACUMULADA", style),
    ]], colWidths=[43.75 * mm] * 4)
    stats.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, BORDER), ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER), ("BACKGROUND", (0, 0), (-1, -1), WHITE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story.extend([stats, Spacer(1, 8 * mm), Paragraph("Resumen de casos", style["section"])])

    rows = [["Caso", "Objeto", "Duracion", "Hallazgos", "Estado"]]
    for case in report["cases"]:
        failed_findings = sum(1 for finding in case.get("findings", []) if not finding.get("passed", False))
        rows.append([
            Paragraph(safe(case["id"]), style["body"]),
            Paragraph(safe(case["objectType"]), style["body"]),
            f"{case.get('durationMs', 0)} ms",
            str(failed_findings),
            Paragraph(f'<font color="{status_color(case["status"]).hexval()}"><b>{status_label(case["status"])}</b></font>', style["body"]),
        ])
    summary_table = Table(rows, colWidths=[61 * mm, 32 * mm, 25 * mm, 24 * mm, 33 * mm], repeatRows=1)
    summary_table.setStyle(table_style())
    story.extend([summary_table, PageBreak(), Paragraph("Detalle funcional y tecnico", style["section"]), Spacer(1, 2 * mm)])

    category_names = {
        "assertion": "Validacion funcional",
        "functional-diff": "Diferencia funcional",
        "cost": "Comparacion de costo",
        "rule": "Regla de base de datos",
        "execution": "Ejecucion",
    }
    for index, case in enumerate(report["cases"]):
        findings = case.get("findings", [])
        heading = [
            Paragraph(f"{safe(case['id'])} - {safe(case['objectType'])}", style["case"]),
            Paragraph(f"Estado: <b>{status_label(case['status'])}</b> | Duracion: {case.get('durationMs', 0)} ms", style["small"]),
            Spacer(1, 2 * mm),
        ]
        finding_rows = [["Tipo", "Evaluacion", "Resultado"]]
        for finding in findings:
            message = finding.get("message") or finding.get("path") or finding.get("metric") or finding.get("error") or "Sin detalle"
            if finding.get("category") == "cost" and finding.get("changePercent") is not None:
                change = finding["changePercent"]
                change_text = f"{change:.2f}%" if isinstance(change, (int, float)) else safe(change)
                message = f"{message}: {finding.get('baseline')} -> {finding.get('candidate')} (cambio {change_text}; limite {finding.get('limitPercent')}%)"
            result = "OK" if finding.get("passed") else ("ADVERTENCIA" if finding.get("severity") == "warning" else "FALLO")
            result_color = GREEN if result == "OK" else (AMBER if result == "ADVERTENCIA" else RED)
            finding_rows.append([
                Paragraph(safe(category_names.get(finding.get("category"), finding.get("category", "Otro"))), style["body"]),
                Paragraph(safe(message), style["body"]),
                Paragraph(f'<font color="{result_color.hexval()}"><b>{result}</b></font>', style["body"]),
            ])
        if len(finding_rows) == 1:
            finding_rows.append(["General", "Sin hallazgos registrados", Paragraph('<font color="#15803D"><b>OK</b></font>', style["body"])])
        detail = Table(finding_rows, colWidths=[38 * mm, 110 * mm, 27 * mm], repeatRows=1)
        detail.setStyle(table_style())
        block = heading + [detail, Spacer(1, 7 * mm)]
        if len(findings) <= 5:
            story.append(KeepTogether(block))
        else:
            story.extend(block)
        if index < len(report["cases"]) - 1:
            story.append(HRFlowable(width="100%", thickness=0.4, color=BORDER))

    story.extend([
        Spacer(1, 6 * mm),
        Paragraph("Notas del informe", style["section"]),
        Paragraph("Las respuestas y los valores funcionales sensibles se omiten por defecto. Las metricas de costo se incluyen para sustentar la comparacion. Este informe refleja exclusivamente la evidencia devuelta por la API REST durante la ejecucion.", style["body"]),
    ])
    return story


def generate(results, output):
    with open(results, encoding="utf-8") as stream:
        report = json.load(stream)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=17 * mm,
        bottomMargin=18 * mm,
        title=f"Informe funcional - {report.get('suite', 'base de datos')}",
        author=report.get("metadata", {}).get("author", "aiquaa"),
        subject="Pruebas funcionales de objetos de bases de datos",
    )
    doc.build(build_story(report), onFirstPage=footer, onLaterPages=footer)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generar informe PDF de pruebas de objetos de base de datos")
    parser.add_argument("--results", required=True, help="db-test-report.json")
    parser.add_argument("--output", required=True, help="PDF de salida")
    args = parser.parse_args()
    path = generate(args.results, args.output)
    print(f"PDF generado: {path}")


if __name__ == "__main__":
    main()
