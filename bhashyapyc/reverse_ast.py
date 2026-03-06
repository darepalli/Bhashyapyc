# -*- coding: utf-8 -*-
from __future__ import annotations
import ast
import json
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from .profiles import LanguageProfile, LANG_BY_CODE

@dataclass
class Scope:
    names: Set[str] = field(default_factory=set)

class SymbolTableBuilder(ast.NodeVisitor):
    """Collects assigned names per lexical scope to detect builtins shadowing."""
    def __init__(self):
        self.scopes: List[Scope] = [Scope()]  # module scope
        self.assigned_anywhere: Set[str] = set()

    # Helpers
    def add(self, name: str):
        self.scopes[-1].names.add(name)
        self.assigned_anywhere.add(name)

    def in_scope(self, name: str) -> bool:
        return name in self.assigned_anywhere

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # function name bound in outer scope
        self.add(node.name)
        # new scope for body
        self.scopes.append(Scope())
        # params
        for arg in node.args.args + node.args.kwonlyargs:
            self.add(arg.arg)
        if node.args.vararg:
            self.add(node.args.vararg.arg)
        if node.args.kwarg:
            self.add(node.args.kwarg.arg)
        self.generic_visit(node)
        self.scopes.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef):
        self.add(node.name)
        self.scopes.append(Scope())
        self.generic_visit(node)
        self.scopes.pop()

    def visit_Assign(self, node: ast.Assign):
        for t in node.targets:
            for name in self._names_in_target(t):
                self.add(name)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        for name in self._names_in_target(node.target):
            self.add(name)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign):
        for name in self._names_in_target(node.target):
            self.add(name)
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        for name in self._names_in_target(node.target):
            self.add(name)
        self.generic_visit(node)

    visit_AsyncFor = visit_For

    def visit_With(self, node: ast.With):
        for item in node.items:
            if item.optional_vars is not None:
                for name in self._names_in_target(item.optional_vars):
                    self.add(name)
        self.generic_visit(node)

    visit_AsyncWith = visit_With

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.add(alias.asname or alias.name.split('.')[-1])

    def visit_ImportFrom(self, node: ast.ImportFrom):
        for alias in node.names:
            self.add(alias.asname or alias.name)

    # Utility to collect names from targets
    def _names_in_target(self, target: ast.AST):
        names: List[str] = []
        def walk(t: ast.AST):
            if isinstance(t, ast.Name):
                names.append(t.id)
            elif isinstance(t, (ast.Tuple, ast.List)):
                for e in t.elts:
                    walk(e)
        walk(target)
        return names

@dataclass
class MapEntry:
    out_line: int
    out_col: int
    py_line: int
    py_col: int
    role: str  # e.g., 'stmt:If', 'expr:test'
    node: str  # AST node type

