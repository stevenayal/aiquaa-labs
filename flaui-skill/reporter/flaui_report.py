"""
flaui_report.py v1 — Reporte PDF ejecutivo para resultados de tests FlaUI (NUnit3 XML)
Powered by skill flaui · aiquaa.com

Estructura de reporte basada en playwright-skill/reporter/playwright_report.py (misma
paleta, estilos y layout de portada) — cambia el parser (NUnit3 XML en vez de JSON
Playwright) y agrega la matriz de trazabilidad Requerimiento -> Tests.

Uso:
    python flaui_report.py --results TestResult.xml
    python flaui_report.py --results TestResult.xml \\
        --output INFORME_UI_MIAPP.pdf \\
        --app-name "Mi App Escritorio" \\
        --environment "QA" \\
        --app-version "v1.0.0" \\
        --repo-url "https://dev.azure.com/org/repo" \\
        --author "Juan Pérez — juan@empresa.com" \\
        --pr "123"
"""

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable, Image, KeepTogether, PageBreak, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

# ─── Paleta (idéntica a playwright-skill para mantener identidad visual del stack) ───
WHITE       = colors.HexColor("#FFFFFF")
NAVY        = colors.HexColor("#0D1B40")
GRAY_DARK   = colors.HexColor("#1A1A1A")
GRAY_MID    = colors.HexColor("#4A4A4A")
GRAY_LIGHT  = colors.HexColor("#F5F5F5")
GRAY_BORDER = colors.HexColor("#DDDDDD")
GREEN_PASS  = colors.HexColor("#16A34A")
RED_FAIL    = colors.HexColor("#DC2626")
AMBER_WARN  = colors.HexColor("#D97706")
BLUE_INFO   = colors.HexColor("#2563EB")
GREEN_BG    = colors.HexColor("#F0FDF4")
RED_BG      = colors.HexColor("#FEF2F2")
AMBER_BG    = colors.HexColor("#FFFBEB")
BLUE_BG     = colors.HexColor("#EFF6FF")

PAGE_W, PAGE_H = A4
MARGIN   = 18 * mm
HEADER_H = 16 * mm
FOOTER_H = 14 * mm

REQ_ID_RE = re.compile(r"^RF-\d+$", re.IGNORECASE)


# ─── Estilos ──────────────────────────────────────────────────────────────────
def build_styles():
    return {
        "title": ParagraphStyle("title",
            fontName="Helvetica-Bold", fontSize=22,
            textColor=GRAY_DARK, leading=28),
        "subtitle": ParagraphStyle("subtitle",
            fontName="Helvetica", fontSize=11,
            textColor=GRAY_MID, leading=16),
        "section": ParagraphStyle("section",
            fontName="Helvetica-Bold", fontSize=13,
            textColor=GRAY_DARK, leading=18, spaceBefore=10),
        "subsection": ParagraphStyle("subsection",
            fontName="Helvetica-Bold", fontSize=10,
            textColor=GRAY_MID, leading=14, spaceBefore=6),
        "body": ParagraphStyle("body",
            fontName="Helvetica", fontSize=9,
            textColor=GRAY_DARK, leading=13),
        "code": ParagraphStyle("code",
            fontName="Courier", fontSize=8,
            textColor=GRAY_DARK, leading=11,
            backColor=GRAY_LIGHT, leftIndent=6),
        "label": ParagraphStyle("label",
            fontName="Helvetica-Bold", fontSize=8,
            textColor=GRAY_MID, leading=11, spaceAfter=2, spaceBefore=6),
        "stat_num": ParagraphStyle("stat_num",
            fontName="Helvetica-Bold", fontSize=20,
            textColor=GRAY_DARK, leading=24, alignment=TA_CENTER),
        "stat_label": ParagraphStyle("stat_label",
            fontName="Helvetica", fontSize=9,
            textColor=GRAY_MID, leading=12, alignment=TA_CENTER),
        "cover_meta_key": ParagraphStyle("cover_meta_key",
            fontName="Helvetica-Bold", fontSize=9,
            textColor=GRAY_MID, leading=14),
        "cover_meta_val": ParagraphStyle("cover_meta_val",
            fontName="Helvetica", fontSize=10,
            textColor=GRAY_DARK, leading=14),
        "verdict_pass": ParagraphStyle("verdict_pass",
            fontName="Helvetica-Bold", fontSize=14,
            textColor=GREEN_PASS, alignment=TA_CENTER, leading=20),
        "verdict_warn": ParagraphStyle("verdict_warn",
            fontName="Helvetica-Bold", fontSize=14,
            textColor=AMBER_WARN, alignment=TA_CENTER, leading=20),
        "verdict_fail": ParagraphStyle("verdict_fail",
            fontName="Helvetica-Bold", fontSize=14,
            textColor=RED_FAIL, alignment=TA_CENTER, leading=20),
        "error_msg": ParagraphStyle("error_msg",
            fontName="Courier", fontSize=8,
            textColor=RED_FAIL, leading=11,
            backColor=RED_BG, leftIndent=8),
    }


