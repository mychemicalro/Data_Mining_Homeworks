
def computeAverageScore(filename):

		if filename == None:
			return

		beers = open(filename, 'r') #opening the beers.txt file
		beers_book = {} #dictionary for saving beers, using the name as key, and (score, #reviews) tuple as value
		for line in beers:
			# print line
			review = line.split() #split line
			key = ""
			for k in range(len(review) - 1):
				key +=review[k]+" " #form the key, leaving out the score, that is the last element

			(old_score, old_reviews_nr) = beers_book.get(key, (0, 0)) #get the value, if exists
			beers_book[key] = (old_score + int(review[-1]), old_reviews_nr + 1) #update the score and the number of reviews

		beers.close() #done with the input file
		print "number of different beers: " + str(len(beers_book.keys()))
		beers_standings = {} #dictionary  for the standings
		for (key, value) in beers_book.items(): #for all the beers in the book
			score = value[0]
			reviews = value[1]
			if reviews < 100:
				beers_book.pop(key, None) #pop the beers with not enough reviews
				continue
			average = score / reviews #otherwise compute the average
			#print score
			beers_standings[key] = average #and save it into the standings
			#print key

		result = sorted(beers_standings, key=beers_standings.get) # sort the standings according to the average
		l = len(result)
		print "Top 10 beers"
		for i in range (l-1, l-11, -1): #and print reversely the top 10 beers
			print result[i] +"with average: " + str(beers_standings[result[i]])

def main():
	computeAverageScore("beers.txt")
main()