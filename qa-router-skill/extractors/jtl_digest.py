#!/usr/bin/env python3
"""JMeter .jtl/CSV → métricas agregadas. Tier 0, streaming, memoria O(4 bytes/fila).

Uso: jtl_digest.py <archivo.jtl> [--top N] [--baseline <archivo.jtl>]
"""
import csv
import sys
import time
from array import array
from collections import defaultdict

from _common import (MAX_CLUSTERS, check_file, emit, fail, footer, now_iso,
                     percentile, truncate)

REQUIRED = {"elapsed", "label", "success"}


def scan(path):
    """Recorre el .jtl una sola vez. Nunca carga el archivo entero en memoria."""
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
        head = fh.read(1)
        if head == "<":
            fail(f"'{path}' es un .jtl en formato XML. Reconfigurá el Simple Data "
                 f"Writer a CSV (ver jmeter-skill) o convertilo antes de digerir.")
        fh.seek(0)
        reader = csv.DictReader(fh)
        if not reader.fieldnames or not REQUIRED.issubset(set(reader.fieldnames)):
            fail(f"'{path}' no tiene las columnas requeridas {sorted(REQUIRED)} "
                 f"(encontradas: {reader.fieldnames})")
        per_label = defaultdict(lambda: array("l"))
        errors = defaultdict(int)
        err_msgs = {}
        total = 0
        failed = 0
        t_min = t_max = None
        for row in reader:
            try:
                elapsed = int(float(row["elapsed"]))
            except (TypeError, ValueError):
                continue
            total += 1
            label = row["label"] or "?"
            per_label[label].append(elapsed)
            ok = str(row["success"]).strip().lower() == "true"
            if not ok:
                failed += 1
                code = row.get("responseCode") or "?"
                errors[(label, code)] += 1
                err_msgs.setdefault((label, code),
                                    truncate(row.get("failureMessage")
                                             or row.get("responseMessage") or "", 80))
            ts = row.get("timeStamp")
            if ts and ts.isdigit():
                ts = int(ts)
                t_min = ts if t_min is None else min(t_min, ts)
                t_max = ts if t_max is None else max(t_max, ts)
    if total == 0:
        fail(f"'{path}' no tiene filas de muestra")
    return per_label, errors, err_msgs, total, failed, t_min, t_max


def overall_stats(per_label):
    everything = array("l")
    for vals in per_label.values():
        everything.extend(vals)
    ordered = sorted(everything)
    return ordered


def main(argv):
    if len(argv) < 2:
        fail(__doc__, 2)
    path = argv[1]
    top_n = MAX_CLUSTERS
    baseline = None
    args = argv[2:]
    for i, a in enumerate(args):
        if a == "--top" and i + 1 < len(args):
            top_n = int(args[i + 1])
        if a == "--baseline" and i + 1 < len(args):
            baseline = args[i + 1]

    started = time.time()
    raw = check_file(path)
    per_label, errors, err_msgs, total, failed, t_min, t_max = scan(path)
    ordered = overall_stats(per_label)

    dur = (t_max - t_min) / 1000.0 if (t_min is not None and t_max and t_max > t_min) else 0.0
    err_pct = 100.0 * failed / total
    lines = [
        f"JMETER · {path.split('/')[-1]} · {now_iso()}",
        f"MUESTRAS: {total} · errores {failed} ({err_pct:.2f}%) · "
        f"duración {dur:.0f}s · throughput {total/dur:.1f}/s" if dur else
        f"MUESTRAS: {total} · errores {failed} ({err_pct:.2f}%)",
        f"LATENCIA (ms): p50 {percentile(ordered, .50):.0f} · "
        f"p90 {percentile(ordered, .90):.0f} · p95 {percentile(ordered, .95):.0f} · "
        f"p99 {percentile(ordered, .99):.0f} · max {ordered[-1]}",
    ]

    rank = sorted(per_label.items(), key=lambda kv: -percentile(sorted(kv[1]), .95))
    lines.append(f"TOP {min(top_n, len(rank))} SAMPLERS POR p95:")
    for label, vals in rank[:top_n]:
        s = sorted(vals)
        lines.append(f"  {label} · n={len(s)} · p95 {percentile(s, .95):.0f}ms · "
                     f"p99 {percentile(s, .99):.0f}ms · max {s[-1]}ms")

    if errors:
        lines.append(f"ERRORES ({failed} en {len(errors)} clusters):")
        for (label, code), count in sorted(errors.items(), key=lambda kv: -kv[1])[:top_n]:
            msg = err_msgs.get((label, code), "")
            lines.append(f"  {label} · {code} · ×{count}" + (f" · {msg}" if msg else ""))
    else:
        lines.append("ERRORES: ninguno")

    if baseline:
        try:
            b_label, _, _, b_total, b_failed, _, _ = scan(baseline)
            b_ordered = overall_stats(b_label)
            d95 = percentile(ordered, .95) - percentile(b_ordered, .95)
            sign = "+" if d95 >= 0 else ""
            lines.append(
                f"VS BASELINE ({baseline.split('/')[-1]}): p95 {sign}{d95:.0f}ms · "
                f"errores {100*b_failed/b_total:.2f}% → {err_pct:.2f}%")
        except SystemExit:
            lines.append(f"VS BASELINE: no se pudo leer '{baseline}'")

    lines.append(footer(path, raw))
    emit(lines, raw, "jmeter-jtl", path, started)


if __name__ == "__main__":
    main(sys.argv)
