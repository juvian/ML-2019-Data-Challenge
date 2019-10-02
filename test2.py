import pandas as pd
import requests
from collections import defaultdict, Counter

df = pd.read_csv('categories.csv')

d = defaultdict(Counter)

for index, row in df.iterrows():
	print(index)
	if 'category 0' not in row or len(str(row['category 0'])) < 4:
		try:
			site = 'MLA' if row['language'] == 'spanish' else 'MLB'
			r = requests.get(f'https://api.mercadolibre.com/sites/{site}/category_predictor/predict?title={row["title"]}').json()
			for i, c in enumerate(r['path_from_root']):
				df.loc[index,'category ' + str(i)] = c['name']
		except Exception as ex:
			print(ex)

	if index % 100 == 5:
		df.to_csv('categories.csv', index=False)		

df.to_csv('categories.csv', index=False)				