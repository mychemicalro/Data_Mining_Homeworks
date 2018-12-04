import itertools, random

class Deck(object):

	def __init__(self):
		self._deck = list(itertools.product(range(1,14),['Spade','Heart','Diamond','Club'])) # create all the possible combinations

		random.shuffle(self._deck)
		self.get2a(1000) # the names of the methods are the points of the exercise
		self.get2b(1000)
		self.get2c(1000)
		self.get2d(1000)
		self.get2e(100000)
		#print("You got:")
		#for i in range(5):
   			#print self._deck[i][0], "of", self._deck[i][1]

   	def get2b(self, draws):
   		draws_with_aces = 0
   		for i in range(draws):
   			random.shuffle(self._deck)
   			for j in range(5):
   				if self._deck[j][0] == 1:
   					draws_with_aces = draws_with_aces + 1
   					break
   		print "2B result: there have been ", draws_with_aces, "/", draws, "successful draws"

	def get2a(self, draws):
		draws_with_aces = 0
		for i in range(draws):
			random.shuffle(self._deck)
			for j in range(2):
				if self._deck[j][0] == 1: # if the card is an ace
					draws_with_aces = draws_with_aces + 1
					break
		print "2A result: there have been ", draws_with_aces, "/", draws, "successful draws"

	def get2c(self, draws):
		draws_with_pairs = 0
		for i in range(draws):
			random.shuffle(self._deck)
			if self._deck[0][0] == self._deck[1][0]: # if the first two cards have the same number
				draws_with_pairs = draws_with_pairs + 1
				
		print "2C result: there have been ", draws_with_pairs, "/", draws, "successful draws"

	def get2d(self, draws):
		draws_with_5diamonds = 0
		for i in range(draws):
			random.shuffle(self._deck)
			if self._deck[0][1] == self._deck[1][1] == self._deck[2][1] == self._deck[3][1] == self._deck[4][1] and self._deck[0][1] == 'Diamond':
				draws_with_5diamonds = draws_with_5diamonds + 1
				
		print "2D result: there have been ", draws_with_5diamonds, "/", draws, "successful draws"

	def get2e(self, draws):
		draws_with_full_houses = 0
		list = []
		for i in range(draws):
			random.shuffle(self._deck)
			for j in range(5):
				list.append(self._deck[j][0]) # ad in an array the five cards

			list.sort() # sort them, in order to control if numbers are equal
			#print list
			if ((list[0] == list[1]) == (list[2] and list[3])) == list[4] or ((list[2] == list[3] == list[4]) and(list[1] == list[2])):
				#print list
				draws_with_full_houses = draws_with_full_houses + 1
			list = []
				
		print "2E result: there have been ", draws_with_full_houses, "/", draws, "successful draws"


Deck()