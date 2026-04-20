"""
jmeter_report.py v1 — Generador de reporte PDF para resultados de JMeter (.jtl)
Powered by skill jmeter · aiquaa.com

Uso:
    python jmeter_report.py --results results/R_MI_API.jtl
    python jmeter_report.py --results results/R_MI_API.jtl \\
        --output INFORME_PERF_MI_API.pdf \\
        --api-name "Mi API" \\
        --threads 1000 \\
        --loops 30 \\
        --author "Juan Pérez — juan@empresa.com" \\
        --repo-url "https://dev.azure.com/org/repo" \\
        --api-version "v1.2.0"
"""

import argparse
import os
import re
from datetime import datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable, Image, KeepTogether, PageBreak, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

# ─── Paleta ───────────────────────────────────────────────────────────────────
BLACK       = colors.HexColor("#000000")
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

PAGE_W, PAGE_H = A4
MARGIN   = 18 * mm
HEADER_H = 16 * mm
FOOTER_H = 14 * mm


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
        "label": ParagraphStyle("label",
            fontName="Helvetica-Bold", fontSize=8,
            textColor=GRAY_MID, leading=11, spaceAfter=2, spaceBefore=6),
        "body": ParagraphStyle("body",
            fontName="Helvetica", fontSize=9,
            textColor=GRAY_DARK, leading=13),
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
    }


# ─── Canvas header/footer ─────────────────────────────────────────────────────
class ReportCanvas:
    def __init__(self, author=None):
        self.author = author

    def __call__(self, canvas, doc):
        canvas.saveState()
        w, h = A4

        canvas.setStrokeColor(GRAY_BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, h - HEADER_H, w - MARGIN, h - HEADER_H)
        canvas.line(MARGIN, FOOTER_H, w - MARGIN, FOOTER_H)

        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(NAVY)
        footer_left = (
            f"Prueba de rendimiento: {self.author}  |  Powered by skill jmeter · aiquaa.com"
            if self.author else "Powered by skill jmeter · https://aiquaa.com/"
        )
        canvas.drawString(MARGIN, FOOTER_H - 5 * mm, footer_left)
        canvas.setFillColor(GRAY_MID)
        canvas.drawRightString(w - MARGIN, FOOTER_H - 5 * mm, f"Pág. {doc.page}")
        canvas.restoreState()


# ─── Parser .jtl ─────────────────────────────────────────────────────────────
def parse_jtl(path: str) -> dict:
    df = pd.read_csv(path)

    # Columnas estándar JMeter .jtl
    required = {"elapsed", "success", "label"}
    if not required.issubset(df.columns):
        raise ValueError(
            f"El .jtl no tiene columnas esperadas. Encontradas: {list(df.columns)}"
        )

    total      = len(df)
    errors     = df[df["success"] == False]
    error_cnt  = len(errors)
    error_rate = (error_cnt / total * 100) if total > 0 else 0

    elapsed = df["elapsed"]
    stats = {
        "total":      total,
        "errors":     error_cnt,
        "error_rate": round(error_rate, 2),
        "avg":        round(elapsed.mean(), 1),
        "min":        int(elapsed.min()),
        "max":        int(elapsed.max()),
        "p90":        round(elapsed.quantile(0.90), 1),
        "p95":        round(elapsed.quantile(0.95), 1),
        "p99":        round(elapsed.quantile(0.99), 1),
        "median":     round(elapsed.median(), 1),
    }

    # Throughput: requests por segundo
    if "timeStamp" in df.columns:
        ts = df["timeStamp"]
        duration_sec = (ts.max() - ts.min()) / 1000
        stats["throughput"] = round(total / duration_sec, 2) if duration_sec > 0 else 0
        stats["duration_sec"] = round(duration_sec, 1)
    else:
        stats["throughput"] = 0
        stats["duration_sec"] = 0

    # Latency si existe
    stats["avg_latency"] = round(df["Latency"].mean(), 1) if "Latency" in df.columns else None

    # Por sampler
    samplers = []
    for label, grp in df.groupby("label"):
        grp_errors = len(grp[grp["success"] == False])
        samplers.append({
            "label":      label,
            "total":      len(grp),
            "errors":     grp_errors,
            "error_rate": round(grp_errors / len(grp) * 100, 2),
            "avg":        round(grp["elapsed"].mean(), 1),
            "p90":        round(grp["elapsed"].quantile(0.90), 1),
            "p95":        round(grp["elapsed"].quantile(0.95), 1),
            "max":        int(grp["elapsed"].max()),
        })

    # Top errores
    top_errors = []
    if "responseCode" in df.columns and error_cnt > 0:
        err_df = errors.copy()
        err_df = err_df.groupby(["label", "responseCode"]).size().reset_index(name="count")
        err_df = err_df.sort_values("count", ascending=False).head(10)
        for _, row in err_df.iterrows():
            top_errors.append({
                "sampler": row["label"],
                "code":    str(row["responseCode"]),
                "count":   int(row["count"]),
            })

    return stats, samplers, top_errors


