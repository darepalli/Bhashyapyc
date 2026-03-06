# -*- coding: utf-8 -*-
import sys, ast
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc.reverse_ast import reverse_translate_python_ast

PY = (
    'def demo():\n'
    '    print = 123\n'
    '    if True:\n'
    '        return print\n'
)

def test_ast_reverse_avoids_shadowed_builtin_and_has_map_sa():
    out, smap = reverse_translate_python_ast(PY, lang='sa', source_name='demo.py')
    # ensure local identifier 'print' not replaced (should remain 'print')
    assert 'print' in out
    assert 'मुद्रय' not in out
    # has basic sourcemap fields
    assert smap['version'] == 1
    assert smap['source_name'] == 'demo.py'
    assert smap['language'] == 'sa'
    assert isinstance(smap['mappings'], list) and len(smap['mappings']) >= 1
