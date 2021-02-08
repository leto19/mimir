entype2idx = {"PERSON": 1,"LOC": 2, "ORG": 3}

def make_ent2idx(summary, word2ent):
	"""
	
	"""
	summary_tokens = summary.split(" ")
	idx = 1
	ent2idx = {}
	for token in summary_tokens:
		if token in word2ent:
			ent = word2ent[token]
			if ent not in ent2idx:
				ent2idx[ent] = idx
	return(ent2idx)

keywords = get_keywords(question)

def get_entidx_feat(word, word2ent, ent2idx):
	ent = word2ent.get(word,0)
	if ent == 0:
		return 0
	return(ent2idx[ent])

def get_enttype_feat(word, word2ent, enttype2idx):
	ent = word2ent.get(word,0)
	if ent == 0:
		return 0
	return(enttype2idx[ent.class_string])

def count_keywords(sents, keywords):
	#To do: add in some preprocessing in here (e.g. stemming)
	sents = sents.split(" ")
	keywords_only = [[w for w in sent if w in keywords] for sent in sents]
	return(sum([len(kws) for kws in keywords_only]))


def get_kf_feat(word, word2ent, keywords):
	"""Returns the averaged frequency for all question keywords inside the "sents" attribute of
	a Named Entity object (The "sents" attribute is just a list containing all
	sentences with that Named Entity from the full text)
		""" 
	keyword_freq = 0

	keyword_freq = count_keywords(entity.sents, keywords)
	
	normalized_freq = keyword_freq / sum([len(sent) for sent in entity.sents]) 
				#Normalize by word count of entity.sents
	
	return(normalized_freq)

summary_tokens = tokenize(summary)

keyword_freq_feature = []

for token in summary_tokens:
	named_entity = match_named_entity(word)
	if named_entity: #if the name matches our pre-created list of name variants for NE objects
		feat = get_keyword_freq(keywords, named_entity)
		keyword_freq_feature.append(feat)
	else:
		keyword_freq_feature.append(0) #if it's just a non-NE word, we return a 0 for this feature
