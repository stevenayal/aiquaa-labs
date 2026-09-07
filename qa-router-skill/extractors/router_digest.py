#!/usr/bin/env python3
"""Dispatcher del qa-router: detecta el tipo de artefacto y corre su extractor.

Uso: router_digest.py <archivo> [opciones del extractor...]
     router_digest.py --list          lista los tipos soportados

Salida 3 = tipo no reconocido → el router debe delegar a tier 1 (qa-bulk-reader).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# (nombre, matcher por nombre de archivo, extractor)
BY_NAME = [
    ("jmeter-jtl", lambda n: n.endswith((".jtl",)), "jtl_digest.py"),
    ("jmx", lambda n: n.endswith(".jmx"), "jmx_digest.py"),
    ("postman-collection", lambda n: n.endswith("postman_collection.json"),
     "collection_digest.py"),
    ("junit/nunit", lambda n: n.endswith(".xml"), "junit_digest.py"),
    ("har", lambda n: n.endswith(".har"), None),
]


def sniff_json(path):
    """Distingue los JSON entre sí leyendo solo las claves de primer nivel."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    keys = set(data.keys())
    if "run" in keys and "collection" in keys:
        return "newman_digest.py"
    if {"info", "item"} <= keys:
        return "collection_digest.py"
    if "suites" in keys and ("config" in keys or "stats" in keys):
        return "pw_digest.py"
    if "paths" in keys and ("openapi" in keys or "swagger" in keys):
        return "openapi_digest.py"
    if keys & {"pullRequests", "resultsByTest", "value", "runs", "workItems"}:
        return "az_digest.py"
    return None


def detect(path):
    name = os.path.basename(path).lower()
    for label, match, script in BY_NAME:
        if match(name):
            if script is None:
                return None, label
            return script, label
    if name.endswith(".json"):
        script = sniff_json(path)
        return script, "json"
    if name.endswith((".csv", ".tsv")) and "jtl" in name:
        return "jtl_digest.py", "jmeter-jtl"
    return None, "desconocido"


def main(argv):
    if "--list" in argv:
        print("Tipos soportados por el dispatcher:")
        print("  .jtl / *jtl*.csv        → jtl_digest.py")
        print("  .jmx                    → jmx_digest.py")
        print("  .xml (JUnit / NUnit3)   → junit_digest.py")
        print("  newman JSON             → newman_digest.py")
        print("  colección Postman v2.1  → collection_digest.py")
        print("  reporte JSON Playwright → pw_digest.py")
        print("  OpenAPI JSON            → openapi_digest.py")
        print("  payload Azure DevOps    → az_digest.py")
        print("  diff de PR              → diff_digest.sh (no pasa por este dispatcher)")
        return 0
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2

    path = argv[1]
    if not os.path.isfile(path):
        print(f"qa-router: no existe el archivo '{path}'", file=sys.stderr)
        return 2

    script, label = detect(path)
    if script is None:
        size = os.path.getsize(path)
        print(f"qa-router: '{path}' ({label}, {size} B) no tiene extractor tier 0.",
              file=sys.stderr)
        print("qa-router: delegá a tier 1 — subagente qa-bulk-reader.", file=sys.stderr)
        return 3

    return subprocess.call([sys.executable, os.path.join(HERE, script), path] + argv[2:])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
