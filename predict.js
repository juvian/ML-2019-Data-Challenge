let fs = require('fs');
let es = require('event-stream');
let tokenize = require('./utils').tokenize;

let data = JSON.parse(fs.readFileSync('data.json'));
let categories = JSON.parse(fs.readFileSync('mapping.json'));
let counts = JSON.parse(fs.readFileSync('counts.json'));

let count = 0;
let correct = 0;
let incorrect = 0;
let errors = [];


var s = fs.createReadStream('train_small.csv')
    .pipe(es.split())
    .pipe(es.mapSync(function(line){

    	let cols = line.split(',');
    	let category = categories[cols[cols.length - 1]];

        if (count > 0) {
        	let probs = {}

        	tokenize(cols[0]).filter(w => data.hasOwnProperty(w)).forEach(w => {
        		let suma = Object.keys(data[w]).reduce((a, b) => a + (b == 'T' ? 0 : data[w][b]  / counts[b]), 0);

        		for (cat in data[w]) {
        			if (cat == 'T') continue;
        			probs[cat] = probs[cat] || 0
        			probs[cat] += (data[w][cat] / counts[cat]) / suma
        		}
        	})

        	let mostLikely = Object.keys(probs).sort((a, b) => probs[b] - probs[a]).slice(0, 7);

        	if (mostLikely.includes(category.toString())) correct++
         	else {
         		incorrect ++
         		errors.push({t: cols[0], p: mostLikely.map(m => ({c: m, p: probs[m]})), o: category, op: probs[category]})
         	}

        }

        count++;
    }).on('error', function(err){
        console.log('Error while reading file.', err);
    })
    .on('end', function(){
    	console.log("end", correct, incorrect)
    	fs.writeFile('errors.json', JSON.stringify(errors, null, 4, 'utf8', (err) => console.log(err)))
    }));