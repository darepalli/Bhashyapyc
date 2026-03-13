# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class LanguageProfile:
    code: str
    kw_def: str
    kw_if: str
    kw_elif: str
    kw_else: str
    kw_for: str
    kw_in: str
    kw_while: str
    kw_with: str
    kw_as: str
    kw_from: str
    kw_import: str
    kw_return: str
    kw_break: str
    kw_continue: str
    expr_map: Dict[str, str]


TELUGU = LanguageProfile(
    code="te",
    kw_def="విధి",
    kw_if="ఐతే",
    kw_elif="లేకుంటే",
    kw_else="లేకపోతే",
    kw_for="ప్రతి",
    kw_in="లో",
    kw_while="వరకు",
    kw_with="తో",
    kw_as="గా",
    kw_from="నుండి",
    kw_import="దిగుమతి",
    kw_return="తిరిగిపంపు",
    kw_break="విరమించు",
    kw_continue="కొనసాగు",
    expr_map={
        "ముద్రించు": "print",
        "సత్యం": "True",
        "అసత్యం": "False",
        "శూన్యం": "None",
        "మరియు": "and",
        "లేదా": "or",
        "కాదు": "not",
    },
)

SANSKRIT = LanguageProfile(
    code="sa",
    kw_def="विधि",
    kw_if="यदि",
    kw_elif="अन्ययदि",
    kw_else="अन्यथा",
    kw_for="कृते",
    kw_in="मध्ये",
    kw_while="यावत्",
    kw_with="सह",
    kw_as="रूपेण",
    kw_from="इतः",
    kw_import="आयात",
    kw_return="प्रत्यावर्तय",
    kw_break="विरम",
    kw_continue="अनुवर्त",
    expr_map={
        "मुद्रय": "print",
        "सत्यम्": "True",
        "असत्यम्": "False",
        "शून्यम्": "None",
        "च": "and",
        "वा": "or",
        "नहि": "not",
    },
)

LANG_BY_CODE = {
    "te": TELUGU,
    "sa": SANSKRIT,
}
