import pandas as pd
from collections import defaultdict, Counter
import json
import unidecode

df = pd.read_csv('categories.csv')

cats = dict()

for group_name, group in df.groupby('category'):
	d = Counter()
	for index, row in group.iterrows():
		d[row['category 0']] += 1
	cats[group_name] = 	unidecode.unidecode(d.most_common(1)[0][0])

replacements = {
	'Deportes y Fitness': 'Esportes e Fitness',
	'Electrodomesticos y Aires Ac.': 'Eletrodomesticos',
	'Herramientas y Construccion': 'Ferramentas e Construcao',
	'Juegos y Juguetes': 'Brinquedos e Hobbies',
	'Hogar, Muebles y Jardin': 'Casa, Moveis e Decoracao',
	'Accesorios para Vehiculos': 'Acessorios para Veiculos',
	'Instrumentos Musicales': 'Instrumentos Musicais'
}

for cat in cats:
	if cats[cat] in replacements:
		cats[cat] = replacements[cats[cat]]

c = Counter(cats.values())
print(c, len(c))

with open("main_categories.json", "w") as f:
	json.dump(cats, f, indent=4)