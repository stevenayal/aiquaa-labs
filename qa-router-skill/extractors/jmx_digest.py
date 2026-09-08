#!/usr/bin/env python3
"""Plan JMeter .jmx (XML verboso) → estructura del plan. Tier 0.

Uso: jmx_digest.py <plan.jmx>
"""
import sys
import time
import xml.etree.ElementTree as ET

from _common import check_file, emit, fail, footer, now_iso, truncate

ASSERTION_TAGS = {
    "ResponseAssertion": "response", "JSONPathAssertion": "jsonpath",
    "DurationAssertion": "duration", "SizeAssertion": "size",
    "XPathAssertion": "xpath", "JSR223Assertion": "jsr223",
}


def sprop(el, name, default=""):
    for tag in ("stringProp", "intProp", "longProp", "boolProp"):
        node = el.find(f"./{tag}[@name='{name}']")
        if node is not None:
            return (node.text or "").strip() or default
    return default


def main(argv):
    if len(argv) < 2:
        fail(__doc__, 2)
    path = argv[1]
    started = time.time()
    raw = check_file(path)
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        fail(f"'{path}' no es XML válido ({exc})")
    if root.tag != "jmeterTestPlan":
        fail(f"'{path}' no es un plan JMeter (raíz <{root.tag}>)")

    plan = root.find(".//TestPlan")
    plan_name = plan.get("testname", "?") if plan is not None else "?"

    variables = []
    for arg in root.iter("elementProp"):
        if arg.get("elementType") != "Argument":
            continue
        name = sprop(arg, "Argument.name")
        value = sprop(arg, "Argument.value")
        if name:
            variables.append((name, truncate(value, 60)))

    groups = []
    for tag in ("ThreadGroup", "SetupThreadGroup", "PostThreadGroup",
                "kg.apc.jmeter.threads.SteppingThreadGroup"):
        for tg in root.iter(tag):
            groups.append((
                tg.get("testname", "?"),
                sprop(tg, "ThreadGroup.num_threads", "?"),
                sprop(tg, "ThreadGroup.ramp_time", "?"),
                sprop(tg, "ThreadGroup.duration", "-"),
                tg.get("enabled", "true"),
            ))

    samplers = []
    for s in root.iter("HTTPSamplerProxy"):
        samplers.append((
            s.get("testname", "?"),
            sprop(s, "HTTPSampler.method", "?"),
            sprop(s, "HTTPSampler.path", "?"),
            s.get("enabled", "true"),
        ))

    assertions = {}
    for tag, label in ASSERTION_TAGS.items():
        n = sum(1 for _ in root.iter(tag))
        if n:
            assertions[label] = n

    datasets = [(d.get("testname", "?"), sprop(d, "filename", "?"))
                for d in root.iter("CSVDataSet")]
    writers = [sprop(w, "filename", "?") for w in root.iter("ResultCollector")
               if sprop(w, "filename")]

    lines = [
        f"JMX · {plan_name} · {now_iso()}",
        f"ESTRUCTURA: {len(groups)} thread group(s) · {len(samplers)} sampler(s) · "
        f"{sum(assertions.values())} assertion(s) · {len(variables)} variable(s)",
    ]
    if variables:
        lines.append("VARIABLES:")
        lines += [f"  {n} = {v}" for n, v in variables]
    lines.append("THREAD GROUPS:")
    for name, threads, ramp, dur, enabled in groups:
        off = "" if enabled == "true" else " [DESHABILITADO]"
        lines.append(f"  {name} · threads={threads} · rampup={ramp}s · duration={dur}{off}")
    lines.append("SAMPLERS:")
    for name, method, sp, enabled in samplers:
        off = "" if enabled == "true" else " [DESHABILITADO]"
        lines.append(f"  {method} {sp} · \"{name}\"{off}")
    if assertions:
        lines.append("ASSERTIONS: " + " · ".join(f"{k}×{v}" for k, v in assertions.items()))
    else:
        lines.append("ASSERTIONS: ninguna — el plan no valida respuestas")
    if datasets:
        lines.append("CSV DATA SET: " + " · ".join(f"{n} → {f}" for n, f in datasets))
    if writers:
        lines.append("SALIDA: " + " · ".join(writers))
    lines.append(footer(path, raw))
    emit(lines, raw, "jmx", path, started)


if __name__ == "__main__":
    main(sys.argv)
