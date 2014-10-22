function SimpleLineChart(config)
{
// Default parameters.
	var p =
	{
		parent          : null,
		labels          : [ "X", "Y" ],
		listeners       : [],
		data            : [[0,0],[1,1],[2,4],[3,9],[4,16]],
		width           : 600,
		height          : 400,
		xi              : 0,
		yi              : 1,
		mleft           : 0,
		mright          : 0,
		mtop	        : 0,
		mbottom         :0
	};

	// If we have user-defined parameters, override the defaults.
	if (config !== "undefined")
	{
		for (var prop in config)
		{
			p[prop] = config[prop];
		}
	}

	// Render this chart.
	function chart()
	{
		var inner_width = p.width - p.mleft - p.mright;
		var inner_height = p.height - p.mtop - p.mbottom;
		
		var x = d3.scale.linear()
			.domain(d3.extent(p.data, function(d){return d[p.xi];}))
			.range([0, inner_width]);

		var y = d3.scale.linear()
			.domain([0, d3.max(p.data, function(d) {return d[p.yi];})])
			.range([inner_height, 0]);

		var lineFunction = d3.svg.line()
	        .x(function(d){return x(d[p.xi]);})
	        .y(function(d){return y(d[p.yi]);});

		// Create the x axis at the bottom.
		var xAxis = d3.svg.axis()
		.scale(x)
		.orient("bottom");

		// Create the y axis to the left.
		var yAxis = d3.svg.axis()
		.scale(y)
		.orient("left");

		var previous_g = p.parent.select('g')[0][0];

		if(!previous_g){
			var chartContainer = p.parent
				.attr("width", p.width)
	    		.attr("height", p.height)
	  			.append("g")
				.attr("transform", "translate(" + p.mleft + "," + p.mtop + ")");

			// Draw the x axis.
			chartContainer.append("g")
				.attr("class", "x axis")
				.attr("transform", "translate(0," + inner_height + ")")
				.call(xAxis)
				.append('text')			
				.attr('class', 'xaxis_label')
				.style("text-anchor", "middle")
				.attr('x', inner_width / 2)
				.attr('y', p.mbottom / 2)
				.text(p.labels[p.xi]);

            // Draw the y axis
			chartContainer.append("g")
				.attr("class", "y axis")
				.call(yAxis)
				.append("text")
				.attr('class', 'yaxis_label')
				.attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("x", -p.mleft)
				.attr("dy", "1em")
				.style("text-anchor", "middle")
				.text(p.labels[p.yi]);

	        chartContainer.append("path")
	        	.attr("class", "line history")
	        	.attr('d', lineFunction(p.data));
            
            //Linear regression line
            var lr_line = ss.linear_regression()
                .data(p.data)
                .line();
            
            var lr_vals = _.map(p.data, function(val, i){return [val[0], lr_line(val[0])];});
            
            chartContainer.append("path")
                .attr("class", "line regression")
                .attr('d', lineFunction(lr_vals));
		}
		else{
			d3.select('.y.axis').transition().call(yAxis);
            d3.select('.x.axis').transition().call(xAxis);
			p.parent.select('g').select('.yaxis_label').text(p.labels[p.yi]);			
            d3.select('.line.history')
                //.attr('class', 'line history')
				.transition()
				.attr("d", lineFunction(p.data));
            
            var lr_line = ss.linear_regression()
                .data(p.data)
                .line();
            
            var lr_vals = _.map(p.data, function(val, i){return [val[0], lr_line(val[0])];});
            d3.select('.line.regression')
                .transition()
                .attr('d', lineFunction(lr_vals));
		}
	}

	// Use this routine to retrieve and update attributes.
	chart.attr = function(name, value)
	{
	// When no arguments are given, we return the current value of the
	// attribute back to the caller.
	if (arguments.length == 1)
	{
		return p[name];
	}
	// Given 2 arguments we set the name=value.
	else if (arguments.length == 2)
	{
		p[name] = value;
	}

	// Return the chart object back so we can chain the operations together.
	return chart;
	}

	// This routine supports the update operation for this chart.  This is
	// applicable when the chart should be partially updated.
	chart.update = function()
	{
	}

	// Return the instantiated chart object.
	return chart;
}