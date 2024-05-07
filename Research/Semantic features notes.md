# Semantic features Notes

Identifying and Protecting Personal Information in Email Search
Lewis Munro
2469780M
Graham McDonald

word embedding - vector space word representations, eadh dimension maps to a latent feature of the word.
	- semantically similar terms are poistioned close to each opther in the vector space
	- directionality between multiple terms in the vector space can encode relations between the terms. 

Berardi et al - optimise the cost effectiveness of sensitivity reviewers.
	- deplyed a utility theoretic ranking approach for semi-automatic text classification.
	- ranks documents by the expected gain in accuracy, has a reviewer correct miss-classified instances
		- if a reviewer validates a document tha the classifier was unsure about then overall accuracy
		  increases.
Mcdonald et al - used POS n-grams with a high sensitivity load to train a condition random fields sequence tagger

Term features - uses the frequencies of terms in documents to train classifiers.
	- n-gram term features - a tuple of n contiguous terms from a larger ordered sequence of terms.

