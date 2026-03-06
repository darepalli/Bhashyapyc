# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from pathlib import Path
import sys, json
from .compiler import compile_to_python
from .reverse import reverse_translate_python
from .reverse_ast import reverse_translate_python_ast

BANNER = "bhashyapyc (rev) — Telugu & Sanskrit front-end with reverse translators + source maps"

def main(argv=None):
    ap = argparse.ArgumentParser(description=BANNER)
    ap.add_argument("source", help="Path to source file")
    ap.add_argument("--lang", choices=['auto','te','sa'], default='auto', help="Language: Telugu(te), Sanskrit(sa), or auto for forward; 'te'/'sa' required for reverse")
    ap.add_argument("--emit-py", dest="emit_py", help="(Forward) Write translated Python to this path")
    ap.add_argument("--run", action="store_true", help="(Forward) Execute the translated code")

    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--reverse", action="store_true", help="Token-based Python → target language (keeps comments)")
    grp.add_argument("--reverse-ast", action="store_true", help="AST-aware Python → target language (semantic, drops comments)")

    ap.add_argument("--emit-src", dest="emit_src", help="(Reverse) Write translated target source to this path (.tepy/.sa)")
    ap.add_argument("--emit-map", dest="emit_map", help="(Reverse AST) Write source map JSON to this path")

    args = ap.parse_args(argv)
    src_path = Path(args.source)
    if not src_path.exists():
        print(f"Source not found: {src_path}", file=sys.stderr)
        sys.exit(1)

    src = src_path.read_text(encoding='utf-8')

    if args.reverse or args.reverse_ast:
        if args.lang not in ('te','sa'):
            print("Reverse modes require --lang te or --lang sa", file=sys.stderr)
            sys.exit(2)
        if args.reverse_ast:
            out_src, smap = reverse_translate_python_ast(src, lang=args.lang, source_name=str(src_path))
            if args.emit_map:
                Path(args.emit_map).write_text(json.dumps(smap, ensure_ascii=False, indent=2), encoding='utf-8')
                print(f"Wrote source map to {args.emit_map}")
        else:
            out_src = reverse_translate_python(src, lang=args.lang)
            smap = None
        if args.emit_src:
            Path(args.emit_src).write_text(out_src, encoding='utf-8')
            print(f"Wrote target source to {args.emit_src}")
        else:
            print(out_src)
        return

    # Forward compilation
    py = compile_to_python(src, lang=args.lang)
    if args.emit_py:
        Path(args.emit_py).write_text(py, encoding='utf-8')
        print(f"Wrote Python to {args.emit_py}")
    if args.run or not args.emit_py:
        g = {"__name__": "__main__", "__file__": str(src_path)}
        exec(compile(py, str(src_path), 'exec'), g, g)

if __name__ == '__main__':
    main()
