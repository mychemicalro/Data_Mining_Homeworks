import requests
from bs4 import BeautifulSoup
import codecs
import re
import time

global_counter = 0

def main():
	global global_counter   
	global_counter = 0

	#first i need a first request for some parameters
	r = requests.get('https://www.kijiji.it/offerte-di-lavoro/offerta/informatica-e-web/') #first request
	s = r.text #getting the string 
	index = s.find("Offerte in Offerte di Lavoro") #find a point above which i can delete everything
	index_page = s.find("last-page") #finding the number of pages
	pages = r.text[index_page:index_page+15]
	arr = re.findall(r'\d+', pages)
	number_of_pages = int(arr[0]) # total number of pages to be visited

	# now, for each page, i must process all the lists
	for p in range(1, number_of_pages + 1):
		if p == 1:
			url = "https://www.kijiji.it/offerte-di-lavoro/offerta/informatica-e-web/" # first page request
		else:
			url = "https://www.kijiji.it/offerte-di-lavoro/offerta/informatica-e-web/?p="+str(p) # all other pages
		print url
		r = requests.get(url)
		s = r.text #getting the text 
		index = s.find("Offerte in Offerte di Lavoro")

		y = BeautifulSoup(r.text[index:], features="html.parser") # giving to the parser only the text that matters
		array_li = y.findAll("li") # getting all li elements
		for j in range(0, len(array_li)):
			parse_job(array_li[j]) # for each li, process it
		time.sleep(1)

def parse_job(li):
	y = BeautifulSoup(str(li), features="html.parser")

	if y.a == None or y.li == None or y.li.div == None or y.li.div.p == None:
		return
		
	title = y.a.string.strip()
	url = y.a['href']
	description = y.li.div.p.string.strip()
	luogo = y.find_all("p")[2].string.strip()
	date = y.find_all("p")[3].string.strip()
	global global_counter # using a global counter in order to make more comprehensive the output
	global_counter = global_counter + 1
	f = codecs.open("jobs.txt", "a+", "UTF-8")
	f.write(str(global_counter)+") "+title+"\t"+description+"..."+"\t"+luogo+"\t"+date+"\t"+url) # writing in output data about a single job
	f.write("\n")
	f.close()

main()