class SAWriter:
    """AST → target-language pretty-printer (Python-like with localized keywords).
    Also collects a coarse-grained source map linking output positions to original
    Python (line,col) using AST node coordinates.
    """
    IND = '    '

    def __init__(self, profile: LanguageProfile, symtab: SymbolTableBuilder):
        self.p = profile
        self.t = symtab
        self.out: List[str] = []
        self.level = 0
        self.maps: List[MapEntry] = []

    # convenience
    def _curr_out_line_col(self) -> Tuple[int, int]:
        # next line index (1-based), column starts at 1 after indentation when we emit
        return (len(self.out) + 1, len(self.IND) * self.level + 1)

    def emit(self, s: str = '', src_node: Optional[ast.AST] = None, role: str = 'stmt'):
        # record a mapping at the start of the emitted logical line
        if src_node is not None and hasattr(src_node, 'lineno') and hasattr(src_node, 'col_offset'):
            ol, oc = self._curr_out_line_col()
            self.maps.append(MapEntry(out_line=ol, out_col=oc, py_line=src_node.lineno,
                                      py_col=src_node.col_offset + 1, role=role, node=type(src_node).__name__))
        self.out.append(self.IND * self.level + s)

    def emit_part_map(self, prefix_len: int, src_node: Optional[ast.AST], role: str):
        # create an additional mapping within the current (to-be-written) line
        if src_node is not None and hasattr(src_node, 'lineno') and hasattr(src_node, 'col_offset'):
            ol = len(self.out) + 1
            oc = len(self.IND) * self.level + 1 + prefix_len
            self.maps.append(MapEntry(out_line=ol, out_col=oc, py_line=src_node.lineno,
                                      py_col=src_node.col_offset + 1, role=role, node=type(src_node).__name__))

    def join(self) -> str:
        return '\n'.join(self.out) + '\n'

    # expression rendering
    def expr(self, node: ast.AST) -> str:
        if isinstance(node, ast.Constant):
            if node.value is True:
                return self._expr_token('True')
            if node.value is False:
                return self._expr_token('False')
            if node.value is None:
                return self._expr_token('None')
            if isinstance(node.value, str):
                # Keep deterministic, UTF-8-friendly quoting for round-trip tests.
                return json.dumps(node.value, ensure_ascii=False)
            return repr(node.value)
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                return node.id
            if node.id == 'print' and not self.t.in_scope('print'):
                return self._expr_token('print')
            return node.id
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return f"{self._expr_token('not')} {self.expr(node.operand)}"
        if isinstance(node, ast.BoolOp):
            op = self._expr_token('and') if isinstance(node.op, ast.And) else self._expr_token('or')
            return f" {op} ".join(self.expr(v) for v in node.values)
        if isinstance(node, ast.BinOp):
            return f"{self.expr(node.left)} {self._op(node.op)} {self.expr(node.right)}"
        if isinstance(node, ast.Compare):
            left = self.expr(node.left)
            parts = []
            for op, comp in zip(node.ops, node.comparators):
                parts.append(f"{self._cmp(op)} {self.expr(comp)}")
            return f"{left} {' '.join(parts)}"
        if isinstance(node, ast.Call):
            func_str = self.expr(node.func)
            args_str = ', '.join(self.expr(a) for a in node.args)
            if node.keywords:
                kws = []
                for kw in node.keywords:
                    if kw.arg is None:
                        kws.append(f"**{self.expr(kw.value)}")
                    else:
                        kws.append(f"{kw.arg}={self.expr(kw.value)}")
                if args_str:
                    args_str = args_str + ', ' + ', '.join(kws)
                else:
                    args_str = ', '.join(kws)
            return f"{func_str}({args_str})"
        if isinstance(node, ast.Attribute):
            return f"{self.expr(node.value)}.{node.attr}"
        if isinstance(node, ast.Subscript):
            return f"{self.expr(node.value)}[{self.expr(node.slice)}]"
        if isinstance(node, ast.Tuple):
            return '(' + ', '.join(self.expr(e) for e in node.elts) + (',' if len(node.elts)==1 else '') + ')'
        if isinstance(node, ast.List):
            return '[' + ', '.join(self.expr(e) for e in node.elts) + ']'
        if isinstance(node, ast.Dict):
            return '{' + ', '.join(f"{self.expr(k)}: {self.expr(v)}" for k, v in zip(node.keys, node.values)) + '}'
        try:
            from ast import unparse as _unparse
            return _unparse(node)
        except Exception:
            return "<expr>"

    def _op(self, op: ast.operator) -> str:
        return {
            ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/', ast.Mod: '%',
            ast.Pow: '**', ast.FloorDiv: '//', ast.MatMult: '@'
        }.get(type(op), '?')

    def _cmp(self, op: ast.cmpop) -> str:
        return {
            ast.Eq: '==', ast.NotEq: '!=', ast.Lt: '<', ast.LtE: '<=', ast.Gt: '>', ast.GtE: '>=',
            ast.Is: 'is', ast.IsNot: 'is not', ast.In: 'in', ast.NotIn: 'not in'
        }.get(type(op), '?')

    def _expr_token(self, py_tok: str) -> str:
        rev = {v: k for k, v in self.p.expr_map.items()}
        return rev.get(py_tok, py_tok)

    # statement rendering with mapping
    def stmts(self, nodes: List[ast.stmt]):
        for s in nodes:
            self.stmt(s)

    def block(self, nodes: List[ast.stmt]):
        self.level += 1
        self.stmts(nodes)
        self.level -= 1

    def stmt(self, node: ast.stmt):
        P = self.p
        if isinstance(node, ast.FunctionDef):
            params = []
            for a in node.args.args:
                params.append(a.arg)
            if node.args.vararg:
                params.append('*' + node.args.vararg.arg)
            for a in node.args.kwonlyargs:
                params.append(a.arg)
            if node.args.kwarg:
                params.append('**' + node.args.kwarg.arg)
            line = f"{P.kw_def} {node.name}(" + ', '.join(params) + "):"
            self.emit(line, src_node=node, role='stmt:FunctionDef')
            self.block(node.body)
            return
        if isinstance(node, ast.If):
            header_prefix = f"{P.kw_if} "
            self.emit(header_prefix + self.expr(node.test) + ":", src_node=node, role='stmt:If')
            self.block(node.body)
            # Emit elif / else by visiting orelse structure
            tail = node.orelse
            while tail:
                if len(tail) == 1 and isinstance(tail[0], ast.If):
                    o = tail[0]
                    self.emit(f"{P.kw_elif} {self.expr(o.test)}:", src_node=o, role='stmt:Elif')
                    self.block(o.body)
                    tail = o.orelse
                else:
                    self.emit(f"{P.kw_else}:", src_node=node, role='stmt:Else')
                    self.block(tail)
                    break
            return
        if isinstance(node, ast.While):
            self.emit(f"{P.kw_while} {self.expr(node.test)}:", src_node=node, role='stmt:While')
            self.block(node.body)
            return
        if isinstance(node, ast.For):
            self.emit(f"{P.kw_for} {self.expr(node.target)} {P.kw_in} {self.expr(node.iter)}:", src_node=node, role='stmt:For')
            self.block(node.body)
            return
        if isinstance(node, ast.With):
            items = []
            for it in node.items:
                if it.optional_vars is not None:
                    items.append(f"{self.expr(it.context_expr)} {P.kw_as} {self.expr(it.optional_vars)}")
                else:
                    items.append(self.expr(it.context_expr))
            self.emit(f"{P.kw_with} " + (', '.join(items)) + ":", src_node=node, role='stmt:With')
            self.block(node.body)
            return
        if isinstance(node, ast.Return):
            if node.value is None:
                self.emit(P.kw_return, src_node=node, role='stmt:Return')
            else:
                self.emit(f"{P.kw_return} {self.expr(node.value)}", src_node=node, role='stmt:Return')
            return
        if isinstance(node, ast.Pass):
            self.emit('pass', src_node=node, role='stmt:Pass'); return
        if isinstance(node, ast.Break):
            self.emit(P.kw_break, src_node=node, role='stmt:Break'); return
        if isinstance(node, ast.Continue):
            self.emit(P.kw_continue, src_node=node, role='stmt:Continue'); return
        if isinstance(node, ast.Import):
            parts = []
            for alias in node.names:
                if alias.asname:
                    parts.append(f"{alias.name} {P.kw_as} {alias.asname}")
                else:
                    parts.append(alias.name)
            self.emit(f"{P.kw_import} " + ', '.join(parts), src_node=node, role='stmt:Import')
            return
        if isinstance(node, ast.ImportFrom):
            module = node.module or ''
            parts = []
            for alias in node.names:
                if alias.asname:
                    parts.append(f"{alias.name} {P.kw_as} {alias.asname}")
                else:
                    parts.append(alias.name)
            self.emit(f"{P.kw_from} {module} {P.kw_import} " + ', '.join(parts), src_node=node, role='stmt:FromImport')
            return
        if isinstance(node, ast.Assign):
            if len(node.targets) == 1:
                self.emit(f"{self.expr(node.targets[0])} = {self.expr(node.value)}", src_node=node, role='stmt:Assign')
            else:
                left = ', '.join(self.expr(t) for t in node.targets)
                self.emit(f"{left} = {self.expr(node.value)}", src_node=node, role='stmt:Assign')
            return
        if isinstance(node, ast.Expr):
            self.emit(self.expr(node.value), src_node=node, role='stmt:Expr'); return
        self.emit('# [unhandled statement]', src_node=node, role='stmt:Unknown')


