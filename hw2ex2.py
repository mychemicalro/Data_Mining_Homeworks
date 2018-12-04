import hashlib
import binascii
import random
import numpy as np
from collections import defaultdict
from operator import itemgetter
import time


def main():
	# part 1
	# First we need to compute the shingles set for all jobs
	k=10
	f = open("result.txt", 'r')

	shinglesDict = {} #dictionary used for LSH, it contains docIDs and the hashed shingles
	jobsDict = {} #dictionary used for Jaccard, it contains docIDs and the words of the job

	id = 0
	for l in f:
		shinglesSet = JobShingling(l, k) #returns a set of hashed shingles
		jobsDict[id] = l.split() #saving the line as a list of words separated by " ", the entry has docID value
		shinglesDict[id] = shinglesSet #creating docID key, hashed list of shingles for each document as value
		id += 1
	f.close()

	#now I have the dict with all shingles sets, with hashed elements, and the dictionary of the jobs
	# I am done with the shingling

	# minwise hashing, part 2
	# I want to generate l random hashing functions of type hash(x) = (ax+b)%c
	l = 225
	coeffA = pickRandomCoeffs(l)
	coeffB = pickRandomCoeffs(l)

	# computing signatures
	signatures = computeSignatures(shinglesDict, coeffA, coeffB, l) # this methods returns a dictionary of signatures, where the key is the docID
	MinwiseSignatures(signatures)
	# part 3, computing LSH
	LSHpairs = LSHresults(signatures)

	# computing the real results, with the intersection of the words of each document
	JaccardResults(jobsDict)

	intersectionBetweenJaccardAndLSH(LSHpairs)

def JaccardForSignatures(sig1, sig2):
	equalHashes = 0
	for i in range(0, 100):
		if sig1[i] == sig2[i]:
			equalHashes += 1
	similarity = equalHashes / 100.0
	return (similarity, equalHashes)

def LSH(signatures, bands, r):
	l = len(signatures.keys()) # number of signatures
	nextPrime = 4294967311 # used for the mod of the hashing function
	resultDict = defaultdict(list) # dictionary with values that are lists
	index = 0 # used for reading the signature lists
	for i in range(0, bands): #for each band
		for (k, v) in signatures.items(): # for each signature
			sum = 0
			for j in range(0, r): # summing all the hashes of the signature in that range, so for the specific band
				sum += v[index + j]
				# the hashing function used is : sum of all r hashes mod nextPrime
			h = sum % nextPrime # hash the sum
			resultDict[h].append(k) # create a key with that hash, and append the id of the job
		index += r # updating the index for reading the signatures
	#print "keys in lsh before filtering", len(resultDict.keys())
	for (k, v) in resultDict.items(): # filtering out the hashes with only a job that hashed to it
		if len(v) < 2:
			del resultDict[k]

	return resultDict # returns the dictionary

def JaccardForAllListsOfWords(jobsDict):
	#dictionary containing all jaccard coefficients
	JaccardCoefficientsWords = {}
	#jac = open("jaccardCoefficients.txt", 'w')
	#calling computeJaccard for each list of words in jobsDict dictionary
	# the algorithm works in the following way: with two for cycles(one here, one in computeJaccardForAListOfWords method), I compare the first shingleSet with all the other
	#and compute their similarity, then i delete the first shingleSet key form the dictionary. so in the end, the last shingleSet
	#won't be compared to any other shingleSet.	
	JaccardCoefficientsWordsArray = []

	for (k,v) in jobsDict.items():
		l = computeJaccardForAListOfWords(k, v, jobsDict)
		JaccardCoefficientsWords[k] = l
		
		JaccardCoefficientsWordsArray.append(l)
		del jobsDict[k]
		#print "docID "+str(k) + ":" + str(l) 
		#jac.write(str(k)+":")
		#for i in l:
			#jac.write(i)
			#print i
		#jac.write("\n")
	#jac.close()
	return (JaccardCoefficientsWords, JaccardCoefficientsWordsArray)

def sortWords(docWords):
	for (k, v) in docWords.items():
		v = set(v) # removing duplicates, and sorting the set of words
		docWords[k] = sorted(v)

def findIntersection(words1, words2, l1, l2):

	#returns the number of common elements
	result = 0
	#words1 = list(words1)
	#words2 = list(words2)
	j = 0
	k = 0
	while j < l1 and k < l2:
		if words1[j] == words2[k]:
			result += 1
			j += 1
			k += 1
		elif words1[j] < words2[k]:
			j += 1
		else:
			k += 1

	return result

def computeJaccardForAListOfWords(docID, words1, jobsDict):
	lenW1 = len(words1) # get length of the first list of words
	coeffList = [] # list of coefficients containing (word2, jaccard coefficient, #common words)
	for (k2, words2) in jobsDict.items(): #for all the other list of words
		lenW2 = len(words2)
		if k2 != docID: # if different jobs
			intersection = findIntersection(words1, words2, lenW1, lenW2) #compute the number of common elements
			jaccardCoeff = intersection / float(lenW1 + lenW2 - intersection) #compute jaccard like intersection/union
			coeffList.append((docID, k2, round(jaccardCoeff, 2), intersection)) #append the triple
	
	return coeffList

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

def computeSignatures(docShingles, coeffA, coeffB, l):
	signatures = {} # the result dictionary
	nextPrime = 4294967311 # next prime after 2**32 -1
	t0 = time.time()
	for key in docShingles.iterkeys():
		shingleSet = docShingles[key] # taking the shingle set
		docSignature = [] # the resulting signature is an array
		for i in range(0, l): #for each hashing function
			minHashCode = nextPrime + 1
			for s in shingleSet: # for each shingle set
				hashCode = (coeffA[i] * s + coeffB[i]) % nextPrime # I compute the hashing function
				if hashCode < minHashCode:
					minHashCode = hashCode # and if the new hash is less than the previous one, i update the overall minHash
					
			docSignature.append(minHashCode) # append the minhash when passing to another hash function
		signatures[key] = docSignature # done with a job, save the signature
	elapsed = (time.time() - t0)
	print "Calculating all the signatures took %.2fsec" % elapsed
	return signatures # returns the dict