# ─── Canvas header/footer ─────────────────────────────────────────────────────
class ReportCanvas:
    def __init__(self, author=None, environment=None):
        self.author      = author
        self.environment = environment

    def __call__(self, canvas, doc):
        canvas.saveState()
        w, h = A4

        canvas.setStrokeColor(GRAY_BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, h - HEADER_H, w - MARGIN, h - HEADER_H)
        canvas.line(MARGIN, FOOTER_H, w - MARGIN, FOOTER_H)

        if doc.page > 1 and self.environment:
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(GRAY_MID)
            canvas.drawString(MARGIN, h - HEADER_H + 4 * mm,
                              f"Ambiente: {self.environment}")

        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(NAVY)
        footer_left = (
            f"Automatización: {self.author}  |  Powered by skill flaui · aiquaa.com"
            if self.author else "Powered by skill flaui · https://aiquaa.com/"
        )
        canvas.drawString(MARGIN, FOOTER_H - 5 * mm, footer_left)
        canvas.setFillColor(GRAY_MID)
        canvas.drawRightString(w - MARGIN, FOOTER_H - 5 * mm, f"Pág. {doc.page}")
        canvas.restoreState()


# ─── Parser NUnit3 XML ─────────────────────────────────────────────────────────
def _iter_test_cases(node):
    """Recorre recursivamente <test-suite> anidados y produce cada <test-case>."""
    for child in node:
        if child.tag == "test-case":
            yield child
        elif child.tag == "test-suite":
            yield from _iter_test_cases(child)


def _extract_req_id(test_case) -> str | None:
    """Busca ReqId explícito o un tag/categoría con forma RF-XXX."""
    props = test_case.find("properties")
    if props is None:
        return None
    for prop in props.findall("property"):
        name = prop.get("name", "")
        value = prop.get("value", "")
        if name == "ReqId" and value:
            return value.upper()
        if name in ("Category", "Tag") and REQ_ID_RE.match(value or ""):
            return value.upper()
    return None


def _extract_screenshot(test_case) -> str | None:
    attachments = test_case.find("attachments")
    if attachments is None:
        return None
    for att in attachments.findall("attachment"):
        path_el = att.find("filePath")
        if path_el is not None and path_el.text:
            p = path_el.text.strip()
            if p.lower().endswith((".png", ".jpg", ".jpeg")) and os.path.isfile(p):
                return p
    return None


