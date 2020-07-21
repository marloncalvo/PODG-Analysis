import random
import re
from functools import reduce
import heapq

common_words = {
	"the",
	"of",
	"to",
	"and",
	"a",
	"in",
	"is",
	"it",
	"you",
	"that",
	"he",
	"was",
	"for",
	"on",
	"are",
	"with",
	"as",
	"I",
	"his",
	"they",
	"be",
	"at",
	"one",
	"have",
	"this",
	"from",
	"or",
	"had",
	"by",
	"not",
	"word",
	"but",
	"what",
	"some",
	"we",
	"can",
	"out",
	"other",
	"were",
	"all",
	"there",
	"when",
	"up",
	"use",
	"your",
	"how",
	"said",
	"an",
	"each",
	"she",
	"which",
	"do",
	"their",
	"time",
	"if",
	"will",
	"way",
	"about",
	"many",
	"then",
	"them",
	"write",
	"would",
	"like",
	"so",
	"these",
	"her",
	"long",
	"make",
	"thing",
	"see",
	"him",
	"two",
	"has",
	"look",
	"more",
	"day",
	"could",
	"go",
	"come",
	"did",
	"number",
	"sound",
	"no",
	"most",
	"people",
	"my",
	"over",
	"know",
	"water",
	"than",
	"call",
	"first",
	"who",
	"may",
	"down",
	"side",
	"been",
	"now",
	"find"
}

def main():
	tokens = parse_file('174.txt')
	tokens_with_ends = parse_file_with_ends('174.txt')
	print(f'Total Number of Words: {get_total_number_of_words(tokens)}')
	print(f'Total Number of Unique Words: {get_total_unique_words(tokens)}')
	print(f'20 most frequently used words: {get_20_most_frequent_words(tokens)}')
	print(f'20 most frequently used words trimmed: {get_20_most_frequent_words_filtered(tokens)}')
	print(f'20 least frequently used words: {get_20_least_frequent_words(tokens)}')
	print(f'Frequency by chapter: {get_freq_by_chapter("love", tokens)}')
	# print(f'Chapter of quote: {get_chapter_of_quote("The highest as the lowest form of criticism is a mode of autobiography", tokens)}')
	# print(f'All sentences from the: {generate_sentence(tokens_with_ends)}')
	# print(f'Sentence completion: {sentence_completion("The", tokens_with_ends)}')
	# print(f'Closest match: {closest_matching_quote("The two men sauntered", _token_to_line(tokens_with_ends))}')

def _token_to_line(tokens):
	lines = []
	cur_line = ""
	for token in tokens:
		if re.match(r'[\.?!]', token):
			lines.append(cur_line.rstrip())
			cur_line = ""
		else:
			cur_line += token + " "

	return lines

def generate_sentence(tokens):
	g = {}
	prev = None
	for i, token in enumerate(tokens):
		if re.match(r'[\.?!"]', token):
			prev = None

		if prev:
			arr = []
			
			if prev not in g:
				g[prev] = arr
			else:
				arr = g[prev]

			arr.append(token)
			
		prev = token

	seen = set()
	cur = "The"
	word = ""

	for i in range(20):
		word += cur + " "
		arr = g[cur]
		cur = arr[random.randint(0, len(arr)-1)]

	return word

"""  " some" -> "words" -> "blah"
     / 
"The"      -> "dog"
    \     /
    "grey" -> "cat" 
    "green" 
"""

class Trie():
	def __init__(self):
		self.children = [None for i in range(256)]
		self.is_word = False
		self.full_sentence = False

	def __str__(self):
		res = []
		for i, child in enumerate(self.children):
			if child:
				res.append(chr(i))
				res.append(str(child))

		return str(res)
		
def closest_matching_quote(quote, lines):
	diff = 99999999999
	res = None

	for line in lines:
		d = _dl_distance(line, quote)
		if  d < diff:
			diff = d
			res = line

	return res


def _dl_distance(a, b):
	d = {}
	l_a = len(a)
	l_b = len(b)
	for i in range(-1, l_a+1):
		d[(i,-1)] = i + 1
	for i in range(-1, l_b+1):
		d[(-1,i)] = i + 1

	for i in range(l_a):
		for j in range(l_b):
			if a[i] == b[j]:
				cost = 0
			else:
				cost = 1

			d[(i,j)] = min(
				d[(i-1, j)] + 1,
				d[(i,j-1)] + 1,
				d[(i-1,j-1)] + cost,
			)

			if i and j and a[i] == b[j-1] and a[i-1] == b[j]:
				d[(i,j)] = min(d[(i,j)], d[i-2, j-2] + cost)

	return d[l_a-1, l_b-1] 

