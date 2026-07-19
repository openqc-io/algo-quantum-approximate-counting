"""Ported from the in-image builtin registry (was added during
the enrichment phase; this file finishes the migration to a standalone
openqc-io/algo-* repo so the algorithm lives in the catalog like every
other one).

Sandbox: no imports — all logic is pure dict construction on Python
built-ins. See vortex_common.algorithm_executor.validate_template_ast
for the full rule set.
"""


class AlgorithmTemplate:

    def build(self, input_data, ctx):
        backend = ctx.get("backend", "auto") if isinstance(ctx, dict) else "auto"
        return {
            "type": "circuit",
            "backend_id": backend,
            "provider": "vortex",
            "qasm": _build_counting_circuit(
                input_data.get("search_space_bits", 3),
                input_data.get("precision_bits", 3),
                input_data.get("num_marked", 2),
            ),
            "shots": 4096,
        }

    def interpret(self, raw_result, input_data):
        result = raw_result
        return {
            "estimated_count": _estimate_count_from_result(
                result, input_data.get("search_space_bits", 3), input_data.get("precision_bits", 3),
            ),
            "actual_count": input_data.get("num_marked", 2),
            "search_space_size": 2 ** input_data.get("search_space_bits", 3),
        }


# ── helpers restored from the retired in-image builtin registry (18187b8^) ──


def _build_counting_circuit(
    search_bits: int = 3, precision_bits: int = 3, num_marked: int = 2,
) -> str:
    """Build quantum approximate counting circuit (QPE + Grover operator)."""
    total = search_bits + precision_bits
    lines = [
        "OPENQASM 2.0;",
        'include "qelib1.inc";',
        f"qreg q[{total}];",
        f"creg c[{precision_bits}];",
        "// Initialize search register in superposition",
    ]
    for i in range(search_bits):
        lines.append(f"h q[{precision_bits + i}];")
    lines.append("// Initialize precision register")
    for i in range(precision_bits):
        lines.append(f"h q[{i}];")
    # Controlled Grover iterations (simplified)
    for p in range(precision_bits):
        power = 2 ** p
        lines.append(f"// Controlled-G^{power} on precision qubit {p}")
        for _ in range(min(power, 4)):  # cap for circuit size
            # Simplified oracle + diffusion
            for s in range(min(num_marked, search_bits)):
                lines.append(f"cz q[{p}],q[{precision_bits + s}];")
            # Diffusion
            for s in range(search_bits):
                lines.append(f"h q[{precision_bits + s}];")
                lines.append(f"x q[{precision_bits + s}];")
            if search_bits >= 2:
                lines.append(f"cz q[{precision_bits}],q[{precision_bits + 1}];")
            for s in range(search_bits):
                lines.append(f"x q[{precision_bits + s}];")
                lines.append(f"h q[{precision_bits + s}];")
    # Inverse QFT on precision register
    lines.append("// Inverse QFT")
    for i in range(precision_bits // 2):
        j = precision_bits - 1 - i
        lines.append(f"swap q[{i}],q[{j}];")
    for i in range(precision_bits):
        for j in range(i):
            lines.append(f"cp({-3.14159 / (2 ** (i - j))}) q[{j}],q[{i}];")
        lines.append(f"h q[{i}];")
    # Measure precision register
    for i in range(precision_bits):
        lines.append(f"measure q[{i}] -> c[{i}];")
    return "\n".join(lines)


def _estimate_count_from_result(
    result: dict, search_bits: int, precision_bits: int,
) -> float:
    """Estimate solution count from QPE measurement."""
    counts = result.get("counts", {})
    if not counts:
        return 0.0
    # Find most frequent outcome
    best = max(counts, key=lambda k: counts[k])
    # Convert to phase estimate
    phase_int = int(best, 2) if all(c in "01" for c in best) else 0
    theta = phase_int / (2 ** precision_bits)
    # N * sin^2(theta * pi / 2) estimates the count
    # (sandbox provides a `math` namespace object; imports are not allowed)
    n = 2 ** search_bits
    estimated = n * (math.sin(math.pi * theta) ** 2) if theta > 0 else 0
    return round(estimated, 1)
