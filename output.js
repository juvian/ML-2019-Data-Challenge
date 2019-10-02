let fs = require('fs');
let es = require('event-stream');
let tokenize = require('./utils').tokenize;

let data = JSON.parse(fs.readFileSync('data.json'));
let categories = JSON.parse(fs.readFileSync('mapping.json'));
let counts = JSON.parse(fs.readFileSync('counts.json'));

let count = 0;

let output = ['id,category'];
let catTrans = {}

for (let cat in categories) catTrans[categories[cat]] = cat;

var s = fs.createReadStream('test.csv')
    .pipe(es.split())
    .pipe(es.mapSync(function(line){

    	let cols = line.split(',');

        if (count > 0 && cols.length > 2) {
        	let probs = {}

        	let ws = tokenize(cols[1]).filter(w => data.hasOwnProperty(w));

            ws.forEach(w => {
        		let suma = Object.keys(data[w]).reduce((a, b) => a + (b == 'T' ? 0 : data[w][b]  / counts[b]), 0);

        		for (cat in data[w]) {
        			if (cat == 'T') continue;
        			probs[cat] = probs[cat] || 0
        			probs[cat] += (data[w][cat] / counts[cat]) / suma
        		}
        	})

        	let mostLikely = Object.keys(probs).sort((a, b) => probs[b] - probs[a]).slice(0, 5);

            let penalty = {}

            
            ws.forEach(w => {
                for (cat in mostLikely) {
                    penalty[cat] = penalty || 0
                    penalty[cat] += data[w].hasOwnProperty(cat) && data[w][cat] / counts[cat] > 0.01 ? 0 : 1;
                }
            })
            
            mostLikely = mostLikely.sort((a, b) => penalty[a] - penalty[b]);

            output.push((count - 1) + ',' + (mostLikely.length ? catTrans[mostLikely[0]] : "NOTEBOOKS"))
        }

        count++;
    }).on('error', function(err){
        console.log('Error while reading file.', err);
    })
    .on('end', function(){
    	console.log("end")
    	fs.writeFile('output.csv', output.join('\n'), 'utf8', (err) => console.log(err))
    }));