def parse_results(path: str) -> dict:
    tree = ET.parse(path)
    root = tree.getroot()  # <test-run> (NUnit3) o <test-suite> raíz suelto

    total = passed = failed = skipped = 0
    duration_s = 0.0
    failures = []
    req_map: dict[str, dict] = {}   # RF-001 -> {tests: [], passed, failed}
    orphans = {"total": 0, "passed": 0, "failed": 0}

    for tc in _iter_test_cases(root):
        result = tc.get("result", "Unknown")
        dur = float(tc.get("duration", "0") or 0)
        duration_s += dur
        name = tc.get("fullname") or tc.get("name") or "?"
        total += 1

        is_pass = result in ("Passed",)
        is_fail = result in ("Failed",)
        is_skip = result in ("Skipped", "Ignored", "Inconclusive")

        if is_pass:
            passed += 1
        elif is_fail:
            failed += 1
        elif is_skip:
            skipped += 1

        req_id = _extract_req_id(tc)
        bucket = req_map.setdefault(req_id, {"tests": [], "passed": 0, "failed": 0, "skipped": 0}) \
            if req_id else None
        target = bucket if bucket is not None else orphans

        if bucket is not None:
            bucket["tests"].append(name)
            if is_pass:
                bucket["passed"] += 1
            elif is_fail:
                bucket["failed"] += 1
            elif is_skip:
                bucket["skipped"] += 1
        else:
            orphans["total"] += 1
            if is_pass:
                orphans["passed"] += 1
            elif is_fail:
                orphans["failed"] += 1

        if is_fail:
            failure_node = tc.find("failure")
            message = stack = ""
            if failure_node is not None:
                msg_el = failure_node.find("message")
                stack_el = failure_node.find("stack-trace")
                message = (msg_el.text or "").strip() if msg_el is not None else ""
                stack = (stack_el.text or "").strip() if stack_el is not None else ""
            failures.append({
                "title": name,
                "message": message[:400],
                "stack": stack[:400],
                "screenshot": _extract_screenshot(tc),
            })

    pass_rate = round(passed / total * 100, 1) if total > 0 else 0

    return {
        "total": total, "passed": passed, "failed": failed, "skipped": skipped,
        "pass_rate": pass_rate,
        "duration_s": round(duration_s, 1),
        "failures": failures,
        "requirements": req_map,
        "orphans": orphans,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ─── Veredicto ────────────────────────────────────────────────────────────────
def get_verdict(stats: dict):
    uncovered = sum(1 for r in stats["requirements"].values() if r["passed"] + r["failed"] == 0)
    if stats["failed"] == 0 and uncovered == 0:
        return "SUITE VERDE — TODOS LOS TESTS PASARON, SIN REQUERIMIENTOS SIN COBERTURA", "pass"
    elif stats["failed"] == 0:
        return "SUITE VERDE CON GAPS — TESTS OK PERO HAY RF SIN COBERTURA", "warn"
    elif stats["pass_rate"] >= 85:
        return "FALLOS MENORES — REVISAR ANTES DEL RELEASE", "warn"
    else:
        return "REGRESIÓN CRÍTICA — BLOQUEA EL RELEASE", "fail"


# ─── Portada ──────────────────────────────────────────────────────────────────
def build_cover(stats, styles, app_name, environment,
                app_version=None, repo_url=None, author=None, pr=None):
    story = []
    w_content = PAGE_W - 2 * MARGIN

    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("Informe Ejecutivo de Automatización de Pantallas", styles["title"]))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        f'<font color="#4A4A4A">{app_name}</font>', styles["subtitle"]))
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY_BORDER))
    story.append(Spacer(1, 6 * mm))

    stat_col = w_content / 4

    def stat_cell(num, label, col=GRAY_DARK):
        return [
            Paragraph(f'<font color="{col.hexval()}">{num}</font>', styles["stat_num"]),
            Paragraph(label, styles["stat_label"]),
        ]

    stat_table = Table(
        [[
            stat_cell(stats["total"],   "Tests totales"),
            stat_cell(stats["passed"],  "Pasaron", GREEN_PASS),
            stat_cell(stats["failed"],  "Fallaron",
                      RED_FAIL if stats["failed"] > 0 else GRAY_DARK),
            stat_cell(f'{stats["pass_rate"]}%', "Tasa de éxito",
                      GREEN_PASS if stats["pass_rate"] >= 95 else
                      AMBER_WARN if stats["pass_rate"] >= 85 else RED_FAIL),
        ]],
        colWidths=[stat_col] * 4,
        style=TableStyle([
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("BACKGROUND",    (0, 0), (-1, -1), GRAY_LIGHT),
            ("BOX",           (0, 0), (-1, -1), 0.5, GRAY_BORDER),
            ("INNERGRID",     (0, 0), (-1, -1), 0.5, GRAY_BORDER),
        ])
    )
    story.append(stat_table)
    story.append(Spacer(1, 6 * mm))

    verdict_text, verdict_type = get_verdict(stats)
    verdict_style = {
        "pass": styles["verdict_pass"],
        "warn": styles["verdict_warn"],
        "fail": styles["verdict_fail"],
    }[verdict_type]
    verdict_bg = {"pass": GREEN_BG, "warn": AMBER_BG, "fail": RED_BG}[verdict_type]

    verdict_table = Table(
        [[Paragraph(verdict_text, verdict_style)]],
        colWidths=[w_content],
        style=TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), verdict_bg),
            ("BOX",           (0, 0), (-1, -1), 0.5, GRAY_BORDER),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ])
    )
    story.append(verdict_table)
    story.append(Spacer(1, 6 * mm))

    meta = [
        ["Fecha / hora",   stats["timestamp"]],
        ["Ambiente",       environment or "No especificado"],
        ["Duración total", f"{stats['duration_s']} seg"],
        ["Tests omitidos", str(stats["skipped"])],
    ]
    if app_version:
        meta.insert(2, ["Versión / release", app_version])
    if pr:
        meta.append(["Pull Request", f"#{pr}"])
    if repo_url:
        meta.append(["Repositorio", f'<font color="#0D1B40"><u>{repo_url}</u></font>'])

    meta_table = Table(
        [[Paragraph(r[0], styles["cover_meta_key"]),
          Paragraph(r[1], styles["cover_meta_val"])] for r in meta],
        colWidths=[42 * mm, w_content - 42 * mm],
        style=TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LINEBELOW",     (0, 0), (-1, -2), 0.3, GRAY_BORDER),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 10 * mm))
    story.append(HRFlowable(width="100%", thickness=0.3, color=GRAY_BORDER))
    story.append(Spacer(1, 3 * mm))

    credit_lines = [
        'Powered by skill <font color="#0D1B40"><b>flaui</b></font>'
        ' · <font color="#0D1B40"><u>https://aiquaa.com/</u></font>'
    ]
    if author:
        credit_lines.append(
            f'Automatización realizada por: <font color="#0D1B40"><b>{author}</b></font>'
        )
    story.append(Paragraph("<br/>".join(credit_lines),
        ParagraphStyle("cover_credit", fontName="Helvetica", fontSize=9,
                       textColor=GRAY_MID, alignment=TA_CENTER, leading=14)))

    story.append(PageBreak())
    return story


# ─── Matriz de trazabilidad RF ↔ Tests ────────────────────────────────────────
def build_traceability(stats, styles):
    story = []
    w_content = PAGE_W - 2 * MARGIN

    story.append(Paragraph("Matriz de Trazabilidad — Requerimientos", styles["section"]))
    story.append(Spacer(1, 3 * mm))

    reqs = stats["requirements"]
    if not reqs and stats["orphans"]["total"] == 0:
        story.append(Paragraph(
            "No se encontraron tests con ReqId asociado (atributo [Req(\"RF-XXX\")] "
            "o tag @RF-XXX en Reqnroll).", styles["body"]))
        return story

    headers = ["Requerimiento", "Tests", "Pasaron", "Fallaron", "Cobertura"]
    col_w = [w_content * 0.22, w_content * 0.40] + [w_content * 0.12] * 3

    header_row = [Paragraph(f"<b>{h}</b>", ParagraphStyle(
        "th", fontName="Helvetica-Bold", fontSize=8,
        textColor=WHITE, alignment=TA_CENTER)) for h in headers]

    data = [header_row]
    for req_id in sorted(reqs.keys()):
        r = reqs[req_id]
        n = len(r["tests"])
        covered = (r["passed"] + r["failed"]) > 0
        if r["failed"] > 0:
            cobertura = Paragraph('<font color="#DC2626"><b>CON FALLOS</b></font>',
                ParagraphStyle("cf", fontName="Helvetica-Bold", fontSize=8,
                               textColor=RED_FAIL, alignment=TA_CENTER))
        elif covered:
            cobertura = Paragraph('<font color="#16A34A">CUBIERTO</font>',
                ParagraphStyle("cc", fontName="Helvetica-Bold", fontSize=8,
                               textColor=GREEN_PASS, alignment=TA_CENTER))
        else:
            cobertura = Paragraph('<font color="#D97706">SIN EJECUTAR</font>',
                ParagraphStyle("cs", fontName="Helvetica", fontSize=8,
                               textColor=AMBER_WARN, alignment=TA_CENTER))

        tests_text = "<br/>".join(t.split(".")[-1] for t in r["tests"][:6])
        if n > 6:
            tests_text += f"<br/>+{n - 6} más"

        data.append([
            Paragraph(f"<b>{req_id}</b>", ParagraphStyle(
                "rid", fontName="Helvetica-Bold", fontSize=8, textColor=NAVY)),
            Paragraph(tests_text, ParagraphStyle(
                "tt", fontName="Helvetica", fontSize=7.5, textColor=GRAY_DARK, leading=10)),
            Paragraph(str(r["passed"]), ParagraphStyle(
                "tp", fontName="Helvetica", fontSize=8, textColor=GREEN_PASS, alignment=TA_CENTER)),
            Paragraph(str(r["failed"]), ParagraphStyle(
                "tf", fontName="Helvetica-Bold", fontSize=8,
                textColor=RED_FAIL if r["failed"] > 0 else GRAY_DARK, alignment=TA_CENTER)),
            cobertura,
        ])

    if stats["orphans"]["total"] > 0:
        o = stats["orphans"]
        data.append([
            Paragraph("<i>SIN REQUERIMIENTO</i>", ParagraphStyle(
                "orid", fontName="Helvetica-Oblique", fontSize=8, textColor=GRAY_MID)),
            Paragraph(f'{o["total"]} test(s) sin [Req] ni tag RF-XXX asociado',
                      ParagraphStyle("ott", fontName="Helvetica", fontSize=7.5, textColor=GRAY_MID)),
            Paragraph(str(o["passed"]), ParagraphStyle(
                "otp", fontName="Helvetica", fontSize=8, textColor=GREEN_PASS, alignment=TA_CENTER)),
            Paragraph(str(o["failed"]), ParagraphStyle(
                "otf", fontName="Helvetica", fontSize=8,
                textColor=RED_FAIL if o["failed"] > 0 else GRAY_DARK, alignment=TA_CENTER)),
            Paragraph("—", ParagraphStyle("otc", fontName="Helvetica", fontSize=8,
                                           textColor=GRAY_MID, alignment=TA_CENTER)),
        ])

    tbl = Table(data, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_LIGHT]),
        ("BOX",            (0, 0), (-1, -1), 0.5, GRAY_BORDER),
        ("INNERGRID",      (0, 0), (-1, -1), 0.3, GRAY_BORDER),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ("LEFTPADDING",    (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 6),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(tbl)

    uncovered = [rid for rid, r in reqs.items() if r["passed"] + r["failed"] == 0]
    if uncovered:
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph(
            f'⚠️ Requerimientos sin ningún test ejecutado: {", ".join(sorted(uncovered))}',
            styles["label"]))

    return story


