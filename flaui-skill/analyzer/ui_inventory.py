"""
ui_inventory.py v1 — Inventario de controles UI para pantallas C# (WinForms / WPF)
Powered by skill flaui · aiquaa.com

Evita que el agente invente AutomationId/selectores: parsea el código fuente real
de la pantalla (*.Designer.cs para WinForms, *.xaml para WPF) y devuelve, por
pantalla, la lista de controles con su AutomationId real y si es "estable"
(existe un identificador que sobrevive a rediseños de layout) o no.

Sin dependencias externas — solo stdlib (re, xml.etree, pathlib).

Uso:
    python ui_inventory.py --src ./src/MiApp --format json
    python ui_inventory.py --src ./src/MiApp --format md
    python ui_inventory.py --src ./src/MiApp --changed-files pr_files.txt --format json
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Windows redirige stdout con la codepage cp1252 por defecto: rompe con ✅/⚠️.
# Forzar UTF-8 (Python 3.7+) antes de emitir cualquier salida.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

# ─── WinForms ───────────────────────────────────────────────────────────────
# private System.Windows.Forms.TextBox txtUsuario;
WINFORMS_DECL_RE = re.compile(
    r"private\s+(?:System\.Windows\.Forms\.)?(?P<type>[A-Za-z_][\w<>]*)\s+"
    r"(?P<field>[A-Za-z_]\w*)\s*;"
)
# this.txtUsuario.Name = "txtUsuario";
WINFORMS_PROP_RE = re.compile(
    r'this\.(?P<field>[A-Za-z_]\w*)\.(?P<prop>Name|Text|AccessibleName)\s*=\s*'
    r'"(?P<value>[^"]*)"\s*;'
)

# Tipos de control WinForms reconocidos (evita matchear campos que no son controles)
WINFORMS_CONTROL_TYPES = {
    "Button", "TextBox", "Label", "ComboBox", "CheckBox", "RadioButton",
    "DataGridView", "ListBox", "ListView", "TreeView", "TabControl", "TabPage",
    "MenuStrip", "ToolStripMenuItem", "PictureBox", "GroupBox", "Panel",
    "NumericUpDown", "DateTimePicker", "MaskedTextBox", "RichTextBox",
    "ProgressBar", "TrackBar", "LinkLabel", "ToolStrip", "ToolStripButton",
    "StatusStrip", "SplitContainer", "MdiClient",
}

# ─── WPF ────────────────────────────────────────────────────────────────────
WPF_CONTROL_TAGS = {
    "Button", "TextBox", "Label", "ComboBox", "CheckBox", "RadioButton",
    "DataGrid", "ListBox", "ListView", "TreeView", "TabControl", "TabItem",
    "Menu", "MenuItem", "Image", "GroupBox", "Grid", "StackPanel",
    "PasswordBox", "DatePicker", "RichTextBox", "ProgressBar", "Slider",
    "Hyperlink", "ToolBar", "Expander", "Border",
}

XAML_NS = {"x": "http://schemas.microsoft.com/winfx/2006/xaml"}
AUTOMATION_ID_ATTR = "{http://schemas.microsoft.com/winfx/2006/xaml/presentation}AutomationId"


def strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def analyze_winforms(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    screen = path.stem.replace(".Designer", "")

    fields = {}
    for m in WINFORMS_DECL_RE.finditer(text):
        ftype = m.group("type")
        if ftype not in WINFORMS_CONTROL_TYPES:
            continue
        fields[m.group("field")] = {
            "field": m.group("field"),
            "type": ftype,
            "automationId": None,
            "text": None,
            "accessibleName": None,
        }

    for m in WINFORMS_PROP_RE.finditer(text):
        field = m.group("field")
        if field not in fields:
            continue
        prop, value = m.group("prop"), m.group("value")
        if prop == "Name":
            fields[field]["automationId"] = value
        elif prop == "Text":
            fields[field]["text"] = value
        elif prop == "AccessibleName":
            fields[field]["accessibleName"] = value

    controls = []
    warnings = []
    for f in fields.values():
        # WinForms: Control.Name se expone como AutomationId vía UIA por defecto.
        # Si no hay Name explícito, cae al nombre de campo autogenerado (inestable
        # frente a renombrados desde el Designer) -> lo marcamos no estable.
        automation_id = f["automationId"] or f["field"]
        stable = bool(f["automationId"]) or bool(f["accessibleName"])
        c = {
            "field": f["field"],
            "type": f["type"],
            "automationId": automation_id,
            "text": f["text"],
            "stable": stable,
        }
        controls.append(c)
        if not stable:
            warnings.append(
                f'{f["field"]} ({f["type"]}) sin Name/AccessibleName explícito — '
                f'AutomationId cae al campo autogenerado "{automation_id}", frágil '
                f'ante refactors del Designer. Recomendado: this.{f["field"]}.AccessibleName = "{f["field"]}";'
            )

    return {
        "screen": screen,
        "file": str(path),
        "kind": "winforms",
        "controls": sorted(controls, key=lambda c: c["field"]),
        "warnings": warnings,
    }


def analyze_wpf(path: Path) -> dict:
    screen = path.stem
    controls = []
    warnings = []
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return {
            "screen": screen, "file": str(path), "kind": "wpf",
            "controls": [], "warnings": [f"XAML inválido, no se pudo parsear: {e}"],
        }

    for elem in tree.iter():
        tag = strip_ns(elem.tag)
        if tag not in WPF_CONTROL_TAGS:
            continue

        x_name = elem.attrib.get("{http://schemas.microsoft.com/winfx/2006/xaml}Name")
        automation_id = elem.attrib.get(AUTOMATION_ID_ATTR) or elem.attrib.get("AutomationProperties.AutomationId")
        automation_name = elem.attrib.get("AutomationProperties.Name")
        content = elem.attrib.get("Content") or elem.attrib.get("Header")

        if not (x_name or automation_id or automation_name or content):
            continue  # elemento sin ningún identificador ni contenido -> ruido de layout

        resolved_id = automation_id or x_name
        stable = bool(automation_id) or bool(x_name)
        field = x_name or automation_id or f"<sin x:Name>"

        c = {
            "field": field,
            "type": tag,
            "automationId": resolved_id,
            "text": content or automation_name,
            "stable": stable,
        }
        controls.append(c)
        if not stable:
            warnings.append(
                f'{tag} con Content/Header "{content or automation_name}" sin x:Name ni '
                f'AutomationProperties.AutomationId — no localizable de forma estable. '
                f'Recomendado: agregar x:Name="..." o AutomationProperties.AutomationId="...".'
            )
        elif not automation_id and x_name:
            warnings.append(
                f'{field} ({tag}) usa solo x:Name (no expuesto por UIA por defecto en todos los '
                f'controles). Recomendado: AutomationProperties.AutomationId="{x_name}" explícito.'
            )

    return {
        "screen": screen,
        "file": str(path),
        "kind": "wpf",
        "controls": sorted(controls, key=lambda c: c["field"]),
        "warnings": warnings,
    }


def discover_files(src: Path, changed_only: set | None) -> tuple[list[Path], list[Path]]:
    winforms_files = list(src.rglob("*.Designer.cs"))
    wpf_files = list(src.rglob("*.xaml"))
    wpf_files = [f for f in wpf_files if f.name != "App.xaml"]

    if changed_only is not None:
        def matches(f: Path) -> bool:
            fs = str(f).replace("\\", "/")
            return any(fs.endswith(c.replace("\\", "/")) for c in changed_only)
        winforms_files = [f for f in winforms_files if matches(f)]
        wpf_files = [f for f in wpf_files if matches(f)]

    return winforms_files, wpf_files


def render_markdown(results: list[dict]) -> str:
    lines = ["# Inventario de controles UI", ""]
    for r in results:
        lines.append(f"## {r['screen']} ({r['kind']}) — `{r['file']}`")
        lines.append("")
        lines.append("| Campo | Tipo | AutomationId | Texto | Estable |")
        lines.append("|---|---|---|---|---|")
        for c in r["controls"]:
            estable = "✅" if c["stable"] else "⚠️"
            lines.append(
                f'| {c["field"]} | {c["type"]} | `{c["automationId"]}` | '
                f'{c["text"] or ""} | {estable} |'
            )
        if r["warnings"]:
            lines.append("")
            lines.append("**Advertencias:**")
            for w in r["warnings"]:
                lines.append(f"- ⚠️ {w}")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Inventario de controles UI (WinForms/WPF) — skill flaui · aiquaa.com")
    parser.add_argument("--src", required=True, help="Carpeta raíz del código fuente C# de la app")
    parser.add_argument("--changed-files", default=None,
                         help="Archivo con lista de rutas (una por línea) para limitar el análisis, "
                              "ej: salida de 'gh pr diff --name-only'")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    args = parser.parse_args()

    src = Path(args.src)
    if not src.exists():
        print(f"ERROR: no existe la ruta --src {src}", file=sys.stderr)
        sys.exit(1)

    changed = None
    if args.changed_files:
        changed_path = Path(args.changed_files)
        if not changed_path.exists():
            print(f"ERROR: no existe --changed-files {changed_path}", file=sys.stderr)
            sys.exit(1)
        changed = {
            line.strip() for line in changed_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }

    winforms_files, wpf_files = discover_files(src, changed)

    if not winforms_files and not wpf_files:
        print(f"AVISO: no se encontraron *.Designer.cs ni *.xaml bajo {src}"
              + (" (con el filtro de --changed-files aplicado)" if changed is not None else ""),
              file=sys.stderr)

    results = [analyze_winforms(f) for f in winforms_files] + [analyze_wpf(f) for f in wpf_files]
    results.sort(key=lambda r: r["screen"])

    if args.format == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(render_markdown(results))

    total_warnings = sum(len(r["warnings"]) for r in results)
    if total_warnings:
        print(f"\n{total_warnings} advertencia(s) — controles sin AutomationId estable.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
