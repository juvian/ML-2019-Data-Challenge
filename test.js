let fs = require('fs');
let es = require('event-stream');
let tokenize = require('./utils').tokenize;

let words = {}
let count = 0;
let banned = new Set()
let catCounts = {}

function Set_toJSON(key, value) {
  if (typeof value === 'object' && value instanceof Set) {
    return [...value];
  }
  return value;
}

function isInteresting(w) {
    if (Object.values(w).length < 50) return true;
    let arr = Object.keys(words[w]).map(c => words[w][c] / catCounts[c]).sort();
    return Math.max.apply(null, Object.values(words[w])) - Math.min.apply(null, Object.values(words[w])) > 10 && arr.reduce((a, b) => a + b, 0) / 2 < arr.slice(-Math.floor(arr.length / 10)).reduce((a, b) => a + b, 0)
}

function end() {
	console.log("end")

    for (let w in words) {
        for (let cat in words[w]) {
            if (words[w][cat] < 10) delete words[w][cat];
        }
        if (isInteresting(w) == false) delete words[w];
    }

    fs.writeFile('data.json', JSON.stringify(words, Set_toJSON), 'utf8', (err) => console.log(err));
    fs.writeFile('mapping.json', JSON.stringify(cats, null, 4), 'utf8', (err) => console.log(err));
    fs.writeFile('counts.json', JSON.stringify(catCounts, null, 4, 'utf8', (err) => console.log(err)))
}
let cats = {}

function numeralize(cat) {
	return cats[cat] = cats[cat] || Object.keys(cats).length + 1;
}

var s = fs.createReadStream('train.csv')
    .pipe(es.split())
    .pipe(es.mapSync(function(line){

    	let cols = line.split(',');
    	let category = numeralize(cols[cols.length - 1]);
        catCounts[category] = catCounts[category] || 0;
        catCounts[category]++

        if (count > 0) {
        	tokenize(cols[0].forEach(w => {
        		if (words.hasOwnProperty(w) == false) {
                    words[w] = {"T": 0};
                }
                words[w][category] = words[w][category] || 0
                words[w][category]++
                words[w]["T"] += 1
        	});
        }
    	count++;
    	if (count % 100000 == 0) console.log(count, Object.keys(words).length)
    })
    .on('error', function(err){
        console.log('Error while reading file.', err);
    })
    .on('end', function(){
    	end()
    })
);