def sentence_completion(word, tokens):
	root = Trie()
	prev = None
	cur = root
	# for each character in the token
	#    we will create a reference to a new trie from c
	#    unless we are at last character, where we will make is_word = True
	#    if we are a period, then make the prev token a full_sentence = True
	for token in tokens:
		if re.match(r'[\.?!]', token):
			cur.children[ord(c)] = Trie()
			cur.children[ord(c)].full_sentence = True
			prev = None
			cur = root

		else:
			for c in token:
				if not cur.children[ord(c)]:
					cur.children[ord(c)] = Trie()
				prev = cur
				cur = cur.children[ord(c)]

			cur.is_word = True

	cur = root
	for c in word:
		cur = cur.children[ord(c)]

	word = word.split()
	return _print_words(cur, word)

def _print_words(trie, word, start=True):
	if trie.full_sentence:
		return [''.join(word[:len(word)-2])]
	
	res = []
	for i, child in enumerate(trie.children):
		if child:
			if trie.is_word and not start:
				word.append(' ')
			word.append(chr(i))
			res.extend(_print_words(child, word, False))
			word.pop()
			if trie.is_word and not start:
				word.pop()
	return res
	
def get_chapter_of_quote(quote, tokens):
	quote_split = re.findall(r'[a-z|A-Z|0-9]+', quote)
	cur_chapter = 0
	for i, token in enumerate(tokens):
		if 'CHAPTER' in token and re.match(r'\d+', tokens[i+1]):
			cur_chapter += 1
		elif quote_split == tokens[i:i+len(quote_split)]:
			return cur_chapter

	return -1
			
def get_freq_by_chapter(word, tokens):
	freq = []
	cur_freq = 0
	for i, token in enumerate(tokens):
		if word in token:
			cur_freq += 1
		elif 'CHAPTER' in token and re.match(r'\d+', tokens[i+1]):
			freq.append(cur_freq)
			cur_freq = 0

	return freq
	
def get_20_most_frequent_words(tokens):
	words_dict = get_words_dict(tokens)
	heap = []
	heapq.heapify(heap)
	for word in words_dict:
		if _is_word(word):
			heapq.heappush(heap, (-1 * words_dict[word], word))

	res = []
	for i in range(20):
		item = heapq.heappop(heap)
		res.append((item[1], item[0]*-1))

	return res

def get_20_most_frequent_words_filtered(tokens):
	words_dict = get_words_dict(tokens)
	heap = []
	heapq.heapify(heap)
	for word in words_dict:
		if _is_word(word) and not _is_common_word(word):
			heapq.heappush(heap, (-1 * words_dict[word], word))

	res = []
	for i in range(20):
		item = heapq.heappop(heap)
		res.append((item[1], item[0]*-1))

	return res

def get_20_least_frequent_words(tokens):
	words_dict = get_words_dict(tokens)
	heap = []
	heapq.heapify(heap)
	for word in words_dict:
		if _is_word(word):
			heapq.heappush(heap, (words_dict[word], word))

	res = []
	for i in range(20):
		item = heapq.heappop(heap)
		res.append((item[1], item[0]))

	return res

def get_total_unique_words(tokens):
	words_dict = get_words_dict(tokens)
	return len(words_dict)
	
def get_total_number_of_words(tokens):
	return reduce(lambda x, y: x + 1 if _is_word(y) else x, tokens, 0)

def parse_file(file_path):
	tokens = []
	with open(file_path, 'r') as txt_file:
		tokens = _tokenfy_from_stream(txt_file)

	return tokens

def parse_file_with_ends(file_path):
	tokens = []
	with open(file_path, 'r') as txt_file:
		tokens = _tokenfy_from_stream_with_ends(txt_file)

	return tokens

def _tokenfy_from_stream(stream):
	res = []
	cur_token = ''
	lines = '\n'.join(stream.readlines())
	groups = re.findall(r'[a-z|A-Z|0-9]+\'{0,1}[a-z|A-Z|0-9]+|[a-z|A-Z|0-9]+', lines)
	return list(groups)

def _tokenfy_from_stream_with_ends(stream):
	res = []
	cur_token = ''
	lines = '\n'.join(stream.readlines())
	groups = re.findall(r'[a-z|A-Z|0-9|\']+|[\.\?!;\:]+|"', lines)
	return list(groups)

def _tokenfy_from_stream_with_ends_spaces(stream):
	res = []
	cur_token = ''
	lines = '\n'.join(stream.readlines())
	groups = re.findall(r'[a-z|A-Z|0-9|\']+|[\.\?!;\:]+|"| ', lines)
	return list(groups)

def get_words_dict(tokens):
	res = {}
	for token in tokens:
		token = token.lower()
		if token in res:
			res[token] = res[token] + 1
		else:
			res[token] = 1

	return res

def _new_cmp(self,a,b):
	return a[1] > b[1]

def _new_cmp2(self,a,b):
	return a[1] < b[1]

def _is_common_word(s):
	return s in common_words

def _is_word(s):
	return re.search('[A-Za-z]', s) != None

if __name__ == "__main__":
	main()