# ─── Veredicto ────────────────────────────────────────────────────────────────
def get_verdict(stats):
    if stats["error_rate"] > 10:
        return "COLAPSO BAJO ESTRÉS", "fail"
    elif stats["error_rate"] > 2 or stats["p95"] > 3000:
        return "DEGRADACIÓN DETECTADA", "warn"
    else:
        return "API AGUANTA LA CARGA", "pass"


# ─── Portada ──────────────────────────────────────────────────────────────────
def build_cover(stats, samplers, styles, api_name, threads, loops,
                api_version=None, repo_url=None, author=None, banner=None):
    story = []
    w_content = PAGE_W - 2 * MARGIN

    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("Informe de Prueba de Rendimiento", styles["title"]))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        f'<font color="#4A4A4A">{api_name}</font>', styles["subtitle"]))
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY_BORDER))
    story.append(Spacer(1, 6 * mm))

    # ── Estadísticas principales ──────────────────────────────────────────────
    stat_col = w_content / 4
    total_req = threads * loops

    def stat_cell(num, label, color=GRAY_DARK):
        return [
            Paragraph(f'<font color="{color.hexval()}">{num}</font>', styles["stat_num"]),
            Paragraph(label, styles["stat_label"]),
        ]

    stat_table = Table(
        [[
            stat_cell(f"{total_req:,}", "Peticiones totales"),
            stat_cell(f"{stats['throughput']}", "Req/seg"),
            stat_cell(f"{stats['avg']} ms", "Tiempo promedio"),
            stat_cell(
                f"{stats['error_rate']}%",
                "Error rate",
                RED_FAIL if stats["error_rate"] > 2 else GREEN_PASS
            ),
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

    # ── Percentiles ───────────────────────────────────────────────────────────
    perc_col = w_content / 5
    perc_table = Table(
        [[
            stat_cell(f"{stats['min']} ms", "Mínimo"),
            stat_cell(f"{stats['median']} ms", "Mediana"),
            stat_cell(f"{stats['p90']} ms", "Percentil 90"),
            stat_cell(f"{stats['p95']} ms", "Percentil 95"),
            stat_cell(f"{stats['p99']} ms", "Percentil 99"),
        ]],
        colWidths=[perc_col] * 5,
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
    story.append(perc_table)
    story.append(Spacer(1, 6 * mm))

    # ── Veredicto ─────────────────────────────────────────────────────────────
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

    # ── Metadata ──────────────────────────────────────────────────────────────
    meta = [
        ["Fecha / hora", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Threads (usuarios)", str(threads)],
        ["Loops por thread", str(loops)],
        ["Total requests", f"{threads * loops:,}"],
        ["Duración real", f"{stats['duration_sec']} seg"],
    ]
    if api_version:
        meta.append(["Versión / release", api_version])
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
        'Powered by skill <font color="#0D1B40"><b>jmeter</b></font>'
        ' · <font color="#0D1B40"><u>https://aiquaa.com/</u></font>'
    ]
    if author:
        credit_lines.append(
            f'Prueba ejecutada por: <font color="#0D1B40"><b>{author}</b></font>'
        )
    story.append(Paragraph("<br/>".join(credit_lines),
        ParagraphStyle("cover_credit", fontName="Helvetica", fontSize=9,
                       textColor=GRAY_MID, alignment=TA_CENTER, leading=14)))

    story.append(PageBreak())
    return story


# ─── Detalle por sampler ──────────────────────────────────────────────────────
def build_sampler_detail(samplers, top_errors, styles):
    story = []
    w_content = PAGE_W - 2 * MARGIN

    story.append(Paragraph("Detalle por Sampler", styles["section"]))
    story.append(Spacer(1, 3 * mm))

    # Tabla de samplers
    headers = ["Sampler", "Total", "Errores", "Error %", "Avg ms", "P90 ms", "P95 ms", "Max ms"]
    col_w = [w_content * 0.28] + [w_content * 0.72 / 7] * 7

    header_row = [Paragraph(f"<b>{h}</b>", ParagraphStyle(
        "th", fontName="Helvetica-Bold", fontSize=8,
        textColor=GRAY_DARK, alignment=TA_CENTER)) for h in headers]

    data = [header_row]
    for s in samplers:
        err_color = RED_FAIL if s["error_rate"] > 2 else GRAY_DARK
        row = [
            Paragraph(s["label"], ParagraphStyle(
                "td", fontName="Helvetica", fontSize=8, textColor=GRAY_DARK)),
            Paragraph(str(s["total"]), ParagraphStyle(
                "tdc", fontName="Helvetica", fontSize=8,
                textColor=GRAY_DARK, alignment=TA_CENTER)),
            Paragraph(str(s["errors"]), ParagraphStyle(
                "tde", fontName="Helvetica", fontSize=8,
                textColor=err_color, alignment=TA_CENTER)),
            Paragraph(
                f'<font color="{err_color.hexval()}">{s["error_rate"]}%</font>',
                ParagraphStyle("tdp", fontName="Helvetica-Bold", fontSize=8,
                               textColor=err_color, alignment=TA_CENTER)),
            Paragraph(str(s["avg"]), ParagraphStyle(
                "tdm", fontName="Helvetica", fontSize=8,
                textColor=GRAY_DARK, alignment=TA_CENTER)),
            Paragraph(str(s["p90"]), ParagraphStyle(
                "td90", fontName="Helvetica", fontSize=8,
                textColor=GRAY_DARK, alignment=TA_CENTER)),
            Paragraph(str(s["p95"]), ParagraphStyle(
                "td95", fontName="Helvetica", fontSize=8,
                textColor=GRAY_DARK, alignment=TA_CENTER)),
            Paragraph(str(s["max"]), ParagraphStyle(
                "tdmax", fontName="Helvetica", fontSize=8,
                textColor=GRAY_DARK, alignment=TA_CENTER)),
        ]
        data.append(row)

    tbl = Table(data, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, GRAY_LIGHT]),
        ("BOX",           (0, 0), (-1, -1), 0.5, GRAY_BORDER),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, GRAY_BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 8 * mm))

    # Top errores
    if top_errors:
        story.append(Paragraph("Top Errores", styles["section"]))
        story.append(Spacer(1, 3 * mm))

        err_headers = ["Sampler", "HTTP Code", "Ocurrencias"]
        err_col_w = [w_content * 0.55, w_content * 0.20, w_content * 0.25]
        err_header_row = [Paragraph(f"<b>{h}</b>", ParagraphStyle(
            "eth", fontName="Helvetica-Bold", fontSize=8,
            textColor=GRAY_DARK, alignment=TA_CENTER)) for h in err_headers]

        err_data = [err_header_row]
        for e in top_errors:
            err_data.append([
                Paragraph(e["sampler"], ParagraphStyle(
                    "etd", fontName="Helvetica", fontSize=8, textColor=RED_FAIL)),
                Paragraph(e["code"], ParagraphStyle(
                    "etdc", fontName="Helvetica-Bold", fontSize=8,
                    textColor=RED_FAIL, alignment=TA_CENTER)),
                Paragraph(str(e["count"]), ParagraphStyle(
                    "etdn", fontName="Helvetica", fontSize=8,
                    textColor=GRAY_DARK, alignment=TA_CENTER)),
            ])

        err_tbl = Table(err_data, colWidths=err_col_w, repeatRows=1)
        err_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), RED_BG),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, RED_BG]),
            ("BOX",           (0, 0), (-1, -1), 0.5, GRAY_BORDER),
            ("INNERGRID",     (0, 0), (-1, -1), 0.3, GRAY_BORDER),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ]))
        story.append(err_tbl)

    return story


