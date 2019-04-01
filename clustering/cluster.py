from sklearn.cluster import AgglomerativeClustering
import numpy as np
from math import inf


def cluster(dist_matrix):
    clustering = AgglomerativeClustering(n_clusters=2, affinity="precomputed",
                                         linkage="average")
    clustering.fit(dist_matrix)
    _labels = clustering.labels_
    return _labels
