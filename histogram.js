let fs = require('fs');

let data = JSON.parse(fs.readFileSync('data.json'));

let qty = {}

for (let word in data) {
	let count = Object.keys(data[word]).length;
	qty[count] = qty[count] || []
	qty[count].push(word)
}

fs.writeFile('histogram.json', JSON.stringify(qty, null, 4), 'utf8', (err) => console.log(err));