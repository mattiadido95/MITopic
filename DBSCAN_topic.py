import os.path

from sklearn.cluster import DBSCAN
import numpy as np
from sklearn.preprocessing import RobustScaler
from sklearn.metrics.pairwise import cosine_similarity

import PCA_plot3D as pca
import operator


def DBSCAN_Topic(word_vect_dict, year):
    print("partito dbscan")
    X = []
    for index in range(0, len(word_vect_dict)):
        X.append(list(word_vect_dict.values())[index])
    bestCluster = {}
    best_eps = {}
    for i in range(1, 11):
        clustering = DBSCAN(metric='cosine', eps=i / 10, min_samples=5).fit(X)

        key = []
        value = []
        d = {}
        for index in range(0, len(word_vect_dict)):
            d[clustering.labels_[index]] = 0

        for index in range(0, len(word_vect_dict)):
            d[clustering.labels_[index]] = d[clustering.labels_[index]] + 1

        cluster_array_sorted = sorted(d.items(), key=operator.itemgetter(1),
                                      reverse=True)  # clusters ordinati in base al numero di elementi
        number_of_clusters = len(cluster_array_sorted)  # abbiamo trovato il numero di cluster diversi

        if cluster_array_sorted[0][0] != -1:
            cluster_array_sorted = cluster_array_sorted[0][0]
        elif len(cluster_array_sorted) == 1:
            continue
        else:
            cluster_array_sorted = cluster_array_sorted[1][0]

        bestCluster[i] = cluster_array_sorted
        best_eps[i] = number_of_clusters  # id raggio piu popoloso

        for index in range(0, len(word_vect_dict)):
            key.append(clustering.labels_[index])  # prendo gli id dei cluster
            value.append(list(word_vect_dict.values())[index])

    theBest = sorted(best_eps.items(), key=operator.itemgetter(1), reverse=True)
    clustering = DBSCAN(metric='cosine', eps=theBest[0][0] / 10, min_samples=5).fit(
        X)  # clustering sul raggio che ha il maggior numero di cluster

    dctWord = {}
    dctValue = {}

    for index in range(0, len(word_vect_dict)):
        if (clustering.labels_[index] != -1):
            dctWord[clustering.labels_[index]] = []
            dctValue[clustering.labels_[index]] = []

    for index in range(0, len(word_vect_dict)):
        if (clustering.labels_[index] != -1):
            dctWord[clustering.labels_[index]].append(list(word_vect_dict.keys())[index])
            dctValue[clustering.labels_[index]].append(list(word_vect_dict.values())[index])

    if os.path.exists(f"output/{year}/clustering/{year}_clusters.txt"):
        os.remove(f"output/{year}/clustering/{year}_clusters.txt")
    bigClusters = {}
    for g in range(0, len(dctWord)):
        tot_vectors = {}
        if len(dctWord[g]) > 50:
            bigClusters[g] = []
            for r in range(0, len(dctWord[g])):
                tot_vectors[dctWord[g][r]] = dctValue[g][r]
                transformer = RobustScaler(quantile_range=(0, 75.0))  # rimuovo gli outlier
                transformer.fit(list(tot_vectors.values()))
                centroid_ = transformer.center_
                centroid_ = np.array([centroid_])
                distance_vector = {}
            for j in range(0, len(tot_vectors) - 1):
                dist = cosine_similarity(centroid_, np.array([list(tot_vectors.values())[j]]))
                distance_vector[list(tot_vectors.keys())[j]] = dist[0][0]
            distance_vector = sorted(distance_vector.items(), key=operator.itemgetter(1), reverse=True)
            if not os.path.exists(f"output/{year}/clustering"):
                os.makedirs(f"output/{year}/clustering")
                a = "w"
            else:
                a = "a"
            with open(f"output/{year}/clustering/{year}_clusters.txt", a) as f:
                f.write("selected year: " + year)
                f.write(" \n")
                f.write("len: " + str(len(dctWord[g])))
                f.write(" \n")
                f.write("cluster words:\n")
                for l in range(0, len(distance_vector)):
                    if l == 100:
                        break
                    bigClusters[g].append(distance_vector[l][0])
                    f.write(distance_vector[l][0] + ", ")

                f.write(" \n")
                f.write(" \n")
        else:
            if not os.path.exists(f"output/{year}/clustering"):
                os.makedirs(f"output/{year}/clustering")
                a = "w"
            else:
                a = "a"
            with open(f"output/{year}/clustering/{year}_clusters.txt", a) as f:
                f.write("selected year: " + year)
                f.write(" \n")
                f.write("len: " + str(len(dctWord[g])))
                f.write(" \n")
                f.write("cluster words:\n")
                for l in range(0, len(dctWord[g])):
                    f.write(dctWord[g][l] + ", ")

                f.write(" \n")
                f.write(" \n")
    key = []
    value = []
    word = []
    for index in range(0, len(word_vect_dict)):
        key.append(clustering.labels_[index])
        value.append(list(word_vect_dict.values())[index])
        word.append(list(word_vect_dict.keys())[index])
    if not os.path.exists(f"output/{year}/PCA/"):
        os.makedirs(f"output/{year}/PCA/")
    pca.pca_clustering_3D(value, key,
                          f"output/{year}/PCA/year_{year}__radius_{theBest[0][0] / 10}_FinalClustering")
    return bigClusters
