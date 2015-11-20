TEAM
======
Alice Berard (aab2227)
Esha Chakraborty (ec3074)

Files
=======
proj1.py

stopwords.txt

README.md

transcripts_tajmahal

transcripts_musk

transcripts_gates

Run the program
================
python proj1.py BingAccountKey precision@10 query

Internal Design
================
The internal design of the project can be explained in the form of a pseudo code as follows:-

while current_precision < desired_precision:
	Query the bing API with API key and query
	Retrieve URL, Title and Summary for each result

	if len(results) < 10
		terminate

	relevant_results = []
	non_relevant_results = []
	for result in results:
		if user_feedback == yes:
			relevant_results.append(result)
		else:
			non_relevant_results.append(result)

	if length(relevant_results)/10 == desired_precision:
		terminate
	if len(relevant_results) == 0:
		terminate
	generate new query term
	update query with new query term

Query Modification
===================
1. Calculating the Document vectors:
	tf-idf scores computed: 
		The term frequency (tf) of each term of the document is calculated. The idf is then computed as log(N/df). Document Score is calculated as tf*idf. The document score vector is then normalized to create the document vector.

2. Our code then uses the standard Rocchio Algorithm to perform query modification. The specific function to handle this task takes the 3 parameters (alpha: 1.0, beta: 0.75 and gamma: 0.15) that act as the weights corresponding to the old query, the normalized related documents and the normalized non-related documents.


Other Information
==================