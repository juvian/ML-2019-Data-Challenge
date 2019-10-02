import pandas as pd
import unicodedata
import re
from collections import Counter, defaultdict
from itertools import islice
import json
from math import log2
from pathlib import Path
from math import floor, sqrt

def average(n):
	if not hasattr(average, 'l'):
		average.l = []
	average.l.append(n)	
	return(sum(average.l) / len(average.l))

print(average(10))
print(average(3))

exit()	


PATH = Path('.')


with open("important.json", "r") as f:
	word_importance = json.load(f)	

with open("main_categories.json", "r") as f:
	main_categories = json.load(f)		

df = pd.read_csv('train_prepro.csv')
df.category = df.category.map(main_categories)

if not (PATH / 'word_counts.json').exists():
	words = defaultdict(Counter)
	for index, rows in sorted(df.groupby('category'), key=lambda x: len(x[1]), reverse=True):
		def process(t):
			for word in set(t.split(' ')):
				if word in word_importance:
					words[word][index] += 1

		rows['title'].apply(process)

	for word in words.keys():
		total = sum(words[word].values())
		for cat in words[word].keys():
			words[word][cat] /= total	
		
	with open(PATH / 'word_counts.json', 'w') as f:
		json.dump(words, f, indent=4)	


with open("word_counts.json", "r") as f:
	word_counts = json.load(f)			


def predict(title):
	probs = defaultdict(int)
	ws = title.split(' ')
	seen = set()
	for idx, word in enumerate(ws):
		if word in word_counts and word not in seen and word in word_importance:
			seen.add(word)
			for cat in sorted(word_counts[word]):
				probs[cat] += log2(1+word_importance[word]) * (100+word_counts[word][cat])
	if len(probs) == 0:
		return "unknown"			
	return max(probs, key=probs.get)

df['prediction'] = df.title.apply(predict)

print((df.prediction != df.category).value_counts())
print(df[['prediction', 'category']])			

df[~(df.prediction == df.category)].to_csv(PATH / 'prediction.csv', index=False)
