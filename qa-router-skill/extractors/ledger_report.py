#!/usr/bin/env python3
"""Lee el ledger del qa-router y reporta el ahorro acumulado. Alimenta /router:costo.

Uso: ledger_report.py [ruta/ledger.jsonl] [--reset]

El ahorro en tokens es una **estimación** (bytes/4), no una medición del tokenizer.
Se reporta como tal — nunca como consumo real facturado.
"""
import json
import os
import sys
from collections import defaultdict

from _common import human_bytes


def default_path():
    return os.environ.get("QA_ROUTER_LEDGER") or os.path.join(
        os.getcwd(), ".qa-router", "ledger.jsonl")


def main(argv):
    path = next((a for a in argv[1:] if not a.startswith("--")), default_path())
    if "--reset" in argv:
        if os.path.isfile(path):
            os.remove(path)
            print(f"qa-router: ledger reiniciado ({path})")
        else:
            print(f"qa-router: no había ledger en {path}")
        return 0
    if not os.path.isfile(path):
        print(f"qa-router: sin ledger en {path} — no se digirió ningún artefacto todavía.")
        return 0

    by_kind = defaultdict(lambda: {"n": 0, "raw": 0, "digest": 0, "saved": 0})
    bad = 0
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                bad += 1
                continue
            k = by_kind[e.get("kind", "?")]
            k["n"] += 1
            k["raw"] += int(e.get("bytes_raw") or 0)
            k["digest"] += int(e.get("bytes_digest") or 0)
            k["saved"] += int(e.get("tokens_saved_est") or 0)

    if not by_kind:
        print(f"qa-router: ledger vacío ({path})")
        return 0

    tot_raw = sum(v["raw"] for v in by_kind.values())
    tot_dig = sum(v["digest"] for v in by_kind.values())
    tot_saved = sum(v["saved"] for v in by_kind.values())
    tot_n = sum(v["n"] for v in by_kind.values())

    print(f"QA-ROUTER · COSTO · {path}")
    print(f"{'ARTEFACTO':<20} {'N':>4} {'CRUDO':>10} {'DIGEST':>10} {'REDUCCIÓN':>10}")
    for kind, v in sorted(by_kind.items(), key=lambda kv: -kv[1]["raw"]):
        ratio = (1 - v["digest"] / v["raw"]) * 100 if v["raw"] else 0
        print(f"{kind:<20} {v['n']:>4} {human_bytes(v['raw']):>10} "
              f"{human_bytes(v['digest']):>10} {ratio:>9.1f}%")
    ratio = (1 - tot_dig / tot_raw) * 100 if tot_raw else 0
    print(f"{'TOTAL':<20} {tot_n:>4} {human_bytes(tot_raw):>10} "
          f"{human_bytes(tot_dig):>10} {ratio:>9.1f}%")
    print(f"\nTOKENS EVITADOS (est. bytes/4): ~{tot_saved:,} — estimación, no medición.")
    if bad:
        print(f"AVISO: {bad} línea(s) del ledger ilegibles, no contabilizadas.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
