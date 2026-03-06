# -*- coding: utf-8 -*-
from __future__ import annotations

import io
import tokenize
from typing import Dict, Optional

from .profiles import LANG_BY_CODE, LanguageProfile


def _reverse_name_map(profile: LanguageProfile) -> Dict[str, str]:
    mapping = {
        "def": profile.kw_def,
        "if": profile.kw_if,
        "elif": profile.kw_elif,
        "else": profile.kw_else,
        "for": profile.kw_for,
        "in": profile.kw_in,
        "while": profile.kw_while,
        "with": profile.kw_with,
        "as": profile.kw_as,
        "from": profile.kw_from,
        "import": profile.kw_import,
        "return": profile.kw_return,
        "break": profile.kw_break,
        "continue": profile.kw_continue,
    }
    for local_name, py_name in profile.expr_map.items():
        mapping[py_name] = local_name
    return mapping


def reverse_translate_python(py_src: str, lang: str = "te") -> str:
    if lang not in LANG_BY_CODE:
        raise ValueError(f"Unsupported language: {lang}")

    profile: LanguageProfile = LANG_BY_CODE[lang]
    mapping = _reverse_name_map(profile)

    out_tokens = []
    prev_meaningful: Optional[tokenize.TokenInfo] = None

    reader = io.StringIO(py_src).readline
    for tok in tokenize.generate_tokens(reader):
        if tok.type == tokenize.NAME and tok.string in mapping:
            # Do not translate attributes like module.print
            if not (prev_meaningful and prev_meaningful.type == tokenize.OP and prev_meaningful.string == "."):
                tok = tokenize.TokenInfo(tok.type, mapping[tok.string], tok.start, tok.end, tok.line)
        out_tokens.append(tok)

        if tok.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.COMMENT):
            prev_meaningful = tok

    return tokenize.untokenize(out_tokens)
