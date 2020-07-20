import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
from sklearn.decomposition import TruncatedSVD
from sklearn import manifold
from sklearn.cluster import DBSCAN, OPTICS, KMeans

import hdbscan
import umap

from server.services.antlr_local.java_parsers import parse_ast_complete, parse_ast_keywords, parse_ast_modified

def create_clusters(labels, submissionIds):
    res = {}
    for c in set(labels):
        res[c] = [submissionIds[idx] for idx, label in enumerate(labels) if label == c]
    return res

def create_token_df(token_set, codeList):
    if token_set == 'modified':
        return pd.DataFrame({ "token_stream": parse_ast_modified(codeList) })
    elif token_set == 'complete':
        return pd.DataFrame({ "token_stream": parse_ast_complete(codeList) })
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
        metric = 'precomputed'
        optics = OPTICS(min_samples=min_samples, metric=metric, max_eps=max_eps).fit(dist_matrix)
        return optics.labels_
    elif name == 'KMeans':
        n_clusters = params.get('k_clusters') or 8
        kmeans = KMeans(n_clusters=n_clusters).fit(dist_matrix)
        return kmeans.labels_
    else:
        raise ValueError(f'cluster_dist_matrix(): Unknown clustering method name: {name}')

def reduce_to_2d(tfidf, dim_visualization_params={}):
    params = dim_visualization_params or {}
    name = params.get('name')
    if name == 'UMAP':
        n_neighbors = params.get('n_neighbors') or 30
        min_dist = params.get('min_dist') or 0.0
        return umap.UMAP(
            n_components=2,
            n_neighbors=n_neighbors,
            min_dist=min_dist,
        ).fit_transform(tfidf)
    else:
        perplexity = params.get('perplexity') or 30
        svd_n_components = params.get('svd_n_components')
        matrix = tfidf
        if svd_n_components is not None:
            matrix = TruncatedSVD(
                n_components=svd_n_components,
                random_state=0
            ).fit_transform(tfidf)
        return TSNE(
            n_components=2,
            perplexity=perplexity
        ).fit_transform(matrix)

def run_ngram(submissionIds, codeList, token_set='modified', ngrams=(3,3), random_seed=-1,
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

    X_embedded = reduce_to_2d(tfidf, dim_visualization_params)

    labels = cluster_dist_matrix(dist_matrix, clustering_params).tolist()

    silhouette_avg = silhouette_score(X, labels)

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
        "silhouette_score": silhouette_avg,
    }
