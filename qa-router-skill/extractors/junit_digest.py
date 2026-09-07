#!/usr/bin/env python3
"""JUnit XML o NUnit3 XML → digest de fallos. Tier 0, parseo incremental.

Cubre: newman-reporter-junit, hurl --report-junit, Reqnroll/NUnit (flaui-skill).
Uso: junit_digest.py <archivo.xml>
"""
import sys
import time
import xml.etree.ElementTree as ET

from _common import (MAX_CLUSTERS, check_file, cluster, emit, fail, footer,
                     now_iso, truncate)


def parse(path):
    """Devuelve (formato, totales, fallos). Un solo recorrido del árbol."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        fail(f"'{path}' no es XML válido ({exc})")
    except OSError as exc:
        fail(f"no se pudo leer '{path}': {exc}", 2)

    if root.tag == "test-run" or root.find(".//test-case") is not None:
        return "nunit", *_nunit(root)
    if root.tag in ("testsuites", "testsuite"):
        return "junit", *_junit(root)
    fail(f"'{path}' no es JUnit ni NUnit3 (raíz <{root.tag}>)")


def _nunit(root):
    totals = {
        "total": root.get("total") or root.get("testcasecount") or "?",
        "passed": root.get("passed", "?"),
        "failed": root.get("failed", "?"),
        "skipped": root.get("skipped", "?"),
        "duration": root.get("duration", "?"),
    }
    fails = []
    for tc in root.iter("test-case"):
        if tc.get("result") not in ("Failed", "Error"):
            continue
        node = tc.find("failure")
        msg = node.findtext("message", "") if node is not None else ""
        trace = node.findtext("stack-trace", "") if node is not None else ""
        cat = ""
        for prop in tc.iter("property"):
            if prop.get("name") == "Category":
                cat = prop.get("value", "")
                break
        fails.append((tc.get("name", "?"), cat, truncate(msg),
                      truncate(trace.strip().splitlines()[0] if trace.strip() else "", 90)))
    return totals, fails


def _junit(root):
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    agg = {"total": 0, "failed": 0, "skipped": 0, "duration": 0.0}
    for s in suites:
        agg["total"] += int(s.get("tests") or 0)
        agg["failed"] += int(s.get("failures") or 0) + int(s.get("errors") or 0)
        agg["skipped"] += int(s.get("skipped") or 0)
        try:
            agg["duration"] += float(s.get("time") or 0)
        except ValueError:
            pass
    totals = {
        "total": agg["total"],
        "passed": agg["total"] - agg["failed"] - agg["skipped"],
        "failed": agg["failed"],
        "skipped": agg["skipped"],
        "duration": f"{agg['duration']:.2f}",
    }
    fails = []
    for tc in root.iter("testcase"):
        for node in list(tc.findall("failure")) + list(tc.findall("error")):
            msg = node.get("message") or (node.text or "")
            fails.append((tc.get("name", "?"), tc.get("classname", ""),
                          truncate(msg), truncate((node.text or "").strip(), 90)))
    return totals, fails


def main(argv):
    if len(argv) < 2:
        fail(__doc__, 2)
    path = argv[1]
    started = time.time()
    raw = check_file(path)
    fmt, totals, fails = parse(path)

    lines = [
        f"{fmt.upper()} · {path.split('/')[-1]} · {now_iso()}",
        f"TOTALES: {totals['total']} casos · {totals['passed']} ok · "
        f"{totals['failed']} fallos · {totals['skipped']} omitidos · {totals['duration']}s",
    ]
    if fails:
        lines.append(f"FALLOS ({len(fails)}):")
        groups = cluster(fails, key_fn=lambda f: f[2][:70])
        for _, count, ex in groups[:MAX_CLUSTERS]:
            name, ctx, msg, where = ex
            tag = f" [{ctx}]" if ctx else ""
            suffix = f" ×{count}" if count > 1 else ""
            lines.append(f"  {name}{tag} · {msg}{suffix}")
            if where:
                lines.append(f"      ↳ {where}")
        if len(groups) > MAX_CLUSTERS:
            rest = sum(c for _, c, _ in groups[MAX_CLUSTERS:])
            lines.append(f"  … {len(groups) - MAX_CLUSTERS} clusters más ({rest} fallos)")
    else:
        lines.append("FALLOS: ninguno")
    lines.append(footer(path, raw))
    emit(lines, raw, fmt, path, started)


if __name__ == "__main__":
    main(sys.argv)
