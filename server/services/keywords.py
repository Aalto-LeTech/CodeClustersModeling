from server.services.antlr_local.java_parsers import parse_keyword_tokens

from collections import Counter

def parse_keywords(submissionIds, codeList):
    res = {}
    for i, c in enumerate(codeList):
        subId = submissionIds[i]
        intTokens, rareTokens = parse_keyword_tokens(c)
        res[subId] = {}
        res[subId]['keywords'] = dict(Counter(intTokens))
        res[subId]['rare_keywords'] = dict(Counter(rareTokens))
    return res
