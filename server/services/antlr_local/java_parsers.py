import antlr4
from antlr4 import RuleContext

from server.services.antlr_local.generated.JavaLexer import JavaLexer
from server.services.antlr_local.generated.JavaParser import JavaParser
from server.services.antlr_local.generated.JavaParserListener import JavaParserListener
from server.services.antlr_local.MyListener import KeyPrinter
from server.services.antlr_local.TreeListener import TreeListener, Node
from server.services.antlr_local.java_tokens import tokenTypes, interestingTokenTypes, rareTokenTypes

def getRule(antlrNode, parser):
    return parser.ruleNames[antlrNode.getRuleIndex()]
    
def getTokenType(n):
    t = n.getSymbol().type
    if t in tokenTypes:
        return tokenTypes[t]
    return None

def generate_complete_tree(parentNode, antlrNode, parser):
    name = getRule(antlrNode, parser)
    depth = antlrNode.depth()
    n = Node(parentNode, name, depth)
    for child in antlrNode.children:
        if hasattr(child, 'getRuleIndex'):
            n.addChild(generate_complete_tree(n, child, parser))
        elif hasattr(child, 'getSymbol'):
            token_type = getTokenType(child)
            if token_type:
                n.addChild(Node(parentNode, token_type, depth + 1))
        else:
            print('unknown node')
    return n

def parse_complete_tree(code):
    code_stream = antlr4.InputStream(code)
    lexer = JavaLexer(code_stream)
    token_stream = antlr4.CommonTokenStream(lexer)
    parser = JavaParser(token_stream)
    tree = parser.compilationUnit()
    t = generate_complete_tree(Node(None, 'root', 0), tree, parser)
    return t

def parse_keyword_tokens(code):
    code_stream = antlr4.InputStream(code)
    lexer = JavaLexer(code_stream)
    token_stream = antlr4.CommonTokenStream(lexer)
    parser = JavaParser(token_stream)
    tree = parser.compilationUnit()

    allTypes = [t.type for t in token_stream.tokens]
    interestingTokens = [interestingTokenTypes[t] for t in allTypes if t in interestingTokenTypes]
    rareTokens = [rareTokenTypes[t] for t in allTypes if t in rareTokenTypes]
    return interestingTokens, rareTokens

def parse_modified_tokens(code):
    code_stream = antlr4.InputStream(code)
    lexer = JavaLexer(code_stream)
    token_stream = antlr4.CommonTokenStream(lexer)
    parser = JavaParser(token_stream)
    tree = parser.compilationUnit()

    printer = KeyPrinter()
    walker = antlr4.ParseTreeWalker()
    walker.walk(printer, tree)

    return printer.get_result()

def parse_ast_complete(codeList):
    token_lists = [parse_complete_tree(c).toList() for c in codeList]
    return list(map(lambda x: ' '.join(x), token_lists))

def parse_ast_keywords(codeList):
    n = len(codeList)
    keywords = [None] * n
    rareKeywords = [None] * n
    for i, c in enumerate(codeList):
        intTokens, rareTokens = parse_keyword_tokens(c)
        keywords[i] = intTokens
        rareKeywords[i] = rareTokens
    return keywords, rareKeywords

def parse_ast_modified(codeList):
    return [parse_modified_tokens(c) for c in codeList]
