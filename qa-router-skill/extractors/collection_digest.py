#!/usr/bin/env python3
"""Colección Postman v2.1 → árbol de requests + nombres de tests. Tier 0.

Uso: collection_digest.py <coleccion.json> [--tests]
     --tests  lista el nombre de cada pm.test() por request
"""
import re
import sys
import time

from _common import check_file, emit, fail, footer, load_json, now_iso

TEST_RE = re.compile(r"""pm\.test\(\s*['"`](.+?)['"`]""")


def url_of(request):
    if isinstance(request, str):
        return request
    url = (request or {}).get("url")
    if isinstance(url, str):
        return url
    if isinstance(url, dict):
        return url.get("raw") or "/" + "/".join(str(p) for p in url.get("path") or [])
    return ""


def tests_of(item):
    names = []
    for ev in item.get("event") or []:
        if ev.get("listen") != "test":
            continue
        script = (ev.get("script") or {}).get("exec") or []
        body = "\n".join(script) if isinstance(script, list) else str(script)
        names += TEST_RE.findall(body)
    return names


def walk(items, depth, out, counters, show_tests):
    for item in items or []:
        if "item" in item:
            out.append(f"{'  ' * depth}{item.get('name', '?')}/")
            counters["folders"] += 1
            walk(item["item"], depth + 1, out, counters, show_tests)
            continue
        req = item.get("request") or {}
        method = req.get("method", "?") if isinstance(req, dict) else "?"
        names = tests_of(item)
        counters["requests"] += 1
        counters["tests"] += len(names)
        if not names:
            counters["sin_tests"].append(item.get("name", "?"))
        out.append(f"{'  ' * depth}{method} {url_of(req)} · \"{item.get('name', '?')}\" "
                   f"· {len(names)} test(s)")
        if show_tests:
            out += [f"{'  ' * (depth + 1)}– {n}" for n in names]


def main(argv):
    if len(argv) < 2:
        fail(__doc__, 2)
    path = argv[1]
    show_tests = "--tests" in argv[2:]
    started = time.time()
    raw = check_file(path)
    data = load_json(path)
    if "item" not in data or "info" not in data:
        fail(f"'{path}' no parece una colección Postman v2.1 (faltan 'info'/'item')")

    tree, counters = [], {"folders": 0, "requests": 0, "tests": 0, "sin_tests": []}
    walk(data["item"], 1, tree, counters, show_tests)

    lines = [
        f"POSTMAN · {data['info'].get('name', '?')} · {now_iso()}",
        f"ESTRUCTURA: {counters['folders']} carpeta(s) · {counters['requests']} request(s) "
        f"· {counters['tests']} test(s)",
        "ÁRBOL:",
    ] + tree
    if counters["sin_tests"]:
        lines.append(f"SIN TESTS ({len(counters['sin_tests'])}): "
                     + ", ".join(counters["sin_tests"][:10])
                     + (" …" if len(counters["sin_tests"]) > 10 else ""))
    lines.append(footer(path, raw))
    emit(lines, raw, "postman-collection", path, started)


if __name__ == "__main__":
    main(sys.argv)
