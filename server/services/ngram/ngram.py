import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
from sklearn.decomposition import TruncatedSVD
from sklearn import manifold
from sklearn.cluster import DBSCAN

import antlr4
from antlr4 import RuleContext

from server.services.ngram.antlr_local.JavaLexer import JavaLexer
from server.services.ngram.antlr_local.JavaParser import JavaParser
from server.services.ngram.antlr_local.JavaParserListener import JavaParserListener
from server.services.ngram.MyListener import KeyPrinter

import re

def normalize_for_ai(source_code):
    res = re.sub("\/\*.*\*\/", "", source_code, flags=re.DOTALL) # multiline comment
    res = re.sub("\/\/.*", "", res) # inline comments
    res = re.sub("\".+\"", "\"\"", res) # string values
    res = re.sub("\d+", "$", res)
    return res

def parse_to_compositional_tokens(code):
    #print("parsing: ", self.ID)
    code_stream = antlr4.InputStream(code)
    lexer = JavaLexer(code_stream)
    token_stream = antlr4.CommonTokenStream(lexer)
    parser = JavaParser(token_stream)
    tree = parser.compilationUnit()

    printer = KeyPrinter()
    walker = antlr4.ParseTreeWalker()
    walker.walk(printer, tree)

    # CyclomaticComplexityVisitor mv = new CyclomaticComplexityVisitor();
    # mv.visit(tree);

    return printer.get_result()

def parse_ast_tokens(codeList):
    n = len(codeList)
    token_list = [None] * n
    normalized_list = [None] * n
    for i, c in enumerate(codeList):
        token_list[i] = parse_to_compositional_tokens(c)
        normalized_list[i] = normalize_for_ai(c)
    return token_list, normalized_list

def create_clusters(labels):
    clusters = {}
    for i, c in enumerate(labels):
        if not c in clusters:
            clusters[c] = [i]
        else:
            clusters[c].append(i)
    return clusters

def run_ngram(submissionIds, codeList, ngrams=(3,3), n_components=50):
    documents = len(codeList)
    tlist, nlist = parse_ast_tokens(codeList)
    df = pd.DataFrame({ "token_stream": tlist, "normalized": nlist })

    ngram_vectorizer = CountVectorizer(analyzer='word', 
                                       ngram_range=ngrams,
                                       token_pattern="[\S]+",
                                       lowercase=False,
                                       strip_accents="ascii")

    #transformer = TfidfTransformer(smooth_idf=True, norm=None)
    transformer = TfidfTransformer(smooth_idf=False)

    X = ngram_vectorizer.fit_transform(df.token_stream)
    tfidf = transformer.fit_transform(X)

    res_tf = pd.DataFrame(X.A, columns=ngram_vectorizer.get_feature_names())

    res_idf = pd.DataFrame(tfidf.A, columns=ngram_vectorizer.get_feature_names())

    sim_matrix = np.around(cosine_similarity(tfidf), decimals=8)
    dist_matrix = np.subtract(np.ones(sim_matrix.shape, dtype=np.int8), sim_matrix) # sim <=> 1 - dist

    X_reduced = TruncatedSVD(n_components=n_components, random_state=0).fit_transform(tfidf)
    X_embedded = TSNE(n_components=2, perplexity=40, verbose=0).fit_transform(X_reduced)

    db = DBSCAN(min_samples=2, metric="precomputed", eps=0.05).fit(dist_matrix)
    labels = db.labels_ # -1 = noise
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    unique_labels = set(labels) 

    labels_list = labels.tolist()
    clusters = create_clusters(labels_list)
    true_label_clusters = {k : [submissionIds[i] for i in v] for k, v in clusters.items()}
    coordinates = [{
        'id': submissionIds[i],
        'x': d[0],
        'y': d[1],
        'cluster': labels_list[i]
        } for (i, d) in enumerate(X_embedded)]
    return {
        "clusters": true_label_clusters,
        "labels": labels_list,
        "TSNE": coordinates,
        "params": {
            "ngrams": ngrams,
            "n_components": n_components,
        }
    }

def group_by_strings(codeDict, stringList):
    keys = codeDict.keys()
    n = len(keys)
    mat = np.zeros((n, len(stringList)))
    for i, k in enumerate(keys):
        mat[i] = np.array([1 if (s in codeDict[k]) else 0 for s in stringList])
    return {
        "ids": list(keys),
        "filters": stringList,
        "matches": mat,
        "counts": np.ones(n) @ mat,
        "score": np.sum(mat, axis=1) / len(stringList)
    }
