from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from operator import add
import binascii
from itertools import combinations
import random

jobs = "file:///Users/mychro94/Desktop/res.txt" #need to be changed
sc = SparkContext("local", "ex2AS")
sc.setLogLevel("ERROR") #log level errors

spark = SparkSession.builder.getOrCreate() # getting or creating session
textFile = sc.textFile(jobs) #reading input file

######################### JACCARD ##########################


jacc = textFile.flatMap(lambda line: line.split()) #split words of a line

def mapping(line):
	length = len(set(line.split()))-1 #take the length without duplicates of the line
	jobID = line.split()[0]
	return (length, jobID) #output length and jobID

jacc = textFile.flatMap(lambda line: [(c, (mapping(line))) for c in set(line.split()[1:])]) #for each word of a line, except for the index, output the word and (length, jobID)

def retList(accum, y):
	if type(accum) == list or isinstance(accum, list):
		return accum+[(y[0],y[1])]
	else:
		return [accum, y]

#for each word, there will be a list of tuples containing the details of the jobs containing that word
jacc = jacc.reduceByKey(retList) # now I have lists containing lengths of jobs and jobIDs

jacc = jacc.values().filter(lambda x: isinstance(x, list)) # keeping only the lists
jacc = jacc.flatMap(lambda l:[(l[i]+l[k], 1) for i in range(0, len(l)-1) for k in range (i+1, len(l))]) # for each pair of docs, output the pair with value 1

def res(x):
	sim = 0
	key = x[0]
	len1 = key[0]
	len2 = key[2]
	job1 = key[1]
	job2 = key[3]
	common_elements = x[1]
	if len1 + len2 - common_elements == 0: # avoiding division by 0
		t = (0,0,0)
	else:
		sim = common_elements / float((len1 + len2 - common_elements))
		t = (job1, job2, sim)

	return t

# again reduce by key, but now all the ones are summed
jacc = jacc.reduceByKey(add) 
jacc = jacc.map(res) # for each element, res is called, that computes the similarity and outputs a tuple
jacc = jacc.filter(lambda x: x[2] > 0.8) # filtering the tuples based on the similarity, if >0.8 then ok.
jacc = jacc.map(lambda x: (x[0], x[1]))
#print "Pairs of near-duplicates proposed by Jaccard", jacc.collect()
print "Number of near-duplicates over 80% of similarity with jaccard", jacc.count() #counting pairs

############################ LSH ################################

textFile = sc.textFile(jobs) #reading input file

def pickRandomCoeffs(k):
	maxShingleID = 2**32-1 #max integer of four bytes
	randList = [] # the result list
	while k > 0:
		randIndex = random.randint(0, maxShingleID) 
		while randIndex in randList:
			randIndex = random.randint(0, maxShingleID) # we dont want duplicates
		randList.append(randIndex)
		k = k - 1
	return randList

def shingling(line):
	text = line.split()
	jobID = text[0]
	k = 10
	del text[0]
	text = " ".join(text)
	result = set() # I don't want duplicates
	l = text.replace("\n", '')
	b = [l[i:i+k] for i in xrange(len(l) - k + 1)] # taking all shingles of length k

	for shingle in b:
		crc = binascii.crc32(shingle) & 0xffffffff #hash the shingle
		result.add(crc) # add the shingle to the result
	t = (jobID, result)
	return t

lsh = textFile.map(shingling) #split words of a line

l = 225 # number of hashing functions
b = 25 # number of bands
r = 9 # number of rows

coeffA = pickRandomCoeffs(l)
coeffB = pickRandomCoeffs(l)

def minwise(tuple):
	global coeffB, coeffA, l, b, r
	jobID = tuple[0]
	shingleSet = tuple[1]
	signature = []
	nextPrime = 4294967311 # next prime after 2**32 -1

	# computing signatures
	for i in range(0, l):
		minHashCode = nextPrime + 1
		for s in shingleSet: # for each shingle set
			hashCode = (coeffA[i] * s + coeffB[i]) % nextPrime
			if hashCode < minHashCode:
				minHashCode = hashCode
		signature.append(minHashCode)

	i = 0
	k = 0

	# LSH
	res = []
	for i in range(0, b): #for each band
		sum_r_minhashes = reduce(lambda x, y: x+y, signature[k: r+k]) # sum the r minhashes
		h = sum_r_minhashes % nextPrime
		k += r
		t = (h, jobID)
		res.append(t)

	return res # list of tuples

lsh = lsh.flatMap(minwise) # computing signatures and sending in output tuples (hashed(minhashes), jobID)

def unify(accum, y):
	if type(accum) == list or isinstance(accum, list): # I want all the jobIDs that hashed together, to be in a list
		return accum + [y]
	else:
		return [accum, y]

lsh = lsh.reduceByKey(unify) # I want only lists of jobIDs
lsh = lsh.filter(lambda x: type(x[1]) == list) # going on only with the lists
# output all the pairs of jobs that hashed together in some band
lsh = lsh.flatMap(lambda l: [(l[1][i],l[1][k]) for i in range(0, len(l[1])-1) for k in range (i+1, len(l[1]))])
lsh = lsh.distinct() # removing duplicates
#print "Near-duplicate pairs proposed by LSH", lsh.collect()
print "Number of near-duplicate pairs given by LSH", lsh.count()

######################### INTERSECTION ########################

# intersection of two RDDs
intersection = lsh.intersection(jacc)
print "Intersected elements between LSH and Jaccard pairs", intersection.count()









