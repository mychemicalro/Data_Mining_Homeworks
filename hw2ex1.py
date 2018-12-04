import nltk
import codecs
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import unidecode
import re
import string
import math

def main():

	processAllJobs() # call used to get rid of punctuation, stop words, weird characters, etc
	# at this point i have written in output the processed jobs. each line represents a job. when a newline is encountered, it means that 
	# a new job is starting
	writeKeyDocIDpairsAndConstructEuclideanIndex() #this call writes (word, docID) pairs sorted to output. also constructs the euclidean index
	# (word docID) rows are sorted, and ready for building an inverted index
	constructInvertedIndex() #constructs the inverted index based on the file with the sorted (word docID) pairs
	computeProximityQuery() #takes in input from terminal some words and outputs the 10 most related job announcements
 
def processAllJobs():
	# the jobs.txt file, for each job it has: "jobIndex." as initial string. so for each line I will be looking for the numbers
	#at the beginning of each line, starting from 1.
	i = 1
	newjob = ""
	job_index =str(i)+"." # useful for reading from the output of exercise 6, first hw
	f = codecs.open("jobs.txt", "r", "UTF-8") # reading jobs
	f1 = codecs.open("result.txt", "w", "UTF-8") #writing the processed jobs

	for line in f:
		if job_index in line[0:len(job_index)]:
			if i > 1:
				# complete job because the line contains the "id" of the job
				job = newjob 
				job = re_job(job) #replaces lots of characters
				job = processJob(job) # here several words are cut off.
				f1.write(unidecode.unidecode(job).replace("aEURC/", "").replace("aEUR", "").replace("(", "").replace(")", "").replace("!", "")) #replacing some other chars coming from conversion to ascii from unicode
				f1.write('\n')

			newjob = "" #new job to be read
			newjob = newjob + line[len(job_index):].lower() # pass to the next new job, not including the id of the job
			i += 1 # incrementing the number of the job to search, that is the next job
			job_index = str(i)+"."
			continue

		newjob = newjob + line.lower() # just concatenate the rest of the job announcement

	#last job processing
	job = newjob
	job = re_job(job)
	job= processJob(newjob)
	f1.write(unidecode.unidecode(job).replace("aEURC/", '').replace("aEUR", ''))
	f1.write('\n')

	f1.close() # closing files
	f.close()

def re_job(newjob):

	newjob = re.sub(' +',' ', newjob)
	newjob = re.sub('\n', ' ', newjob)
	newjob = re.sub('\t', ' ', newjob)
	newjob = re.sub('\\(', '', newjob)
	newjob = re.sub('\\)', '', newjob)
	newjob = re.sub('^', '', newjob)
	newjob = re.sub('\\*', '', newjob)
	newjob = re.sub(';', '', newjob)
	newjob = re.sub('\\?', '', newjob)
	newjob = re.sub('!', '', newjob)
	newjob = re.sub('~', '', newjob)
	newjob = re.sub('$', '', newjob)
	newjob = re.sub(':', '', newjob)
	newjob = re.sub(',', '', newjob)
	newjob = re.sub('\\[', '', newjob)
	newjob = re.sub('\\]', '', newjob)
	newjob = re.sub('--', '', newjob)
	newjob = newjob.replace("...", '')
	newjob = newjob.replace("'", '')
	newjob = newjob.replace("&", '')
	newjob = newjob.replace("%", '')
	newjob = newjob.replace("''", '')

	return newjob

def processJob(job):
	job_tokens = word_tokenize(job) #tokenize it
	job_tokens = stopWordsRemoval(job_tokens) #removing some other characters
	job_tokenized = " ".join(job_tokens) #unifying the string

	return job_tokenized #returning the whole string

def stopWordsRemoval(job_tokens):
	# removes stopwords and punctuation
	words = job_tokens
	stopWords = set(stopwords.words('italian')) | {"#", '', '.', '-', '*', '(', ')', '!'}
	wordsFiltered = []
 
	for w in words:
		if w not in stopWords: 
			if ('-' in w or '.' in w or '^' in w or '_' in w) and w != ".net":
				continue
			t = False
			if len(w) < 2 and w != "C":
				continue
			for i in w:
				if i.isalpha():
					t = True
			if t == False:
				continue
			elif w.isdigit():
				continue
			elif '/' in w:
				spl = w.split('/')
				for i in spl:
					wordsFiltered.append(i)
			else:
				wordsFiltered.append(w)

	return wordsFiltered

