// Helper functions for smoothly transitioning between full opacity and transparency.
var smoothShow = function(selection) {
    selection.transition().duration(100).style("opacity", 1);
}
var smoothHide = function(selection) {
    selection.transition().duration(100).style("opacity", 0);
}

// Bounding box intersection check
// BBoxes are JS objects with (x,y) as top-left corner and a width and height.
var intersects = function(a, b) {
    // Min is (left|top)most, Max is (right|bottom)most coordinate
    var aMinX = a.x, aMaxX = a.x + a.width,
        aMinY = a.y, aMaxY = a.y + a.height,
        bMinX = b.x, bMaxX = b.x + b.width,
        bMinY = b.y, bMaxY = b.y + b.height;

    if ( aMaxX < bMinX || aMinX > bMaxX ) { return false };
    if ( aMaxY < bMinY || aMinY > bMaxY ) { return false };
    return true;
}

function changeChart(ticker, frequency, currency, years, months, weeks, days) {
    var years = years ? years : 0;
    var months = months ? months : 0;
    var weeks = weeks ? weeks : 0;
    var days = days ? days : 0;

    // Construct dates for NOW and however long ago
    var formatDate = d3.time.format("%Y-%m-%d");
    var dateNow = new Date();
    var dateBefore = new Date();
    dateBefore.setFullYear(
        dateBefore.getFullYear() - years,
        dateBefore.getMonth() - months,
        dateBefore.getDate() - weeks * 7 - days
    );
    var startdate = dateBefore;
    var enddate = dateNow;

    

    // Construct URL
    var jsonLocation = "/stockdata/historical/" + ticker +"/" + formatDate(startdate) + "/" + formatDate(enddate) + "/" + frequency;
    console.log("Requesting for charting: " + jsonLocation);
    var col = { closing:     d3.rgb("#45ADA8")   // green
              , volume:      d3.rgb("#9DE0AD")   // light grey
              , background:  d3.rgb("#ffffff")
              , neutral:     d3.rgb("#547980") } // grey
    var parseDate = d3.time.format("%Y-%m-%d").parse;
    d3.json(jsonLocation, function(data) {
        data.forEach(function(d) {
            console.log(d);
            d.date = parseDate(d.date);
            d.volume = +d.volume;
            d.close = +d.closing;
        });
        d3.select("#graphcontainer svg").remove();
        drawgraph(ticker, startdate, enddate, frequency, currency);
    });
    // XXX This works in jquery to prevent the link click event from happening,
    // but clearly not in d3. Ah well. Workaround necessary.
    return false;
}

