import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
from sklearn.decomposition import TruncatedSVD
from sklearn import manifold
from sklearn.cluster import DBSCAN

import hdbscan
import umap

import antlr4
from antlr4 import RuleContext

from server.services.antlr_local.generated.JavaLexer import JavaLexer
from server.services.antlr_local.generated.JavaParser import JavaParser
from server.services.antlr_local.generated.JavaParserListener import JavaParserListener
from server.services.antlr_local.MyListener import KeyPrinter
from server.services.antlr_local.java_tokens import interestingTokenTypes, rareTokenTypes

import re

def normalize_for_ai(source_code):
    res = re.sub("\/\*.*\*\/", "", source_code, flags=re.DOTALL) # multiline comment
    res = re.sub("\/\/.*", "", res) # inline comments
    res = re.sub("\".+\"", "\"\"", res) # string values
    res = re.sub("\d+", "$", res)
    return res

def parse_to_compositional_tokens(code):
    code_stream = antlr4.InputStream(code)
    lexer = JavaLexer(code_stream)
    token_stream = antlr4.CommonTokenStream(lexer)
    parser = JavaParser(token_stream)
    tree = parser.compilationUnit()

    printer = KeyPrinter()
    walker = antlr4.ParseTreeWalker()
    walker.walk(printer, tree)

    return printer.get_result()

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

def parse_ast_modified(codeList):
    n = len(codeList)
    token_list = [None] * n
    normalized_list = [None] * n
    for i, c in enumerate(codeList):
        token_list[i] = parse_to_compositional_tokens(c)
        normalized_list[i] = normalize_for_ai(c)
    return token_list, normalized_list

def parse_ast_keywords(codeList):
    n = len(codeList)
    keywords = [None] * n
    rareKeywords = [None] * n
    for i, c in enumerate(codeList):
        intTokens, rareTokens = parse_to_keyword_tokens(c)
        keywords[i] = intTokens
        rareKeywords[i] = rareTokens
    return keywords, rareKeywords

def create_clusters(labels):
    clusters = {}
    for i, c in enumerate(labels):
        if not c in clusters:
            clusters[c] = [i]
        else:
            clusters[c].append(i)
    return clusters

def create_token_df(token_set, codeList):
    if token_set == 'modified':
        tlist, nlist = parse_ast_modified(codeList)
        return pd.DataFrame({ "token_stream": tlist })
    else:
        keywords, rareKeywords = parse_ast_keywords(codeList)
        return pd.DataFrame({ "token_stream": list(map(lambda x: ' '.join(x), keywords)) })

def cluster_dist_matrix(dist_matrix, clustering_params):
    params = clustering_params or {}
    name = params.get('name')
    if name == 'HDBSCAN':
        min_cluster_size = params.get('min_cluster_size') or 2
        return_dendrogram = params.get('return_dendrogram') or False
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            gen_min_span_tree=return_dendrogram
        )
        clusterer.fit(dist_matrix)
        #plt.figure(3, figsize=(24,8)) 
        #clusterer.single_linkage_tree_.plot(cmap='viridis', colorbar=True)
        return clusterer.labels_
    else:
        eps = params.get('eps') or 0.05
        db = DBSCAN(min_samples=2, metric="precomputed", eps=eps).fit(dist_matrix)
        return db.labels_

def reduce_to_2d(X_reduced, dim_visualization_params={}):
    params = dim_visualization_params or {}
    name = params.get('name')
    if name == 'UMAP':
        n_neighbors = params.get('n_neighbors') or 30
        min_dist = params.get('min_dist') or 0.0
        return umap.UMAP(
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            n_components=2
        ).fit_transform(X_reduced)
    else:
        perplexity = params.get('perplexity') or 30
        return TSNE(
            n_components=2,
            perplexity=perplexity
        ).fit_transform(X_reduced)

def run_ngram(submissionIds, codeList, token_set='modified', ngrams=(3,3), svd_n_components=50,
              clustering_params={}, dim_visualization_params={}):

    documents = len(codeList)
    df = create_token_df(token_set, codeList)

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

    X_reduced = TruncatedSVD(n_components=svd_n_components, random_state=0).fit_transform(tfidf)
    X_embedded = reduce_to_2d(X_reduced, dim_visualization_params)

    labels = cluster_dist_matrix(dist_matrix, clustering_params)
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
        "2d": coordinates,
    }
