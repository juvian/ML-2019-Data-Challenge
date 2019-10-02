import pandas as pd
import unicodedata
import re
from collections import Counter, defaultdict
from itertools import islice
import json
from math import log2
from pathlib import Path
from math import floor


PATH = Path('.')


def normalize_title(title):
    s = re.sub(r'[^a-zA-Z0-9ñç%. ]', ' ', unicodedata.normalize('NFKD', title.lower()).encode('ascii', 'ignore').decode("utf-8"))
    s = re.sub(r'[\d]+', "1", s)
    s = re.sub(r's |s$', ' ', s)
    s = re.sub(r' +', ' ', s)
    s = re.sub(r'(1 )+', '1 ', s)
    return re.sub(r'o |o$', 'a ', s).strip()


if not (PATH / 'train_prepro.csv').exists():
	df = pd.read_csv('train_small.csv')
	print("1")
	df['title'] = df.title.apply(normalize_title)
	print("2")
	df = df[~df.title.isna() & (df.title != 'nan') & (df.title != '')]
	df.to_csv(PATH / 'train_prepro.csv', index=False)

df = pd.read_csv('train_prepro.csv')	

if not (PATH / 'important.json').exists():
	d = defaultdict(Counter)

	def process(r):
		ws = r['title'].split(' ')

		for w in ws:
			d[w][r['category']] += 1

	print("a")
	df.apply(process, axis=1)

	word_importance = dict()

	for w, c in d.items():
		importance = 0
		count = 0

		for x in c.most_common():
			if x[1] < 10:
				break
			count += 1	
			importance += x[1]

		if count > 0:	
			word_importance[w] = importance / (count**2)



	with open("important.json", "w") as f:
		json.dump(word_importance, f, indent=4)

with open("important.json", "r") as f:
	word_importance = json.load(f)		


if not (PATH / 'vocab.json').exists():

	cats = df['category'].nunique()
	total = 60000 - 15 * cats
	carry = 0
	important = set()
	ordered = []

	for index, rows in sorted(df.groupby('category'), key=lambda x: len(x[1]), reverse=True):
		available = 15 + floor(total * len(rows) / len(df)) + carry
		words = defaultdict(int)

		def process(r):
			ws = r.split(' ')
			weights = [word_importance.get(x, 0) for x in ws]
			total = sum(weights)

			for w, wei in zip(ws, weights)[0:len(ws)//2]:
				words[w] += wei / total if total > 0 else 1/len(ws)

		rows['title'].apply(process)

		for w in sorted(words.keys(), key = lambda x: words[x], reverse=True):
			if w not in important:
				if w == "de":
					print(words)
					exit()
				important.add(w)
				ordered.append(w)
				available -= 1
				if available == 0:
					break

		carry = available


	for w in sorted(word_importance, key=lambda x: word_importance[x], reverse=True):
		if w not in important:
			important.add(w)
			ordered.append(w)
			if len(important) == 60000:
				break


	with open('vocab.json', "w") as f:
		json.dump(ordered, f)
					