function drawgraph(ticker, startdate, enddate, frequency, currency) {

    // XXX Unused parameters
    
    console.log("Drawing graph for "+ticker+".");

    var formatDate = d3.time.format("%Y-%m-%d");
    if (!startdate || !enddate) {
        // Construct dates for NOW and ONE YEAR AGO
        var dateNow = new Date();
        var dateOneYearAgo = new Date();
        dateOneYearAgo.setFullYear(dateOneYearAgo.getFullYear() - 1);
    }

    var startdate = startdate ? startdate : dateOneYearAgo;
    var enddate = enddate ? enddate : dateNow;
    
    // Updates URL for raw data link
    var dlurl = '/stockdata/historical/raw/' + ticker +"/" + formatDate(startdate) + "/" + formatDate(enddate) + "/" + frequency;
    d3.select("#rawlink").attr("href", dlurl);


    // Construct URL
    var jsonLocation = "/stockdata/historical/" + ticker +"/" + formatDate(startdate) + "/" + formatDate(enddate) + "/" + frequency;
    console.log("Requesting for charting: " + jsonLocation);
    var col = { closing:     d3.rgb("#45ADA8")   // green
              , volume:      d3.rgb("#9DE0AD")   // light grey
              , background:  d3.rgb("#ffffff")
              , neutral:     d3.rgb("#547980") } // grey

    // Conventional margins
    var margin = {top: 10, right: 70, bottom: 20, left: 50},
        width = 620 - margin.left - margin.right,
        height = 350 - margin.top - margin.bottom;

    // Root SVG element (with inner marginated inner area)
    var svg = d3.select("#graphcontainer").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .attr("fill", col.background);
    // This filter creates a larger, blurred, white drop shadow at no offset
    // Useful for smoothly occluding background elements when e.g. a chart label
    // is meant to obscure the data underneath.
    var filter = svg.append("svg:defs").append("svg:filter")
        .attr("id", "blurdrop");
    // Dilate to make larger
    filter.append("svg:feMorphology")
        .attr("in", "SourceAlpha")
        .attr("result", "dilated")
        .attr("operator", "dilate")
        .attr("radius", "2.5");
    // Blur
    filter.append("svg:feGaussianBlur")
        .attr("in", "dilated")
        .attr("stdDeviation", 2)
        .attr("result", "blurred");
    // Whiten
    // Linear with slope 0 and intercept at 1 implies f == 1 for all inputs
    var compTransfer = filter.append("svg:feComponentTransfer")
        .attr("result", "colouredBlurred");
    compTransfer.append("feFuncR")
        .attr("type", "linear").attr("slope","0").attr("intercept", 1);
    compTransfer.append("feFuncG")
        .attr("type", "linear").attr("slope","0").attr("intercept", 1);
    compTransfer.append("feFuncB")
        .attr("type", "linear").attr("slope","0").attr("intercept", 1);
    // Merge original onto the drop shadow
    var feMerge = filter.append("svg:feMerge");
    feMerge.append("svg:feMergeNode").attr("in", "colouredBlurred");
    feMerge.append("svg:feMergeNode").attr("in", "SourceGraphic");

    // Date parser function for YYYY-MM-DD date strings
    var parseDate = d3.time.format("%Y-%m-%d").parse;
    // Date formatter
    var formatDate = d3.time.format("%e %b %Y");

    d3.json(jsonLocation, function(data) {
        data.forEach(function(d) {
            console.log(d);
            d.date = parseDate(d.date);
            d.volume = +d.volume;
            d.close = +d.closing;
        });
        if (data.every(function(d){return ! d === undefined})) {
            console.log("shit!");
        }
        var lookupTable = []
        data.forEach(function (d) {
            lookupTable[d.date] = {"close":d.close, "volume":d.volume};
        });

        svg.append("svg:rect").attr("width",width).attr("height", height);
        svg.datum(data);


        // Get minimum and maximum date values
        // ASSUMPTION: Data is sorted "new to old"!
        var maxDate = data[0].date;
        var minDate = data[data.length-1].date;

        cloExtent = d3.extent(data, function(d) { return d.close; });
        // Set up scales
        var xScale = d3.time.scale()
            .domain([minDate, maxDate])
            .range([0, width]);
        var yScaleClo = d3.scale.linear()
            //.domain([0,d3.max(data, function(d) { return d.close; })])
            //.domain(d3.extent(data, function(d) { return d.close; }))
            .domain([cloExtent[0] * 0.8, cloExtent[1]])
            .range([height, 0]);
        var yScaleVol = d3.scale.linear()
            .domain([0,d3.max(data, function(d) { return d.volume; })])
            .range([height, height / 2]);

        // Set up axes
        var xAxis = d3.svg.axis()
            .scale(xScale)
            .tickFormat(function(date) {
                if (0 == date.getMonth()) {
                    return date.getFullYear();
                } else if (date.getDate() != 1) {
                    return d3.time.format("%d")(date);
                } else {
                    return d3.time.format("%b")(date);
                }
            })
            .orient("bottom");

        if (data.length < 10) {
            xAxis.ticks(d3.time.days)
                .tickFormat(d3.time.format("%a %d"));
        }

        var yAxisClo = d3.svg.axis()
            .scale(yScaleClo)
            .orient("left");
        var yAxisVol = d3.svg.axis()
            .tickFormat(function(vol) {
                if (vol >= 1000000) {
                    return (vol / 1000000.0) + "M";
                } else if (vol >= 1000) {
                    return (vol / 1000.0) + "k";
                } else {
                    return vol;
                }
            })
            .scale(yScaleVol)
            .orient("right");

        // Set up line and area generators
        var line = d3.svg.line()
            .x(function(d) { return xScale(d.date); })
            .y(function(d) { return yScaleClo(d.close); });
        var area = d3.svg.area()
            .x(function(d) { return xScale(d.date); })
            .y1(function(d) { return yScaleVol(d.volume); })
            .y0(height);
        var emptyLine = d3.svg.line()
            .x(function(d) { return xScale(d.date); })
            .y(function(d) { return height; });
        var emptyArea = d3.svg.area()
            .x(function(d) { return xScale(d.date); })
            .y1(function(d) { return height; })
            .y0(height);

        // Append the whole lot to SVG

        /*
        // Dots for closing price
        var dots = svg.selectAll(".dot")
        dots
            .data(data)
          .enter().append("circle")
            .attr("class", "dot")
            .attr("cx", line.x())
            .attr("cy", line.y())
            .attr("r", 10)
            .style("stroke", col.background)
            .style("stroke-width", 1)
          .transition()
            .duration(500)
            .style("stroke", col.closing)
            //.ease("elastic", 1.75)
            .delay(function(d,i) { return 1.5 * (data.length - i); })
            .attr("r", 2)
          .transition()
            .delay(2500)
            .duration(750)
            .style("stroke-width", 0);
        */

        // Path 1: Area chart for volume
        svg.append("path")
            .attr("class", "area")
            .style("fill", col.volume)
            .attr("d", emptyArea)
          .transition()
            .ease("elastic", 1, 1.25)
            .delay(100)
            .duration(1000)
            .attr("d", area);
        // Path 2: Line chart for closing price
        svg.append("path")
            .attr("class", "line")
            .attr("d", emptyLine)
            .style("stroke", col.closing)
            .style("stroke-width", 1)
          .transition()
            .ease("elastic", 1, 1.25)
            .duration(1000)
            .attr("d", line);
        var millionsFormat = function(n) {
            if (n > 1000000.0) {
                return String.format("%.2fM", n/1000000.0);
            }
            return n;
        }

        // Axes
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis)
            .style("fill", col.neutral);

        svg.append("g")
            .attr("class", "y axis c2")
            .call(yAxisClo)
            .style("fill", col.closing)
          .append("svg:text")
            .attr("id", "yLabelClo")
            .attr("dy", "-.35em")
            .text("Closing price (" + currency + ")")
            .attr("filter", "url(#blurdrop)")
            .attr("transform", "rotate(90)");

        svg.append("g")
            .attr("class", "y axis c2")
            .attr("transform", "translate(" + width + ",0)")
            .call(yAxisVol)
            .style("fill", col.volume)
          .append("svg:text")
            .attr("id", "yLabelVol")
            .attr("dy", "-.35em")
            .attr("text-anchor", "end")
            .text("Volume")
            .attr("filter", "url(#blurdrop)")
            .attr("transform", "translate(0," + height/2 + ")rotate(-90)");

        // Rule lines
        svg.append("svg:text")
            .attr("id", "xtext")
            .attr("text-anchor", "middle")
            .attr("fill", col.neutral)
            .attr("filter", "url(#blurdrop)")
            .attr("stroke", "none")
            .attr("display", "none");
        svg.append("svg:text")
            .attr("id", "ytextClo")
            .attr("x", 0)
            .attr("filter", "url(#blurdrop)")
            .attr("text-anchor", "start")
            .attr("dy", "-.25em")
            .attr("dx", ".25em")
            .attr("fill", col.closing.darker(1))
            .attr("display", "none");
        svg.append("svg:text")
            .attr("id", "ytextVol")
            .attr("filter", "url(#blurdrop)")
            .attr("text-anchor", "end")
            .attr("x", width)
            .attr("y", height)
            .attr("dy", "-.25em")
            .attr("dx", "-.25em")
            .attr("fill", col.volume.darker(1))
            .attr("stroke", "none")
            .attr("display", "none");
        svg.append("line")
            .attr("id", "yruleClo")
            .style("display", "none")
            .style("stroke", col.neutral.brighter(0.5))
            .style("width", 0.2);
        svg.append("line")
            .attr("id", "yruleVol")
            .attr("x1", width)
            .style("display", "none")
            .style("stroke", col.neutral.brighter(0.5))
            .style("width", 0.2);
        svg.append("line")
            .attr("id", "xrule")
            .style("display", "none")
            .attr("y1", "0.5em")
            .attr("y2", height)
            .style("stroke", col.neutral.brighter(0.5))
            .style("width", 0.2);

        svg.on("mousemove", function(){
            var mouseX = d3.mouse(this)[0];

            // See how far away each data point is
            var distanceMappings = data.map(function(d) {
                var what = Math.abs(xScale(d.date) - mouseX);
                return {"dist":what, "data":d};
            });

            // Find the closest one
            var nearest = undefined;
            var count = 1;
            distanceMappings.forEach(function(d) {
                if (nearest === undefined || nearest.dist > d.dist) {
                    count+=1;
                    nearest = d;
                }
            });

            // We just need the data
            nearest = nearest.data;
            var x = Math.round(xScale(nearest.date));
            var yClo = Math.round(yScaleClo(nearest.close));
            var yVol = Math.round(yScaleVol(nearest.volume));
            svg.select("#xrule")
                .attr("x1", x)
                .attr("x2", x);
            svg.select("#yruleClo")
                .attr("y1", yClo)
                .attr("y2", yClo)
                .attr("x1", x);
            svg.select("#yruleVol")
                .attr("y1", yVol)
                .attr("y2", yVol)
                .attr("x2", x);
            svg.select("#xtext")
                .text(formatDate(nearest.date))
                .attr("x", x);
            svg.select("#ytextClo")
                .text(currency + " " + nearest.close.toFixed(2))
              .transition()
                .duration(300)
                .attr("y", yClo);
            svg.select("#ytextVol")
                .text(nearest.volume)
              .transition()
                .duration(300)
                .attr("y", yVol);



            var yTextClo = svg.select("#ytextClo");   // Rule line text
            var yLabelClo = svg.select("#yLabelClo"); // Axis label
            // Get bounding boxes
            var textBBox = yTextClo.node().getBBox();
            var labelBBox = yLabelClo.node().getBBox();

            // HAX
            // getBBox doesn't understand SVG transform="rotate(X)" attributes
            // So just switch the width and height to simulate rotation by 90 deg
            var x = labelBBox.width;
            labelBBox.width = labelBBox.height;
            labelBBox.height = x;

            textBBox = {"x": yTextClo.attr("x"), "y": yClo - textBBox.height,
                     "width":textBBox.width, "height": textBBox.height};

            /*
            // Boxes for debugging
            svg.selectAll(".removeThis1").remove();
            svg.append("svg:rect")
                .attr("class", "removeThis1")
                .style("fill", col.closing.darker(1))
                .attr("x", textBBox.x)
                .attr("y", textBBox.y)
                .attr("width", textBBox.width)
                .attr("height", textBBox.height);

            svg.selectAll(".removeThis4").remove();
            svg.append("svg:rect")
                .attr("class", "removeThis4")
                .style("fill", col.closing.darker(0.5))
                .attr("x", labelBBox.x)
                .attr("y", labelBBox.y)
                .attr("width", labelBBox.width)
                .attr("height", labelBBox.height);
            */

            if (intersects(textBBox, labelBBox)) {
                smoothHide(yLabelClo);
            } else {
                smoothShow(yLabelClo);
            }



            var yTextVol = svg.select("#ytextVol");   // Rule line text
            var yLabelVol = svg.select("#yLabelVol"); // Axis label
            // Get bounding boxes
            var textBBox = yTextVol.node().getBBox();
            var labelBBox = yLabelVol.node().getBBox();

            // HAX
            // getBBox doesn't understand SVG transform="rotate(X)" attributes
            // So just switch the width and height to simulate rotation by 90 deg
            var x = labelBBox.width;
            labelBBox.width = labelBBox.height;
            labelBBox.height = x;
            // HAX: Fudge the label coordinates a lot. Again due to transform attr
            // not being accounted for.
            labelBBox.x += width +labelBBox.width * 2;
            labelBBox.y += height/2 + labelBBox.width;


            textBBox = {"x": yTextVol.attr("x") - textBBox.width, "y": yVol - textBBox.height,
                     "width":textBBox.width, "height": textBBox.height};

            /*
            // Boxes for debugging
            svg.selectAll(".removeThis2").remove();
            svg.append("svg:rect")
                .attr("class", "removeThis2")
                .style("fill", col.volume.darker(1))
                .attr("x", textBBox.x)
                .attr("y", textBBox.y)
                .attr("width", textBBox.width)
                .attr("height", textBBox.height);

            svg.selectAll(".removeThis3").remove();
            svg.append("svg:rect")
                .attr("class", "removeThis3")
                .style("fill", col.volume.darker(0.5))
                .attr("x", labelBBox.x)
                .attr("y", labelBBox.y)
                .attr("width", labelBBox.width)
                .attr("height", labelBBox.height);
            */

            if (intersects(textBBox, labelBBox)) {
                smoothHide(yLabelVol);
            } else {
                smoothShow(yLabelVol);
            }

        });
        svg.on("mouseout", function(){
            svg.selectAll("#yruleClo, #yruleVol, #xrule, #xtext, #ytextClo, #ytextVol")
                .style("display", "none");
            smoothShow(d3.select("#yLabelVol, #yLabelClo"));
        });
        svg.on("mouseover", function(){
            svg.selectAll("#yruleClo, #yruleVol, #xrule, #xtext, #ytextClo, #ytextVol")
                .style("display", "block");
        });

    });
}
