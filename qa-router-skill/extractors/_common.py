"""Helpers compartidos por los extractores tier 0 del qa-router.

Sin dependencias externas — solo stdlib. Todo extractor:
  - escribe el digest en stdout,
  - registra el ahorro en el ledger (.qa-router/ledger.jsonl),
  - sale 0 si pudo parsear, 3 si el formato no era el esperado (el router
    entonces cae a tier 1), 2 si el uso fue incorrecto.

Regla dura: un digest parcial nunca se devuelve como si fuera completo.
Si el parseo falla a mitad de camino, se sale 3 con el motivo en stderr.
"""
import json
import os
import sys
import time
from datetime import datetime, timezone

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_UNPARSEABLE = 3

# Cuántos clusters de fallo se imprimen. Los clusters cubren el 100% de los
# fallos (cada uno lleva su conteo); este tope limita la variedad, no el total.
MAX_CLUSTERS = int(os.environ.get("QA_ROUTER_MAX_CLUSTERS", "12"))
MAX_ROWS = int(os.environ.get("QA_ROUTER_MAX_ROWS", "15"))


def fail(msg, code=EXIT_UNPARSEABLE):
    """Falla ruidoso. Nunca devuelve un digest a medias."""
    print(f"qa-router: {msg}", file=sys.stderr)
    if code == EXIT_UNPARSEABLE:
        print("qa-router: formato no reconocido — delegá a tier 1 (qa-bulk-reader).",
              file=sys.stderr)
    sys.exit(code)


def check_file(path):
    if not os.path.isfile(path):
        fail(f"no existe el archivo '{path}'", EXIT_USAGE)
    return os.path.getsize(path)


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def human_bytes(n):
    n = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{int(n)} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} GB"


def truncate(text, limit=160):
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def percentile(sorted_vals, q):
    """Percentil por interpolación lineal. sorted_vals: secuencia ordenada."""
    n = len(sorted_vals)
    if n == 0:
        return 0.0
    if n == 1:
        return float(sorted_vals[0])
    pos = (n - 1) * q
    lo = int(pos)
    hi = min(lo + 1, n - 1)
    frac = pos - lo
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * frac


def cluster(items, key_fn):
    """Agrupa fallos por firma. Devuelve [(clave, conteo, ejemplo)] desc por conteo."""
    buckets = {}
    for it in items:
        k = key_fn(it)
        if k in buckets:
            buckets[k][0] += 1
        else:
            buckets[k] = [1, it]
    out = [(k, v[0], v[1]) for k, v in buckets.items()]
    out.sort(key=lambda t: -t[1])
    return out


def emit(lines, raw_bytes, kind, source, started=None):
    """Imprime el digest y registra el ahorro."""
    body = "\n".join(str(x) for x in lines if x is not None)
    sys.stdout.write(body + "\n")
    record_ledger(kind, source, raw_bytes, len(body.encode("utf-8")), started)


def record_ledger(kind, source, raw_bytes, digest_bytes, started=None):
    """Anota una línea en el ledger. Nunca rompe el extractor si falla."""
    dest = os.environ.get("QA_ROUTER_LEDGER", "")
    if dest == "off":
        return
    if not dest:
        dest = os.path.join(os.getcwd(), ".qa-router", "ledger.jsonl")
    entry = {
        "ts": now_iso(),
        "tier": 0,
        "kind": kind,
        "source": os.path.basename(source),
        "bytes_raw": raw_bytes,
        "bytes_digest": digest_bytes,
        "ratio": round(1 - (digest_bytes / raw_bytes), 4) if raw_bytes else 0.0,
        # Aproximación declarada: ~4 bytes por token. No es una medición real.
        "tokens_saved_est": max(0, (raw_bytes - digest_bytes) // 4),
    }
    if started is not None:
        entry["ms"] = int((time.time() - started) * 1000)
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as exc:  # ledger es telemetría, no puede tumbar el digest
        print(f"qa-router: ledger no escrito ({exc})", file=sys.stderr)


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        fail(f"'{path}' no es JSON válido ({exc.msg}, línea {exc.lineno})")
    except OSError as exc:
        fail(f"no se pudo leer '{path}': {exc}", EXIT_USAGE)


def footer(path, raw_bytes):
    return f"CRUDO: {path} ({human_bytes(raw_bytes)})"
