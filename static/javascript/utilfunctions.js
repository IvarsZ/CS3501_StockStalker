function updateStockList(tableid,tickerlist){
    
    var jsonLocation = "/stockdata/current/"+tickerlist+"/";
    console.log(jsonLocation);

    d3.json(jsonLocation, function(data){
        data.forEach(function(d){

            console.log(d);
            var sym = String(d.symbol).replace(new RegExp('\\.','g'),'\\.');
            var id = '#'+tableid+'_'+sym+'_'; 
            
            console.log("Formatting "+d.symbol+" into "+id);

            d3.select(id+'current')
                .html(format(d.lasttradepriceonly,2,' ')); 
            d3.select(id+'change')
                .html(colourFormat(d.change, format(d.change, 2)+' ('+d.percentchange+')')); 
            d3.select(id+'volume')
                .html(d3.format(",d")(d.volume)); 
        });
    });
}


/*
 * Functions to add/remove stocks to/from profile.
 */
function addStock(ticker){
    request('add', ticker);
}
function removeStock(ticker){
    operation = request('remove', ticker); 
}
function request(action, ticker){
    
    jsonLocation = '/stockstalker/'+action+'/'+ticker+'/';
    console.log(jsonLocation);

    return d3.json(jsonLocation, function(data){

        // Try to update the table
        try {
            if(data.result == true){
                
                remove = document.getElementById(ticker+'_row')
                container = remove.parentNode;
                container.removeChild(remove);
                N = container.childNodes.length;
                console.log(N);

                if(N < 5){ // Good bit of magic numbers happening
                    
                    table = document.getElementById('watchlist')
                    tableparent = table.parentNode;
                    tableparent.removeChild(table);

                    oldcontents = tableparent.innerHTML;
                    tableparent.innerHTML = "No tracked stocks."+oldcontents;

                } else {
                    console.log("Still stuff in table : "+N);
                }
            } 
        } catch (e){
            console.log("Could not update table: "+e.message);
        }
        
        // Try to update the button
        try{
            if(data.result == true){
                toggleButton();
            } else {
                document.getElementById('addremovefeedback').innerHTML = data.message; 
            }
        } catch (e){
            console.log("Could not toggle button: "+e.message);
        }

        return data;
    });
}

function formatChange(num, precision){
    return formatGeneral(num, precision, '+');
}

function format(num, precision){
    return formatGeneral(num, precision, ' ');
}

function formatGeneral(num, precision, prefix){
    var f = d3.format(prefix+',.'+precision+'f');
    return f(num);
}

function colourFormat(value, text){
    if(Number(value) < 0){
        colour = '#C02702';
    } else {
        colour = 'green';
    }

    return '<span style="color: '+colour+';">'+text+'</span>';
}
function escapeNan(input){
    if (input=='None'){
        return 'N/A';
    } else {
        return format(input, 2);
    }
}

/*
 * Update table on stock page
 */
function updateStockData(ticker, currency){
    
    jsonLocation = '/stockdata/current/'+ticker+'/';

    return d3.json(jsonLocation, function(data){


        data.forEach(function(d){
            
            var sym = String(ticker).replace(new RegExp('\\.','g'),'\\.');
            var id = '#'+sym+'_'; 
            
            // Define an array of properties which will be inserted automatically.
            var fields = new Array(
                'lasttradepriceonly',
                'change', 
                'volume', 
                'open', 
                'previousclose',
                'marketcapitalization',
                'peratio',
                'pricebook',
                'pegratio',
                'divy',
                'adivy',
                '50avg',
                '200avg');

            var values = new Array(
                currency+' '+format(d.lasttradepriceonly, 2),
                colourFormat(d.change, formatChange(d.change,2)+' ('+d.percentchange+')'),
                d3.format(",d")(d.volume),
                currency+' '+format(d.open, 2),
                currency+' '+format(d.previousclose, 2),
                d.marketcapitalization,
                format(d.peratio, 2),
                escapeNan(d.pricebook),
                escapeNan(d.pegratio),
                escapeNan(d.dividendyield),
                format(d.dividendshare, 2),
                colourFormat(d.changefromfiftydaymovingaverage, format(d.fiftydaymovingaverage, 2)+' ('+d.percentchangefromfiftydaymovingaverage+')'),
                colourFormat(d.changefromtwohundreddaymovingaverage, format(d.twohundreddaymovingaverage, 2)+' ('+d.percentchangefromtwohundreddaymovingaverage+')') 
            );

            for(i = 0; i < fields.length; i++){
                d3.select(id+fields[i])
                    .html(values[i]);
            }

        });
        return data;
    });

}


function startUpdateLoop(ticker, currency) {

    function upd() {
        console.log("Async. upd (" + ticker + ")");
        updateStockData(ticker, currency);
    }

    upd(); // First update
    setInterval(upd, 30 *1000); // Rest of updates
}

