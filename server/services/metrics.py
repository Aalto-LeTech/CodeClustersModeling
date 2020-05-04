import numpy as np
import pandas as pd

import antlr4
from antlr4 import RuleContext

from server.services.antlr_local.generated.JavaLexer import JavaLexer
from server.services.antlr_local.generated.JavaParser import JavaParser
from server.services.antlr_local.generated.JavaParserListener import JavaParserListener
from server.services.antlr_local.MyListener import KeyPrinter
from server.services.antlr_local.java_tokens import interestingTokenTypes

from collections import Counter

def counts_to_id_dict(ids, counts):
    d = {}
    for i, c in enumerate(counts):
        if None in c:
            c.pop(None)
        if len(c) != 0:
            d[ids[i]] = dict(c)
    return d

def parse_to_keyword_tokens(code):
    code_stream = antlr4.InputStream(code)
    lexer = JavaLexer(code_stream)
    token_stream = antlr4.CommonTokenStream(lexer)
    parser = JavaParser(token_stream)
    tree = parser.compilationUnit()

    allTypes = [t.type for t in token_stream.tokens]
    interestingTokens = [interestingTokenTypes[t] for t in allTypes if t in interestingTokenTypes]
    rareTokens = [rareTokenTypes[t] for t in allTypes if t in rareTokenTypes]
    return interestingTokens, rareTokens

def parse_ast_tokens(codeList):
    n = len(codeList)
    keywords = [None] * n
    rareKeywords = [None] * n
    keywordCounts = [None] * n
    rareKeywordCounts = [None] * n
    for i, c in enumerate(codeList):
        intTokens, rareTokens = parse_to_keyword_tokens(c)
        keywords[i] = intTokens
        rareKeywords[i] = rareTokens
        keywordCounts[i] = Counter(intTokens)
        rareKeywordCounts[i] = Counter(rareTokens)
    return keywords, rareKeywords, keywordCounts, rareKeywordCounts

def create_metrics(submissionIds, codeList):
    documents = len(codeList)
    keywords, rareKeywords, keywordCounts, rareKeywordCounts = parse_ast_tokens(codeList)
    return {
        "keywords": keywords,
        "rare_keywords": rareKeywords,
        "keyword_counts": counts_to_id_dict(submissionIds, keywordCounts),
        "rare_keyword_counts": counts_to_id_dict(submissionIds, rareKeywordCounts)
    }