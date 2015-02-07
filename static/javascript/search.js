
stockSymbols = [];


function clearValue(element){
    element.value = "";
}

// Called on body click
function hideResults(e, id){
    // Unless it was the searchbox being clicked, the results table will
    // disappear.
    if (e.srcElement.id != 'searchbox'){
        document.getElementById(id).innerHTML = '';
    }
}

// Called once, on body load
function loadSearchData(){
    jsonLocation = '/stockdata/allstocks/';
    d3.json(jsonLocation, function(data){
        data.forEach(function(d){
            d.name = d.name.replace(/ PLC$/,"");
        });
        stockSymbols = data;
    });
}

function containsAll(terms) {
    return function(someString) {
        var someString = someString.toLowerCase();
        return terms.every(function(term) {
            // Check if term is found
            return someString.indexOf(term.toLowerCase()) > -1;
        });
    }
}
function symbolContainsAll(terms) {
    return function(symbol) {
        return [symbol.ticker, symbol.name].some(containsAll(terms));
    }
}

var MAX_RESULTS       = 12; // Show max this many results
var NAME_CUTOFF_CHARS = 18; // After this many chars, replace with "..."

function updateResults(searchTerms) {
    var isEmpty = false;
    var matchingSymbols = [];
    if (searchTerms != "") {
        isEmpty = false;
        var searchTerms = searchTerms.toLowerCase().split(" ");
        matchingSymbols = stockSymbols.filter(symbolContainsAll(searchTerms));
    } else {
        isEmpty = true;
    }
    var part1 = '<td><a href="/stockstalker/stock/';
    var part2 = '/">';
    var part3 = '</a></td><td><a href="/stockstalker/stock/';
    var part4 = '/">';
    var part5 = '</a></td><td class="faint"><a href="/stockstalker/stock/';
    var part6 = '/">';
    var part7 = '</a></td>';


    // We only want the first results
    listedSymbols = matchingSymbols.slice(0, MAX_RESULTS);

    var table = document.getElementById('searchResults');

    // Remove all rows in the table
    while(table.childNodes.length > 0){
        table.removeChild(table.childNodes[0]);
    }
    
    // Add a row for each symbol
    for (i=0; i<listedSymbols.length; i++){

        var row = document.createElement('tr');
        table.appendChild(row);

        var d = listedSymbols[i];
        row.innerHTML = part1 + d.ticker + part2
            + d.ticker + part3 + d.ticker + part4
            + (d.name.length <= NAME_CUTOFF_CHARS + 3 ? d.name : d.name.substring(0,NAME_CUTOFF_CHARS) + "...") + part5 + d.ticker + part6
            + d.index + part5;

        // Animate results, but only if this is being done after the very first
        // character of input.
        if (this.previousWasEmpty) {
            d3.select(row.parent).style("opacity", 0).transition().duration(250).style("opacity", 0.5).delay(i*10);
            d3.select(row).style("opacity", 0).transition().duration(250).style("opacity", 1).delay(i*10);
        }
    }

    this.previousWasEmpty = isEmpty;


    // {{{ Old code
    /*** *** ***

    // THIS DIDN'T WORK. (The above code is messier, but DOES.)
    // WTF MATE? https://www.youtube.com/watch?v=kCpjgl2baLs

    var res = d3.select("#searchResults").selectAll("tr");

    res.data(listedSymbols)
      .enter().append("tr")
        .html(function(d) {
            return part1 + d.ticker + part2
            + d.ticker + part3 + d.ticker + part4
            + (d.name.length <= 23 ? d.name : d.name.substring(0,20) + "...") + part5 + d.ticker + part6
            + d.index + part5; });

    var res = d3.select("#searchResults").selectAll("tr");
    res.data(display).exit().remove();
    
    *** *** ***/
    // }}}
}

// Needed to check for whether the previous state of the input box was empty
updateResults.previousWasEmpty = true;