def writeKeyDocIDpairsAndConstructEuclideanIndex():

	# the docID will be the number of the row
	# with this call I can also build the Euclidean Distances Index, that is the doc (id, distance) pairs

	f = open("result.txt", 'r') # open without unicode
	d = open("WordDocIDpairsSorted.txt", 'w') #file containing (word docID) sorted pairs
	d1 = open("EuclideanDistancesIndex.txt", 'w') #file containing (docID distance) pairs

	indexWords = []

	i = 0 # used as the jobID
	for l in f:
		# this for is writing the (word, docID) pairs for the inverted index construction
		words = word_tokenize(l)
		jobsDict = {} # dictionary containing, for each job, a value standing for the occurrences of each of its words
		for p in range(0, len(words)):
			if len(words[p]) < 2 and (words[p] != "c" or words[p] != "C"): #filtering some other chars
				continue
			if words[p].isdigit():
				continue
			indexWords.append((words[p], str(i)))
			word_occ = jobsDict.get(words[p], 0) #get the value, if exists, if not it is 0
			jobsDict[words[p]] = word_occ + 1 # update occurances 

		distance = 0 # initialize the distance
		for (key, value) in jobsDict.items(): # iterate over all values, take the sum of the squares
			distance = distance + value*value
		distance = math.sqrt(distance) # get the sqrt

		d1.write(str(i) +","+ str(distance) + "\n") # write the distance to the output alongside with the id
		i+=1

	sortedIndexWords = sorted(indexWords, key=lambda tup: tup[0]) #sorting based on the word
	for i in sortedIndexWords:
		#print i[0], i[1]
		d.write(i[0]+" "+i[1]+"\n") #outputs (word docID) sorted pairs

	f.close()
	d.close()
	d1.close()

def constructInvertedIndex():
	# this method will write to output the inverted index, that in each line contains: word:df:(docID occurrences) pairs
	# where word is the word, df is the document frequency, and the pairs stand for how many times a word appears in the document
	# with the docID.

	# read the sorted file with word, docID
	f = open("WordDocIDpairsSorted.txt", 'r')
	d = open("invertedIndex.txt", 'w')

	# this methods scans the keyDocIDpairsSorted.txt file, and for each word it checks how many times a word 
	# shows up in some document. this can be done since the file is ordered, first by word, and then by docID

	previous_key = ""
	previous_id = "0"
	count = 1
	first_line = True
	list_for_key = [] # contains, for each word, all the (docID #occurrences) pairs
	for line in f:
		tup = line.split()
		current_key = tup[0] #taking word
		current_id = tup[1] #taking docID

		if current_id == previous_id and current_key == previous_key:
			count +=1 # if both equal, then the counter is incremented
		elif current_id != previous_id and previous_key == current_key:
			list_for_key.append((previous_id, count))
			count = 1
			previous_id = current_id # if word is the same, but docID changes, I am done with a (docID, #occurs) pairs, so i move to the 
			#following docID
		elif previous_key != current_key: # if words are different, I need to move to another word processing.
			if first_line == False: # taking out the first line
				list_for_key.append((previous_id, count))
				d.write(previous_key+":") # writing in output word:df:pairs(docID, #occurrences)
				d.write(str(len(list_for_key))+":")
				for elem in list_for_key:
					d.write(elem[0]+","+str(elem[1])+":")

				d.write("\n")

				list_for_key = [] #updating values
				count = 1
				previous_key = current_key
				previous_id = current_id
			else: #same as above, just not in the case in which this is the first word encountered
				list_for_key = []
				count = 1
				previous_key = current_key
				previous_id = current_id
				first_line = False

	# processing last row
	list_for_key.append((previous_id, count))
	d.write(previous_key+":")
	d.write(str(len(list_for_key))+":")
	for elem in list_for_key:
		d.write(elem[0]+","+str(elem[1])+":")
	d.write("\n")

	f.close()
	d.close()

def computeProximityQuery():
	# in here, we are getting a query with some terms, and we want to find the
	# top k most similar jobs announcements
	N = 4259 #number of jobs
	# initialize array with N scores, where N is the number of docs
	scores = [0.0] * (N+1)
	lengths = [0.0] * (N+1)
	# fetch all the euclidean distances from the file.
	f = open("EuclideanDistancesIndex.txt", 'r')
	for line in f: # populating lengths
		pair = line.replace("\n",'').split(",")
		lengths[int(pair[0])+1] = float(pair[1]) # array containing all the euclidean distances, docID has its euclidean distance at lengths[docID] location
	f.close()

	query = raw_input("Insert the query: ")
	terms = query.split()
	postingLists = searchQueryTerms(terms) #got the lists, after searching the terms in the file.
	# computing wtq
	tf = 1 #tf of the query term is 1
	for (key, value) in postingLists.items():
		#print value[0] #value contains all the pairs (docID, #occurences)
		df = int(value[0]) # value[0] is the length of the array of pairs (docID occurences), that is the document frequency
		idf = math.log10(N/df)
		wtq = tf * idf # this should be the weight of term t in query q

		for v in value[1:-1]: # basically, for each document in the posting list of the term
			docID = int(v.split(",")[0])
			tf_td = int(v.split(",")[1])
			wtd = tf_td * idf # we compute the weight of that term in the document
			scores[docID] += wtq * wtd # and update the doc's score

	#normalizing values
	for i in range(1, len(lengths)):
		scores[i] = scores[i]/lengths[i]

	result = sorted(range(len(scores)), key=lambda k: scores[k], reverse = True) #sorting values
	print "The 10 most similar job announcements are"
	for i in result[:10]:
		print "document index:", i, "with score:",scores[i]

def searchQueryTerms(terms):
	# terms is a list of terms
	f = open("invertedIndex.txt", 'r')
	postingLists = {}
	for line in f:
		pairs =  line.replace("\n", '').split(":") #in this way I get the word, and all the elements of the posting list
		# need to look after terms
		for t in terms:
			if pairs[0] == t:
				# add the list of pairs to postinglists
				postingLists[pairs[0]] = pairs[1:]

	f.close()
	return postingLists

main()