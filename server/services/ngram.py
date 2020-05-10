import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
from sklearn.decomposition import TruncatedSVD
from sklearn import manifold
from sklearn.cluster import DBSCAN, OPTICS, KMeans

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

def create_clusters(labels, submissionIds):
    res = {}
    for c in set(labels):
        res[c] = [submissionIds[idx] for idx, label in enumerate(labels) if label == c]
    return res

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
    if name == 'DBSCAN' or name is None:
        min_samples = params.get('min_samples') or 5
        eps = params.get('eps') or 0.5
        metric = 'precomputed'
        dbscan = DBSCAN(min_samples=min_samples, metric=metric, eps=eps).fit(dist_matrix)
        return dbscan.labels_
    elif name == 'HDBSCAN':
        min_cluster_size = params.get('min_cluster_size') or 2
        min_samples = params.get('min_samples') or 5
        metric = 'precomputed'
        show_linkage_tree = params.get('show_linkage_tree') or False
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric=metric,
            gen_min_span_tree=show_linkage_tree
        )
        clusterer.fit(dist_matrix)
        #plt.figure(3, figsize=(24,8)) 
        #clusterer.single_linkage_tree_.plot(cmap='viridis', colorbar=True)
        return clusterer.labels_
    elif name == 'OPTICS':
        min_samples = params.get('min_samples') or 5
        max_eps = params.get('max_eps') or np.inf
        if max_eps == -1:
            max_eps = np.inf
        metric = 'precomputed'
        optics = OPTICS(min_samples=min_samples, metric=metric, max_eps=max_eps).fit(dist_matrix)
        return optics.labels_
    elif name == 'KMeans':
        n_clusters = params.get('k_clusters') or 8
        kmeans = KMeans(n_clusters=n_clusters).fit(dist_matrix)
        return kmeans.labels_
    else:
        raise ValueError(f'cluster_dist_matrix(): Unknown clustering method name: {name}')

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

def run_ngram(submissionIds, codeList, token_set='modified', ngrams=(3,3), svd_n_components=50, random_seed=-1,
              clustering_params={}, dim_visualization_params={}):

    documents = len(codeList)
    df = create_token_df(token_set, codeList)

    if random_seed != -1:
        np.random.seed(random_seed)

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

    labels = cluster_dist_matrix(dist_matrix, clustering_params).tolist()

    clusters = create_clusters(labels, submissionIds)
    coordinates = [{
        'id': submissionIds[i],
        'x': d[0],
        'y': d[1],
        'cluster': labels[i]
        } for (i, d) in enumerate(X_embedded)]

    return {
        "clusters": clusters,
        "2d": coordinates,
    }
