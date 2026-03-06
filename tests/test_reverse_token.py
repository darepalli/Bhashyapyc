# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bhashyapyc import reverse_translate_python

def test_token_reverse_preserves_comments_and_translates_keywords_te():
    py = '# comment\nif True:\n    print("x")\n'
    te = reverse_translate_python(py, lang='te')
    assert '# comment' in te  # comment preserved
    assert 'యెడల' in te      # 'if' translated
    assert 'ముద్రించు' in te  # 'print' translated
