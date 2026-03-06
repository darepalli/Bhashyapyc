
## Reverse translation modes
- `--reverse` (token-based): preserves **comments & strings**; replaces only tokenized names/keywords. May translate user-defined identifiers named like builtins.
- `--reverse-ast` (AST-aware): **semantic** mapping using Python `ast`; avoids translating shadowed names like a local variable named `print`. Drops comments but keeps string literals intact.

### Examples
```bash
# Token-based Python → Telugu
python -m bhashyapyc examples/py_hello.py --reverse --lang te --emit-src out_te.tepy

# AST-aware Python → Sanskrit (avoids shadowed builtins)
python -m bhashyapyc examples/py_fib.py --reverse-ast --lang sa --emit-src out_sa.sa
```



### Source maps for AST reverse
When using `--reverse-ast`, you can also emit a JSON source map aligning output lines/columns to the original Python positions.

**Example:**
```bash
python -m bhashyapyc examples/py_fib.py   --reverse-ast --lang sa   --emit-src out_sa.sa   --emit-map out_sa.sa.map.json
```
The map looks like:
```json
{
  "version": 1,
  "source_name": "examples/py_fib.py",
  "language": "sa",
  "mappings": [
    {"out_line": 1, "out_col": 1, "py_line": 1, "py_col": 1, "role": "stmt:FunctionDef", "node": "FunctionDef"},
    {"out_line": 2, "out_col": 1, "py_line": 2, "py_col": 5, "role": "stmt:If", "node": "If"}
  ]
}
```
This is **coarse-grained** at the line level (with column offsets to the start of the generated segment). It is sufficient for editor integrations and step‑mapping. You can enrich it further by adding more `emit_part_map(...)` calls in `reverse_ast.py` if you need per‑expression token granularity.
