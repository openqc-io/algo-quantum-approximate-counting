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
