# -*- coding: utf-8 -*-
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc.reverse_ast import reverse_translate_python_ast

PY = (
    'def f(n):\n'
    '    for i in range(2):\n'
    '        if n > i:\n'
    '            pass\n'
)

def test_sourcemap_contains_roles_and_node_types_te(tmp_path):
    out, smap = reverse_translate_python_ast(PY, lang='te', source_name='f.py')
    # save to disk to mimic CLI --emit-map
    map_path = tmp_path / 'f.tepy.map.json'
    map_path.write_text(json.dumps(smap, ensure_ascii=False, indent=2), encoding='utf-8')
    data = json.loads(map_path.read_text(encoding='utf-8'))
    assert {'version','source_name','language','mappings'} <= set(data.keys())
    roles = {m['role'] for m in data['mappings']}
    assert any(r.startswith('stmt:For') or r.startswith('stmt:If') for r in roles)