def JobShingling(job, k):
	# this does the shingle of a single job, given k
	l = job.replace("\n", '') # substituting the new line char
	result = set() # I don't want duplicates
	b = [l[i:i+k] for i in xrange(len(l) - k + 1)] # taking all shingles of length k
	for shingle in b:
		crc = binascii.crc32(shingle) & 0xffffffff #hash the shingle
		result.add(crc) # add the shingle to the result
	return result

def MinwiseSignatures(signatures):
	# here I do jaccard over all the signatures
	t0 = time.time()
	signaturesJaccard = set()
	for (k1,sig1) in signatures.items():
		for (k2, sig2) in signatures.items():
			if k1!=k2 and k1 < k2:
				similarity = 0
				(similarity, common_elements) = JaccardForSignatures(sig1, sig2)
				signaturesJaccard.add((k1, k2, similarity, common_elements))

	#print "how many times signatures jaccard", how_many_times
	#orderedJaccardSignaturesCoeff = sorted(signaturesJaccard, key=itemgetter(2), reverse=True) # sort all the comparisons
	# the first 10 are the highest values
	#print "\n"
	#print "Top 10 similarities between all the signatures:"
	#print orderedJaccardSignaturesCoeff[0:10]
	elapsed = (time.time() - t0)
	print "Calculating all minwise hashing pairs took %.2fsec" % elapsed

def LSHresults(signatures):

	b = 25
	r = 9
	t0 = time.time()
	LSHresult = LSH(signatures, b, r) # returns a dict containing as key an hash, and as value a list of all docs that hash to that value for some band 
	
	#now I have all the candidate pairs. I need to fetch, for each item in the dictionary, all the signatures of the documents contained under that key
	r = set()

	for (k, v) in LSHresult.items():
		for i in range(0, len(v)):
			k1 = v[i]
			sig1 = signatures[k1] # fetch signature 1
			for j in range (0, (len(v))):
				k2 = v[j]
				if k1 < k2:
					sig2 = signatures[k2] # get signature 2
					(similarity, common_elements) = JaccardForSignatures(sig1, sig2)
					r.add((v[i], v[j], similarity, common_elements))
	elapsed = (time.time() - t0)
	print "Calculating all LSH pairs took %.2fsec" % elapsed

	# print "how many times LSH jaccard", how_many_times
	#print "\n"
	# need to see how many documents are given by the LSH with 1-(1-s^r)^b 
	#print "Top similarities between the signatures of the candidate pairs suggested by the LSH algorithm:"
	#print "jobID1, jobID2, similarity, common elements"
	orderedJaccardSignaturesWithLSH = sorted(r, key=itemgetter(2), reverse=True) #prints all the pairs of documents that were canditate pairs of being similar, alongside with the minwise based similarity
	# print orderedJaccardSignaturesWithLSH[0:10]
	jobsPairs = []
	for i in orderedJaccardSignaturesWithLSH:
		jobsPairs.append((i[0], i[1]))

	#print len(jobsPairs), "jobsPairs len"
	print "The number of duplicate pairs found with LSH are", len(r)
	return jobsPairs

def JaccardResults(jobsDict):
	# now I sort all the lists of words of each job, i this way i can do Jaccard directly on that lists, in order to get 
	# the most accurate similarity between two jobs
	sortWords(jobsDict)
	t0 = time.time()
	(JaccardCoefficientsWords, JaccardCoefficientsWordsArray) = JaccardForAllListsOfWords(jobsDict) #contains, for each job, all the jaccard similarities with all the other jobs
	elapsed = (time.time() - t0)
	print "Calculating all Jaccard Similarities took %.2fsec" % elapsed
	JaccardCoefficientsWordsArr = []
	for i in JaccardCoefficientsWordsArray:
		for j in i:
			JaccardCoefficientsWordsArr.append(j)

	# I should have an array of tuples
	orderedJaccardCoefficientsWords = sorted(JaccardCoefficientsWordsArr, key=itemgetter(2), reverse=True)

	f=open("JaccardCoefficients.txt", 'w')

	#print "\n"
	#print "Top similarities between the all the jobs with Jaccard similarity:"
	#print "jobID1, jobID2, similarity, common elements"
	jobsOverEighty = 0
	for i in orderedJaccardCoefficientsWords:
		if i[2] >= 0.80:
			jobsOverEighty += 1
			f.write(str(i[0]) + ","+str(i[1])+","+str(i[2]))
			f.write("\n")
			#print i
	#print "There are",jobsOverEighty,"jobs"
	f.close()
	#print orderedJaccardCoefficientsWords[0:10]
	#print "\n"
	print "The number of duplicate pairs found with Jaccard with similarity at least 80% are "+str(jobsOverEighty)

def intersectionBetweenJaccardAndLSH(LSHpairs):
	f = open("JaccardCoefficients.txt", 'r')
	JacPairs = set()
	for l in f: # reading the jaccard coefficients computed and saved on file
		values = l.split(",")
		JacPairs.add((int(values[0]), int(values[1])))

	f.close()

	pairsLSH = set(LSHpairs) 
	commonPairs = JacPairs.intersection(pairsLSH)

	print "The intersection between the Jaccard similarity computed on the words of the jobs, and the similarity results of the LSH technique has", len(commonPairs), "elements."

main()