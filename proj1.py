import xml.etree.ElementTree as ET
import urllib2
import base64
from collections import defaultdict
import nltk
import math
import re
import string
import operator
import sys

stopwords = nltk.corpus.stopwords.words('english')

def getBingQuery(query):
	return 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27' + query + '%27&$top=10&$format=Atom'

def parseResults(content):
	results = []
	root = ET.fromstring(content)
	entries = root.findall('{http://www.w3.org/2005/Atom}entry')
	n = len(entries)
	for i in range(n):
		results.append({'URL': entries[i][3][0][4].text, 'Title': entries[i][3][0][1].text, 'Summary': entries[i][3][0][2].text})
	return results

def printResponse(accountKey, precision, query, bingUrl, results):	
	feedbacks = []
	print "Parameters:"
	print "Client key = " + accountKey
	print "Query      = " + " ".join(query)
	print "Precision  = " + precision
	print "URL: " + bingUrl
	print "Total no of results: " + str(len(results))
	print "Bing Search Results: "
	print "====================="
	for i in range(len(results)):
		print "Result " + str(i+1)
		print "["
		print " URL: " + results[i]['URL']
		print " Title: " + results[i]['Title']
		print " Summary: " + results[i]['Summary']
		print "]"
		print
		feedbacks.append(raw_input("Relevant (Y/N)? ").lower())
	return feedbacks

def printFeedbackSummary(feedbacks, precision, query):
	prec = feedbacks.count('y') * 1.0 / len(feedbacks)
	continue_flag = False
	print "====================="
	print "FEEDBACK SUMMARY"
	print "Query: " + " ".join(query)
	print "Precision: " + str(prec)
	if prec == 0:
		print "No relevant results among the top-10 pages, done"
	elif prec < float(precision):
		print "Still below the desired precision of " + str(precision)
		continue_flag = True
	else:
		print "Desired precision reached, done"
	return continue_flag
	
def Compute_wordlist(results):
	list_complete = []
	final_list = []
	for result in results:
		list_complete.extend(split_words(result['URL']))
		list_complete.extend(split_words(result['Title']))
		list_complete.extend(split_words(result['Summary']))
	list_complete = set(list_complete)
	for item in list_complete:
		if item not in stopwords and len(item)!=0:
			final_list.append(item)
	return final_list

def split_words(line):
	temp=""
	for c in line:
		if 0 < ord(c) < 127:
			temp += c.lower()
		else:
			temp = ' '
	line = temp
	regex = [",",".",":","-","?","!","'","/","&","|",";","_","=","+","#","^",\
			"*","~","\\","\'","\"","\u","%","$","@","(",")","[","]","{","}",\
			"0","1","2","3","4","5","6","7","8","9"]
	for symbol in regex:
		line = line.replace(symbol, " ")
	return line.split(" ")

def getTF(doc, list_complete):
	tfvec = defaultdict(float)
	for term in list_complete:
		tfvec[term] = 0.0
	temp = []
	temp.extend(split_words(doc['URL']))
	temp.extend(split_words(doc['Title']))
	temp.extend(split_words(doc['Summary']))
	for item in list_complete:
		for term in temp:
			if item == term:
				tfvec[item] += 1
	return tfvec

def getqueryTF(doc, list_complete):
	tfvec = defaultdict(float)
	for term in list_complete:
		tfvec[term] = 0.0
	temp = list(doc)
	for item in list_complete:
		for term in temp:
			if item == term:
				tfvec[item] += 1
	return tfvec

def getIDF(doc, results, list_complete):
	N = len(results)
	idfvec = defaultdict(float)
	for term in list_complete:
		idfvec[term] = 0.0
	temp = []
	temp.extend(split_words(doc['URL']))
	temp.extend(split_words(doc['Title']))
	temp.extend(split_words(doc['Summary']))
	temp = set(temp)
	#check whether the words in doc are present in each 'result'
	tempres = []
	for result in results:
		tempres.extend(split_words(result['URL']))
		tempres.extend(split_words(result['Title']))
		tempres.extend(split_words(result['Summary']))

		for item1 in temp:
			if item1 in tempres and len(item1)!=0:
				idfvec[item1] += 1
	for key in idfvec.iterkeys():
		if idfvec[key]:
			idfvec[key] = math.log(N/idfvec[key])
	return idfvec

def Compute_tf_idf(documents, list_complete, results, flag):
	vector = defaultdict(float)
	for term in list_complete:
		vector[term] = 0.0
	if flag:			#documents
		for doc in documents:
			tfvec = getTF(doc, list_complete)
			idfvec = getIDF(doc, results, list_complete)
			for key in vector.iterkeys():
				vector[key] += tfvec[key]*idfvec[key]
	else:				# documents = query
		tfvec = getqueryTF(documents, list_complete)
		for key in vector.iterkeys():
			vector[key] += tfvec[key] # *idfvec[key]
	return vector

def update_query(q, rdoc, dr, nrdoc, dnr):
	qnew = defaultdict(float)
	alpha=1
	beta=0.75
	gamma=0.15
	for key in q.iterkeys():
		qnew[key] = alpha*q[key] + (beta*rdoc[key])/dr - (gamma*nrdoc[key])/dnr
	return qnew
	

def main():
	#Handle options
	accountKey = sys.argv[1]
	precision = sys.argv[2]
	query = sys.argv[3:len(sys.argv)]	
	continue_flag = True
	#Loop until the precision target is reached
	while continue_flag:
		#Execute the Bing query and get results
		bingUrl = getBingQuery("%20".join(query))
		accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
		headers = {'Authorization': 'Basic ' + accountKeyEnc}
		req = urllib2.Request(bingUrl, headers = headers)
		response = urllib2.urlopen(req)
		#content contains the xml/json response from Bing.
		content = response.read()

		#Show results to user and get feedback
		results = parseResults(content)
		feedbacks = printResponse(accountKey, precision, query, bingUrl, results)
		continue_flag = printFeedbackSummary(feedbacks, precision, query)

		if continue_flag:
			list_complete = Compute_wordlist(results)

			#separate results as relevant and not relevant based on user feedback
			r_results = []
			nr_results = []

			for i in xrange(len(results)):
				if(feedbacks[i].lower() == 'y'):
					r_results.append(results[i])
				else:
					nr_results.append(results[i])

			#compute tf-idf for query wrt list_complete
			query_vector = Compute_tf_idf(query, list_complete, results, 0)

			#compute tf-idf for relevant documents wrt list_complete
			rdoc_vector = Compute_tf_idf(r_results, list_complete, results, 1)
			
			dr = len(r_results)

			#compute tf-idf for non-relevant documents wrt list_complete
			nrdoc_vector = Compute_tf_idf(nr_results, list_complete, results, 1)
			
			dnr = len(nr_results)

			qnew = update_query(query_vector, rdoc_vector, dr, nrdoc_vector, dnr)
			sorted_qnew = dict(sorted(qnew.items(), key=operator.itemgetter(1), reverse=True)[:2])
			print sorted_qnew
			
			new_query = list(query)
			for key in sorted_qnew.iterkeys():
				new_query.append(key)
			query = set(new_query)
			print "==============================="
			print ("New Query =		 %s")%query
			print "==============================="
				

if __name__ == "__main__":
	main()

