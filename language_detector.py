from __future__ import division 
import nltk, re, io, json, string, collections, glob, os, sys
from nltk.collocations import *
from bs4 import BeautifulSoup
from urllib.request import urlopen
from operator import itemgetter

def view_html(raw_html):
	html_file = urlopen(raw_html).read().decode('utf8')
	print(html_file)

def strip_html(raw_html):
	html = urlopen(raw_html).read()
	soup = BeautifulSoup(html)
	for script in soup(["script", "style"]):
		script.extract()
	text = soup.get_text()
	lines = (line.strip() for line in text.splitlines())  						# break into lines and remove leading and trailing space on each
	chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) 	# break multi-headlines into a line each
	text = '\n'.join(chunk for chunk in chunks if chunk) 						# drop blank lines

def ngrams(input, n, size):
	bigrams = [input[i:i+n] for i in range(len(input) - n+1)]
	output_list = collections.Counter(bigrams).most_common(size)
	output_list.sort(key=itemgetter(0))
	output_list.sort(key=itemgetter(1),reverse=True)
	return output_list


def difference_calculator(training, test):	
	#training_set = dict(training).keys()
	training_list = [i[0] for i in training]
	test_list = [i[0] for i in test]
	DNE_PENALTY = len(training_list)
	total_distance = 0
	for index2, item2 in enumerate(test_list):
		for index1, item1 in enumerate(training_list):
			if item2 in training_list:
				if item2 == item1:
					total_distance = total_distance + (abs(index2 - index1))
					break
				else:
					continue
			else:
				total_distance = total_distance + DNE_PENALTY
				break
	return total_distance

def preprocess(raw):
	words = raw.read().lower()
	no_punctuation = ""
	for symbol in words:
		if symbol == '.' or symbol == '?' or symbol == '!':
			symbol = 'X'
		if symbol not in string.punctuation:
			no_punctuation = no_punctuation + symbol
	processed = no_punctuation.replace('X', '_')
	return processed

def load_languages():
	path = os.path.dirname(os.path.realpath(__file__))#'C:\\Users\\Kevin\\Desktop\\Language_Detector\\training_data'
	language_list = []
	for filename in glob.glob(os.path.join(path, 'training_data\\*.txt')):
		f = open(filename, "r", encoding='UTF-8')
		train = preprocess(f)
		bigrams = ngrams(train, 2, 300)
		base = os.path.basename(filename)
		language_list.append((os.path.splitext(base)[0], bigrams))
		f.close()
	return language_list

def main():
	language_list = load_languages()
	closest_match = None
	user_input = input("Give me a file and I will tell you what language it's in: ")
	assert os.path.exists(user_input), "I did not find the file at, "+str(user_input)
	f = open(user_input, 'r+', encoding='UTF-8')
	train = preprocess(f)		
	test_bigrams = ngrams(train, 2, 300)
	for i, (language, train_bigram) in enumerate(language_list):
		difference = difference_calculator(train_bigram, test_bigrams)
		if closest_match == None:
			closest_match = (language, difference)
		elif difference < closest_match[1]:
			closest_match = (language, difference)
	print (closest_match)

if __name__ == "__main__":
    main()