# ─── Detalle de fallos ────────────────────────────────────────────────────────
def build_failures(stats, styles):
    if not stats["failures"]:
        return []

    story = []
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("Detalle de Fallos", styles["section"]))
    story.append(Spacer(1, 3 * mm))

    w_content = PAGE_W - 2 * MARGIN

    def esc(s):
        return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    for i, f in enumerate(stats["failures"], 1):
        block = []
        header = Table(
            [[Paragraph(
                f'<font color="{RED_FAIL.hexval()}"><b>#{i} {esc(f["title"])}</b></font>',
                ParagraphStyle("fh", fontName="Helvetica-Bold", fontSize=9, textColor=RED_FAIL)
            )]],
            colWidths=[w_content],
            style=TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), RED_BG),
                ("BOX",           (0, 0), (-1, -1), 0.5, GRAY_BORDER),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ])
        )
        block.append(header)

        if f["message"]:
            block.append(Paragraph("Mensaje:", styles["label"]))
            block.append(Paragraph(esc(f["message"]), styles["error_msg"]))

        if f["stack"]:
            block.append(Paragraph("Stack trace:", styles["label"]))
            block.append(Paragraph(esc(f["stack"]), styles["code"]))

        if f["screenshot"]:
            block.append(Paragraph("Captura al momento del fallo:", styles["label"]))
            try:
                img = Image(f["screenshot"])
                max_w = w_content
                if img.imageWidth > max_w:
                    ratio = max_w / img.imageWidth
                    img.drawWidth = max_w
                    img.drawHeight = img.imageHeight * ratio
                block.append(img)
            except Exception:
                block.append(Paragraph(f'(no se pudo cargar {esc(f["screenshot"])})', styles["body"]))

        block.append(Spacer(1, 4 * mm))
        block.append(HRFlowable(width="100%", thickness=0.3, color=GRAY_BORDER))
        block.append(Spacer(1, 3 * mm))

        story.append(KeepTogether(block))

    return story


