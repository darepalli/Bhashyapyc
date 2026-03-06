# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc.reverse_ast import reverse_translate_python_ast

PY = 'print("אבגदे एकद्वि తెలుగు")\n'  # Hebrew + Devanagari + Telugu string

def test_reverse_ast_preserves_mixed_rtl_ltr_string():
    tgt, smap = reverse_translate_python_ast(PY, lang='sa', source_name='rtl.py')
    assert '"אבגदे एकद्वि తెలుగు"' in tgt
