# Quantum Approximate Counting

Estimate the number of solutions to a search problem using Grover iterations combined with quantum phase estimation.

## Provenance

This algorithm was ported from the in-image builtin registry in
`vortex-common/vortex_common/algorithm_executor.py` during the
M-DoD-B (Migration Done) phase. The algorithm itself is unchanged;
it now lives in this standalone repo so it ingests through the
canonical catalog sync pipeline (algorithm.json + template.py at a
pinned commit), like every other algorithm.

## Input

```json
{
  "type": "object",
  "required": [],
  "properties": {
    "search_space_bits": {
      "type": "integer",
      "description": "Search space qubits (default 3)"
    },
    "precision_bits": {
      "type": "integer",
      "description": "QPE precision qubits (default 3)"
    },
    "num_marked": {
      "type": "integer",
      "description": "Number of marked items (default 2)"
    }
  }
}
```

## Output

```json
{
  "type": "object",
  "properties": {
    "estimated_count": {
      "type": "number"
    },
    "actual_count": {
      "type": "number"
    },
    "search_space_size": {
      "type": "number"
    }
  }
}
```

## License

Apache-2.0 — see [LICENSE](./LICENSE).