# ─── Entry point ──────────────────────────────────────────────────────────────
def generate_report(results_path, output_path, app_name="App",
                    environment=None, app_version=None,
                    repo_url=None, author=None, pr=None):
    stats = parse_results(results_path)

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=HEADER_H + 6 * mm, bottomMargin=FOOTER_H + 8 * mm,
        title=f"Informe Ejecutivo UI — {app_name}",
        author="aiquaa — https://aiquaa.com/",
    )

    styles  = build_styles()
    on_page = ReportCanvas(author=author, environment=environment)

    story  = build_cover(stats, styles, app_name, environment,
                         app_version=app_version, repo_url=repo_url, author=author, pr=pr)
    story += build_traceability(stats, styles)
    story += build_failures(stats, styles)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

    verdict_text, _ = get_verdict(stats)
    print(f"Reporte : {output_path}")
    print(f"  Total  : {stats['total']} tests")
    print(f"  Passed : {stats['passed']} ({stats['pass_rate']}%)")
    print(f"  Failed : {stats['failed']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  RF cubiertos: {sum(1 for r in stats['requirements'].values() if r['passed']+r['failed']>0)}"
          f"/{len(stats['requirements'])}")
    print(f"  Duración: {stats['duration_s']}s")
    print(f"  Veredicto: {verdict_text}")


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="FlaUI PDF Report Ejecutivo — aiquaa.com")
    parser.add_argument("--results",     required=True, help="XML NUnit3 de resultados (TestResult.xml)")
    parser.add_argument("--output",      default=None,  help="Nombre del PDF de salida")
    parser.add_argument("--app-name",    default="App", help="Nombre de la aplicación")
    parser.add_argument("--environment", default=None,  help="Ambiente (QA, Staging, etc.)")
    parser.add_argument("--app-version", default=None,  help="Versión de la aplicación")
    parser.add_argument("--repo-url",    default=None,  help="URL del repositorio")
    parser.add_argument("--author",      default=None,  help="Autor de la automatización")
    parser.add_argument("--pr",          default=None,  help="Número de Pull Request de origen")
    args = parser.parse_args()

    output_path = args.output
    if not output_path:
        slug = re.sub(r"[^A-Z0-9]+", "_", args.app_name.upper()).strip("_")
        output_path = f"INFORME_UI_{slug}.pdf"

    generate_report(
        results_path=args.results,
        output_path=output_path,
        app_name=args.app_name,
        environment=args.environment,
        app_version=args.app_version,
        repo_url=args.repo_url,
        author=args.author,
        pr=args.pr,
    )