# ─── Entry point ──────────────────────────────────────────────────────────────
def generate_report(results_path, output_path, api_name="API",
                    threads=1000, loops=30,
                    api_version=None, repo_url=None,
                    author=None, banner=None):
    stats, samplers, top_errors = parse_jtl(results_path)

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=HEADER_H + 6 * mm, bottomMargin=FOOTER_H + 8 * mm,
        title=f"Informe de Prueba de Rendimiento — {api_name}",
        author="aiquaa — https://aiquaa.com/",
    )

    styles  = build_styles()
    on_page = ReportCanvas(author=author)

    story  = build_cover(stats, samplers, styles, api_name, threads, loops,
                         api_version=api_version, repo_url=repo_url,
                         author=author, banner=banner)
    story += build_sampler_detail(samplers, top_errors, styles)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

    verdict_text, _ = get_verdict(stats)
    print(f"Reporte: {output_path}")
    print(f"  Requests  : {threads * loops:,} ({threads} threads x {loops} loops)")
    print(f"  Throughput: {stats['throughput']} req/seg")
    print(f"  Avg       : {stats['avg']} ms")
    print(f"  P95       : {stats['p95']} ms")
    print(f"  Error rate: {stats['error_rate']}%")
    print(f"  Veredicto : {verdict_text}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JMeter PDF Report — aiquaa.com")
    parser.add_argument("--results",     required=True, help="Archivo .jtl de JMeter")
    parser.add_argument("--output",      default=None,  help="Nombre del PDF de salida")
    parser.add_argument("--api-name",    default="API", help="Nombre de la API")
    parser.add_argument("--threads",     type=int, default=1000, help="Threads usados")
    parser.add_argument("--loops",       type=int, default=30,   help="Loops por thread")
    parser.add_argument("--api-version", default=None, help="Versión de la API")
    parser.add_argument("--repo-url",    default=None, help="URL del repositorio")
    parser.add_argument("--author",      default=None, help="Autor de la prueba")
    parser.add_argument("--banner",      default=None, help="Imagen de portada (opcional)")
    args = parser.parse_args()

    output_path = args.output
    if not output_path:
        slug = re.sub(r"[^A-Z0-9]+", "_", args.api_name.upper()).strip("_")
        output_path = f"INFORME_PERF_{slug}.pdf"

    generate_report(
        results_path=args.results,
        output_path=output_path,
        api_name=args.api_name,
        threads=args.threads,
        loops=args.loops,
        api_version=args.api_version,
        repo_url=args.repo_url,
        author=args.author,
        banner=args.banner,
    )
