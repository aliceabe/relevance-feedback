import xml.etree.ElementTree as ET
import urllib2
import base64
import sys

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

#def updateQuery(results, feedbacks):
	#TODO: function that updates the query given the results and the feedbacks
	#results is of the following form:
	'''
	[
		{
			'URL': 'http://en.wikipedia.org/wiki/Musk',
			'Summary': 'Musk is a class of aromatic substances commonly used as base notes in perfumery. They include glandular secretions from animals such as the musk deer, numerous plants ...',
			'Title': 'Musk - Wikipedia, the free encyclopedia'
		},
		{
			'URL': 'http://en.wikipedia.org/wiki/Elon_Musk',
			'Summary': 'Elon Reeve Musk (born June 28, 1971) is a South African-born Canadian-American business magnate, engineer, inventor and investor. [14] He is the CEO and CTO of SpaceX ...',
			'Title': 'Elon Musk - Wikipedia, the free encyclopedia'
		},
		{
			'URL': 'http://dictionary.reference.com/browse/musk',
			'Summary': 'noun 1. a substance secreted in a glandular sac under the skin of the abdomen of the male musk deer, having a strong odor, and used in perfumery. 2. an artificial ...',
			'Title': 'Musk | Define Musk at Dictionary.com'
		},
		{
			'URL': 'https://www.facebook.com/MUSKmeat',
			'Summary': "ANNOUNCING HOLY MOUNTAIN'S FIRST EVER SUMMER SALE Summer is winding down and we need to make room for the Dust and Chime records coming this Fall. 15% off EVERYTHING ...",
			'Title': 'MUSK'
		},
		{
			'URL': 'https://twitter.com/ElonMusk',
			'Summary': u'1,349 tweets \u2022 165 photos/videos \u2022 2.64M followers. "Dragon 2 is designed to land on any surface (liquid or solid) in the solar system. Am glad to see people ...',
			'Title': 'Elon Musk (@elonmusk) | Twitter'
		},
		{
			'URL': 'http://www.merriam-webster.com/dictionary/musk',
			'Summary': 'Definition of MUSK for Kids: a strong-smelling material that is used in perfumes and is obtained from a gland of an Asian deer (musk deer) or is prepared artificially',
			'Title': 'Musk | Definition of musk by Merriam-Webster'
		},
		{
			'URL': 'http://www.fragrantica.com/notes/Musk-4.html',
			'Summary': 'Musk is a whole class of fragrant substances used as base notes in perfumery. This wonderful animalistic note creates a groundwork on which the rest of the aromatic ...', 'Title': 'Musk perfume ingredient, Musk fragrance and essential oils ...'}, {'URL': 'http://ghr.nlm.nih.gov/gene/MUSK', 'Summary': u"The official name of this gene is \u201cmuscle, skeletal, receptor tyrosine kinase.\u201d MUSK is the gene's official symbol. The MUSK gene is also known by ...",
			'Title': 'MUSK - muscle, skeletal, receptor tyrosine kinase ...'
		},
		{
			'URL': 'http://www.amazon.com/s?ie=UTF8&page=1&rh=n%3A3760911%2Ck%3Aperfume%20musk',
			'Summary': 'Online shopping from a great selection at Beauty Store. ... Avany 100% Pure Uncut Alcohol Free Roll on Body Oil Perfume and Colonge, Egyptian Musk 0.33oz', 'Title': 'Amazon.com: perfume musk: Beauty'}, {'URL': 'http://www.kiehls.com/collections/musk', 'Summary': "Musk by Kiehl's Since 1851. Perfume fragrance essential oil roll on and spray. Eau de toilette fragrances, shower gel, body wash, perfumed lotion and moisturizer.",
			'Title': 'Musk - Fragrance Oil, Perfume & Eau de Toilette Spray ...'
		}
	]
	'''
	#feedbacks is of the following form:
	#['N', 'Y', 'N', 'N', 'Y', 'N', 'N', 'N', 'N', 'N']

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
		feedbacks.append(raw_input("Relevant (Y/N)?"))
	return feedbacks

def printFeedbackSummary(feedbacks, precision, query):
	prec = feedbacks.count('Y') * 1.0 / len(feedbacks)
	cont = False
	print "====================="
	print "FEEDBACK SUMMARY"
	print "Query: " + " ".join(query)
	print "Precision: " + str(prec)
	if prec == 0:
		print "No relevant results among the top-10 pages, done"
	elif prec < float(precision):
		print "Still below the desired precision of " + str(precision)
		cont = True
	else:
		print "Desired precision reached, done"
	return cont

def main():
	#Handle options
	accountKey = sys.argv[1]
	precision = sys.argv[2]
	query = sys.argv[3:len(sys.argv)]	
	cont = True
	#Loop until the precision target is reached
	while cont:
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

		#Print feedback summary
		cont = printFeedbackSummary(feedbacks, precision, query)
		#if cont:
		#	query = updateQuery(results, feedbacks)

if __name__ == "__main__":
	main()