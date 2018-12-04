import math
from sklearn.cluster import KMeans
import numpy as np
import pickle
import nltk
from nltk.cluster.kmeans import KMeansClusterer
from pyclustering.cluster.kmeans import kmeans
from pyclustering.utils.metric import type_metric, distance_metric
import sklearn.metrics
from collections import defaultdict
import operator

def main():
	np.seterr(divide='ignore', invalid='ignore')
	#call for computing tf-idf for each document, and then apply SVD on the matrix. u, s and vh are saved into files
	(matrix, list_of_keys) = computeTFIDFmatrix()
	k = 64
	clusters1 = KmeansCosineDistance(matrix, k)
	computeSVD(matrix)
	clusters2 = KmeansAfterSVD(k)
	findDescriptiveWords(matrix, list_of_keys) #this is done on the original matrix m. the list of keys is used to retrive the words

def findDescriptiveWords(matrix, list_of_keys):
	#reading the dictionary
	with open ('dict_clusters.txt', 'rb') as fp:
		dict_clusters = pickle.load(fp)
	fp.close()

	TFIDFapproach(dict_clusters, matrix, list_of_keys)

def TFIDFapproach(dict_clusters, matrix, list_of_keys):

	#I will consider all the job announcements in a cluster like a single document. therefore I unify
	#all the announcements into only 1, and then extract the words with the higher tf-idf values
	for (k, v) in dict_clusters.items():
		dict_tfidf = {}
		for announcement in v:
			for word in range(0, len(matrix[announcement])):
				if matrix[announcement][word] == 0:
					continue
				tfidf = matrix[announcement][word]
				old_tfidf = dict_tfidf.get(word, 0)
				dict_tfidf[word] = tfidf + old_tfidf
		printDescriptiveWords(k, dict_tfidf, list_of_keys) #i have the dictionary with all tfidf values for the cluster, now print the words

def printDescriptiveWords(k, dict_, list_of_keys):

	significant_words = [] #i will consider top 20 of the significant words
	sorted_x = sorted(dict_.items(), key=operator.itemgetter(1)) #sort by value, that is tfidf
	for word in sorted_x[-1:-21:-1]: #the top 20 tfidf values
		ind = word[0] #the index of the word in the list_of_keys
		significant_words.append(list_of_keys[ind])
	print "Significant words for cluster", k, significant_words

def computeTFIDFmatrix():
	doc_len = 18929 #number of words in the inverted index
	number_of_rows = 4259 #number of job announcements
	matrix = [[0 for x in range(doc_len)] for y in range(number_of_rows)] 
	N = 4259 #number of job announcements

	index = open("invertedIndex.txt", 'r')
	i = 0 #used as counter on the words in the inverted index
	list_of_keys = []
	#computing tfidf
	for line in index:
		l = line.replace("\n", '').split(":")[:-1] #taking the array of elements from the inverted index
		key = l[0] #word
		list_of_keys.append(key)
		occ = int(l[1]) #doc frequency of the word
		postingList = l[2:] #(doc,occurrences) pairs

		for elem in postingList:
			(doc, o) = elem.split(',')
			tf = int(o) #term frequency of the word in document doc
			idf = math.log10(N/occ)
			tfidf = tf * idf #computing the tf idf of the word
			matrix[int(doc)][i] = tfidf #saving in the matrix, for document doc in column i the tfidf of the word
		i += 1 #incrementing the counter of the words in the inverted index, that acts like an ID of the word
	index.close()
	X = np.array(matrix)
	return X, list_of_keys

def printKmeansResult(kmeans):
	dict_clusters = {}
	c = 0
	for i in kmeans.labels_:
		counter = dict_clusters.get(i, 0)
		dict_clusters[i] = counter + 1

	for (k, v) in dict_clusters.items():
		print "cluster ", k, "has ", v, "documents"

def computeIndexOfEnergy(singular_values):
	total_energy = sum(map(lambda x: x**2, s))
	energy = 0
	counter = 0
	for i in singular_values:
		energy += i**2
		if energy/total_energy > 0.90:
			return counter, s[:counter+1] #return counter and truncated singular_values list
		counter += 1

def removeColsFromU(u, i):

	return np.delete(u, np.s_[i+1:], axis=1)

def removeRowsFromVh(vh, i):

	return vh[:i+1]

def KmeansAfterSVD(k):

	#reading u, s and vh from files
	with open ('u.txt', 'rb') as fp:
		u = pickle.load(fp)
	fp.close()

	with open ('s.txt', 'rb') as fp:
		s = pickle.load(fp)
	fp.close()

	with open ('vh.txt', 'rb') as fp:
		vh = pickle.load(fp)
	fp.close()

	us = np.matmul(u, np.diag(s)) #obtaining the U*S matrix, before to do it the list s must be a diagonal matrix.

	kclusterer = KMeansClusterer(k, distance=nltk.cluster.util.cosine_distance)
	assigned_clusters = kclusterer.cluster(us, assign_clusters=True)
	print "The Davies Bouldin index on K-means (after SVD) with cosine distance is", sklearn.metrics.davies_bouldin_score(us, assigned_clusters), "with k equal", k
	printClustering(assigned_clusters)
	return assigned_clusters

def KmeansCosineDistance(X, k):

	#k-means using the cosine distance
	kclusterer = KMeansClusterer(k, distance=nltk.cluster.util.cosine_distance)
	assigned_clusters = kclusterer.cluster(X, assign_clusters=True)
	print "The Davies Bouldin index on K-means (original tf-idf matrix) with cosine distance is", sklearn.metrics.davies_bouldin_score(X, assigned_clusters), "with k equal", k
	printClustering(assigned_clusters)
	return assigned_clusters

def printClustering(assigned_clusters):

	dict_clusters = defaultdict(list)
	job_id = 0

	for i in assigned_clusters:
		dict_clusters[i].append(job_id)
		job_id += 1

	with open ('dict_clusters.txt', 'wb') as fp:
		pickle.dump(dict_clusters, fp)
	fp.close()

	for (k, v) in dict_clusters.items():
		print "cluster ", k, "has ", len(v), "jobs"

def computeSVD(X):
	#SVD calls, matrices are saved on files
	u, s, vh = np.linalg.svd(X, full_matrices=False)
	(ind, s) = computeIndexOfEnergy(s) #find the singular values needed for having at least 90% of the total energy
	vh = removeRowsFromVh(vh, ind) #removing rows from Vh
	u = removeColsFromU(u, ind) #removing columns from U

	#need to write u, s and vh on file
	with open('u.txt', 'wb') as fp:
		pickle.dump(u, fp)

	fp.close()
	with open('s.txt', 'wb') as fp:
		pickle.dump(s, fp)
	fp.close()

	with open('vh.txt', 'wb') as fp:
		pickle.dump(vh, fp)
	fp.close()

main()