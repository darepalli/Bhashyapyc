# -*- coding: utf-8 -*-
from __future__ import annotations

import io
import tokenize
from typing import Dict

from .profiles import LANG_BY_CODE, LanguageProfile


def _validate_indentation(src: str) -> None:
    for lineno, line in enumerate(src.splitlines(), start=1):
        if not line:
            continue
        i = 0
        while i < len(line) and line[i] in " \t\u00a0":
            i += 1
        prefix = line[:i]
        if "\t" in prefix:
            raise SyntaxError(f"Tabs are not allowed for indentation (line {lineno})")
        if "\u00a0" in prefix:
            raise SyntaxError(f"NBSP is not allowed for indentation (line {lineno})")


def _forward_name_map(profile: LanguageProfile) -> Dict[str, str]:
    mapping = {
        profile.kw_def: "def",
        profile.kw_if: "if",
        profile.kw_elif: "elif",
        profile.kw_else: "else",
        profile.kw_for: "for",
        profile.kw_in: "in",
        profile.kw_while: "while",
        profile.kw_with: "with",
        profile.kw_as: "as",
        profile.kw_from: "from",
        profile.kw_import: "import",
        profile.kw_return: "return",
        profile.kw_break: "break",
        profile.kw_continue: "continue",
    }
    mapping.update(profile.expr_map)
    return mapping


def _translate_names(src: str, mapping: Dict[str, str]) -> str:
    out_tokens = []
    reader = io.StringIO(src).readline
    for tok in tokenize.generate_tokens(reader):
        if tok.type == tokenize.NAME and tok.string in mapping:
            tok = tokenize.TokenInfo(tok.type, mapping[tok.string], tok.start, tok.end, tok.line)
        out_tokens.append(tok)
    return tokenize.untokenize(out_tokens)


def _detect_lang(src: str) -> str:
    te_markers = ["విధి", "యెడల", "లేకపోతే", "తిరిగి", "ముద్రించు"]
    sa_markers = ["विधि", "यदि", "अन्यथा", "प्रत्यावर्तय", "मुद्रय"]
    if any(m in src for m in te_markers):
        return "te"
    if any(m in src for m in sa_markers):
        return "sa"
    return "te"


def compile_to_python(src: str, lang: str = "auto") -> str:
    if src.startswith("\ufeff"):
        src = src[1:]
    _validate_indentation(src)

    if lang == "auto":
        lang = _detect_lang(src)
    if lang not in LANG_BY_CODE:
        raise ValueError(f"Unsupported language: {lang}")

    profile = LANG_BY_CODE[lang]
    mapping = _forward_name_map(profile)
    return _translate_names(src, mapping)