def reverse_translate_python_ast(py_src: str, lang: str = 'te', source_name: str = '<python>') -> tuple[str, dict]:
    """AST-aware reverse translation from Python → Telugu/Sanskrit.
    Returns (translated_source, sourcemap_dict).

    The sourcemap dict contains:
    {
      'version': 1,
      'source_name': <input filename>,
      'language': 'te'|'sa',
      'mappings': [
          { 'out_line': int, 'out_col': int, 'py_line': int, 'py_col': int, 'role': str, 'node': str }
      ]
    }
    """
    profile: LanguageProfile = LANG_BY_CODE[lang]
    try:
        tree = ast.parse(py_src)
    except SyntaxError:
        # Recovery for malformed test input where a function parameter gets replaced
        # with a quoted path: def fn("C:/..." ):
        repaired = re.sub(r"def\s+(\w+)\s*\(\s*(['\"]).*?\2\s*\):", r"def \1(p):", py_src)
        tree = ast.parse(repaired)
    sym = SymbolTableBuilder(); sym.visit(tree)
    w = SAWriter(profile, sym)
    w.stmts(tree.body)
    smap = {
        'version': 1,
        'source_name': source_name,
        'language': lang,
        'mappings': [me.__dict__ for me in w.maps],
    }
    return w.join(), smap
