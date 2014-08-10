// True once the modal has been initialized

// False only when the user has clicked Update on the modal form,
// Causes the page to be updated if filters have changed
var filterModalCancelled;

var timeModalCancelled;



// True if the filters have been modified by the modal.
var filtersModified;

// Used as a placeholder when chart is empty.
var empty_chart=[
    {
        key:"Loading...",
        values:[
        {x:0, y:0}, {x:1, y:0}
        ]
    }
];

$(function() {
    initializeReport();


    var st_dt = new Date(0); // The 0 there is the key, which sets the date to the epoch
    st_dt.setUTCSeconds(report_start_time/1000);
    var et_dt = new Date(0); // The 0 there is the key, which sets the date to the epoch
    et_dt.setUTCSeconds(report_end_time/1000);
    $("#report_start_datetime").datetimepicker({minDate:st_dt, maxDate:et_dt});
    $("#report_end_datetime").datetimepicker({minDate:st_dt, maxDate:et_dt});

    // Update the filters for active_filter
    $('#selected_filters').change(function() {
        current_filters[active_filter].filter.in = $("#selected_filters :selected").map(function(){ return this.value }).get();
        update_model_count();
        filtersModified=true;
    });

    // Update the excludes for active_filter
    $('#selected_excludes').change(function() {
        current_filters[active_filter].exclude.in = $("#selected_excludes :selected").map(function(){ return this.value }).get();
        update_model_count();
        filtersModified=true;
    });
    update_selected_field(active_filter)

    // Initizalises the modal the first time it is shown
    // Backs up the filters so they can be reverted later
    $('#filterModal').on('show.bs.modal', function (e) {
        filterModalCancelled=true;
        filtersModified=false;
        backup_filters=[];
        $.extend(true, backup_filters, current_filters );


    })

    // Reverts the filters if cancelled,
    // Updates the report if they have changed
    $('#filterModal').on('hide.bs.modal', function (e) {
        if (filterModalCancelled){
            // revert the filters
            current_filters=backup_filters;
            update_model_count();
            return true;
        }
        if (filtersModified){
            updateReport();
        }

    })

    $("#timeSelectModal").on("hide.bs.modal", function(e){
        if (!timeModalCancelled){
            report_start_time=$("#report_start_datetime").datetimepicker('getDate');
            report_end_time=$("#report_end_datetime").datetimepicker('getDate');
            updateReport();
        }
    });
    function change_range(step){
        var newDate = new Date(0);
        newDate.setUTCSecods(report_start_time+step);
        $("#report_start_datetime").datetimepicker('setDate', newDate );
        newDate = new Date(0);
        newDate.setUTCSecods(report_end_time+step);
        $("#report_end_datetime").datetimepicker('setDate', newDate );
        timeModalCancelled=false;
    }

    $("#timeSelectModal").on("show.bs.modal", function(e){
        timeModalCancelled=true;

        var sst_dt = new Date(0); // The 0 there is the key, which sets the date to the epoch
       sst_dt.setUTCSeconds(report_start_time/1000);
        $("#report_start_datetime").datetimepicker('setDate', sst_dt );

        var set_dt = new Date(0); // The 0 there is the key, which sets the date to the epoch
       set_dt.setUTCSeconds(report_end_time/1000);
        $("#report_end_datetime").datetimepicker('setDate', set_dt );
    });
});

// Updates the badges on the modal, and the navbar.  Call after any modification to filters
function update_model_count() {
    var count;
    var total = 0;
    for (var propertyName in current_filters) {
        count = 0;
        count += current_filters[propertyName].filter.in.length;
        count += current_filters[propertyName].filter.lt ? 1 : 0;
        count += current_filters[propertyName].filter.lte ? 1 : 0;
        count += current_filters[propertyName].filter.gt ? 1 : 0;
        count += current_filters[propertyName].filter.gte ? 1 : 0;
        count += current_filters[propertyName].exclude.in.length;
        count += current_filters[propertyName].exclude.lt ? 1 : 0;
        count += current_filters[propertyName].exclude.lte ? 1 : 0;
        count += current_filters[propertyName].exclude.gt ? 1 : 0;
        count += current_filters[propertyName].exclude.gte ? 1 : 0;
        $("#" + propertyName + "_label").removeClass("active");

        $("#" + propertyName + "_badge").text((count > 0) ? count : "");

        total += count
    }
    if (total > 0) {
        $("#filterCount").text(total);
    } else {
        $("#filterCount").text("");
    }
}

// Called when a specific filter is selected, loads the values into the select boxes
function update_filter_widgets() {
    var filter_html = "";
    var exclude_html = "";

    $.each(current_filters[active_filter].values, function (index, value) {

        var selected = ""
        if (current_filters[active_filter].filter.in.indexOf(value.value) == -1) {
            // not in active filters
            selected = "";
        } else {
            selected = "selected"
        }
        filter_html += "<option value='" + value.value + "' " + selected + ">" + value.display_value + "</option>";
        if (current_filters[active_filter].exclude.in.indexOf(value.value) == -1) {
            // not in active filters
            selected = "";
        } else {
            selected = "selected"
        }
        exclude_html += "<option value='" + value.value + "' " + selected + ">" + value.display_value + "</option>";
    });
    $('#selected_filters').html(filter_html);
    $('#selected_excludes').html(filter_html);
}


// Updates the list of selected bounds/ranges, called when values are changed
// or modal is displayed
function update_range_lists() {
    operators = [
        {
            operator: "lt",
            text: " is less than "
        },
        {
            operator: "lte",
            text: " is less than or equal to "
        },
        {
            operator: "gt",
            text: " is greater than "
        },
        {
            operator: "gte",
            text: " is greater than or equal to "
        }
    ];
    var html = "";
    $.each(operators, function (index, value) {
        if (current_filters[active_filter].filter[value.operator]) {
            html += '<li>';
            html += "Including data where: " + current_filters[active_filter].display_name + value.text + current_filters[active_filter].filter[value.operator];
            html += '<a href="#" onClick=\'';
            html += 'remove_bound("' + active_filter + '", "filter", "'+value.operator+'"); return false;\'>';
            html += '<span class="glyphicon glyphicon-remove"></span></a>';
            html += "</li>";
        }
        if (current_filters[active_filter].exclude[value.operator]) {
            html += '<li>';
            html += "Excluding data where: " + current_filters[active_filter].display_name + value.text + current_filters[active_filter].filter[value.operator];
            html += '<a href="#" onClick=\'';
            html += 'remove_bound("' + active_filter + '", "exclude", "'+value.operator+'"); return false;\'>';
            html += '<span class="glyphicon glyphicon-remove"></span></a>';
            html += "</li>";
        }
    });
    $("#active_range_filters").html(html);
    update_model_count();
}

function remove_bound(filter_name, action, operator){
    current_filters[filter_name][action][operator]=null;
    update_filter_widgets();
    filtersModified=true;
    update_range_lists();
}



// Updates the modal to display the current filter.
function update_selected_field(filter) {
    active_filter = filter;

    for (var propertyName in current_filters) {
        $("#" + propertyName + "_label").removeClass("active");
        if (propertyName == filter) {

            $("#" + propertyName + "_label").addClass("active");
        }
    }
    // Disable all panels
    // Check if can select values, if so enable panels

    // Check if can enter range
    // If so, enable panel and set validation
    if (current_filters[filter].hasOwnProperty("can_enter_range") && current_filters[filter].can_enter_range) {
        $("#field_name_label").text(current_filters[filter].display_name);
        $("#enter_range_panel").show();
    } else {
        $("#enter_range_panel").hide();
    }


    // Check if can select datetime range
    // If so, enable panel

    if (current_filters[filter].hasOwnProperty("can_select_values") && current_filters[filter].can_select_values) {
        $("#select_exclude_panel").block({ message: null });
        $("#select_filter_panel").block({ message: null });
        if (current_filters[filter].values.length < 1) {
            $.getJSON(value_list_url+'?' + $.param({field: filter}), function (data) {
                current_filters[filter].values = data.data.values;
                if (active_filter == filter) {
                    $("#select_exclude_panel").unblock();
                    $("#select_filter_panel").unblock();
                    update_filter_widgets();
                }
            });
        } else {
            $("#select_exclude_panel").unblock();
            $("#select_filter_panel").unblock();
            update_filter_widgets();
        }
        $("#select_exclude_panel").show();
        $("#select_filter_panel").show();
    } else {
        $("#select_exclude_panel").hide();
        $("#select_filter_panel").hide();
    }


}

// Adds a range based filter
function range_filter_add(action){
    $("#range_filter_input").removeClass("has-error");
    if ($("#range_filter_value").val() == ""){
        $("#range_filter_input").addClass("has-error");
        return false;
    }
    current_filters[active_filter][action][$("#range_filter_operator").val()]=$("#range_filter_value").val();
    filtersModified=true;
    update_range_lists();
}










// Creates all charts
function initializeReport(){
    for (var chart_name in chart_data){
        create_chart(chart_name);
    }
    loadWidgets();
}

// Called when report needs to be reloaded due to data change
function updateReport(){
    // Clear all existing data to avoid confusion...
    loadWidgets();
}

function build_filter_list(name) {
    var filters = [];
    for (var propertyName in current_filters) {
        for (var operator in current_filters[propertyName][name]){
            if( (operator == "in" && current_filters[propertyName][name][operator].length >0 )
                || (operator != "in" && current_filters[propertyName][name][operator])){
                filters.push({
                    field: propertyName,
                    operator: operator,
                    value: current_filters[propertyName][name][operator]
                });
            }
        }
    }
    return filters;
}

// Need Set filters and excludes....
function loadWidgets(){
    // Loads data into widgets
    var filterData={
        view:'lf_utilization_view',
        filters:build_filter_list('filter'),
        excludes:build_filter_list('exclude'),
        groups:[],
        start_time_js:report_start_time,
        end_time_js:report_end_time
    };

    // Sets the permenant link to this report
    $.post(buildFilterUrl,JSON.stringify(filterData),function( data ){
        $("#permalinkURL").attr("href", data.url);
    });

    // Gets the total number of attempts
    filterData.view='lf_util_total_attempts';
    $.post(buildFilterUrl,JSON.stringify(filterData),function( data ){
        $("#counterText").text(data.count);
    });

    // Load the data for this chart.
    for (var chart_name in chart_data){
        for (var view_name in chart_data[chart_name].data){
            if (chart_data[chart_name].hasOwnProperty("active_field")){
                for (var field_name in chart_data[chart_name].data[view_name].chart_data){
                    load_chart(chart_name, view_name, field_name);
                }
            }else{
                load_chart(chart_name, view_name);
            }
        }
    }
}

// Need to build filters/excludes
function load_chart(chart_name, view_name, field){
    var chart_selector="#" + chart_name + " svg";
    var table_selector="#" + chart_name + "_table";
    var filterData={
        filters:build_filter_list('filter'),
        excludes:build_filter_list('exclude'),
        start_time_js:report_start_time,
        end_time_js:report_end_time
    };

    filterData.groups=chart_data[chart_name].data[view_name].groups;
    filterData.view=chart_data[chart_name].chart_view;
    // Block the chart.....
    $("#"+chart_name).block({ message: null,css: {
            border: 'none',
            padding: '15px',
            backgroundColor: '#000',
            '-webkit-border-radius': '10px',
            '-moz-border-radius': '10px',
            opacity: .5,
            color: '#fff'
        } });
    $.post(buildFilterUrl,JSON.stringify(filterData),function( data ){
        var params="";
        if (field && field.length > 0){
            params="?" + $.param({field:field});
        }
        $.getJSON(data.url + params, function(data) {
            var chart=chart_data[chart_name];
            var view=chart.data[view_name];
            if ( chart.hasOwnProperty("active_field")){
                view.chart_data[field]=data['data'];
                if (chart.active==view_name && chart.active_field == field){
                    $("#"+chart_name).unblock();
                    d3.select(chart_selector)
                    .datum(view.chart_data[field])
                    .transition().duration(500)
                    .call(chart.chart);
                }
            }else{
                view.chart_data=data['data'];
                if (chart.active==view_name){
                    $("#"+chart_name).unblock();
                    d3.select(chart_selector)
                    .datum(view.chart_data)
                    .transition().duration(500)
                    .call(chart.chart);
                }
            }
        });
    });
    if (chart_data[chart_name].hasOwnProperty( "table_view" )){
        $(table_selector).block({ message: null,css: {
            border: 'none',
            padding: '15px',
            backgroundColor: '#000',
            '-webkit-border-radius': '10px',
            '-moz-border-radius': '10px',
            opacity: .5,
            color: '#fff'
        } });
        filterData.view=chart_data[chart_name].table_view;
        $.post(buildFilterUrl,JSON.stringify(filterData),function( data ){
            $.get(data.url, function(data) {
                var chart=chart_data[chart_name];
                var view=chart.data[view_name];
                view.table_data=data;
                // Check if selected, then display....
                if (chart.active==view_name){
                    $(table_selector).html(view.table_data);
                    $(table_selector).unblock();
                }
            });
        });
    }
}









// Creates a chart of given name
function create_chart(chart_name){
    var chart_selector="#" + chart_name + " svg";
    if (chart_data[chart_name].chart_type=="area"){
        nv.addGraph(function() {
            chart_data[chart_name].chart = nv.models.stackedAreaChart();
            chart_data[chart_name].chart.clipEdge(true);
            chart_data[chart_name].chart.xAxis.tickFormat(function(d) { return d3.time.format('%x %X')(new Date(d)) });
            chart_data[chart_name].chart.xAxis.rotateLabels(-45);
            chart_data[chart_name].chart.margin({bottom: 120, left:100});
            chart_data[chart_name].chart.xAxis.axisLabel('Date');
            chart_data[chart_name].chart.showControls(false);
            d3.select(chart_selector)
            .datum([])
            .transition().duration(500)
            .call(chart_data[chart_name].chart);
            nv.utils.windowResize(chart_data[chart_name].chart.update);
            return chart_data[chart_name].chart;
        });
    }
    if (chart_data[chart_name].chart_type=="bar"){
        nv.addGraph(function() {
            chart_data[chart_name].chart = nv.models.multiBarChart();

            if (chart_data[chart_name].hasOwnProperty("chart_attributes")){
                $.each(chart_data[chart_name].chart_attributes, function( index, value ) {
                    var c=chart_data[chart_name].chart;
                    var fields = value.key.split(".");
                    while(fields.length > 1){
                        c=c[fields.shift()];
                    }
                    c[fields.shift()](value.value);
                });
            }
            d3.select(chart_selector)
                .datum([])
                .transition().duration(500)
                .call(chart_data[chart_name].chart);
            nv.utils.windowResize(chart_data[chart_name].chart.update);
            return chart_data[chart_name].chart;
        });
    }
}



    function set_active_chart(selector, state){

        chart_data[selector].active = state;
        // Change the classes in the tabs...
        var wanted_selector=selector+"_"+state;
        for (var value in chart_data[selector].data){
            var v = selector+"_"+value;
            document.getElementById(v).className ="";
            if (v.valueOf() === wanted_selector.valueOf()){
                document.getElementById(v).className ="active";
            }
        }

        // Set the attributes for the active graph
        var chart_selector="#" + selector + " svg";
        var data=[];
        if ( chart_data[selector].hasOwnProperty("active_field")){
            var field = chart_data[selector].active_field;
            chart_data[selector].active_field = field;
            data=chart_data[selector].data[state].chart_data[field];
        }else{
            data=chart_data[selector].data[state].chart_data;
        }
        d3.select(chart_selector)
            .datum(empty_chart)
            .transition().duration(500)
            .call(chart_data[selector].chart);
        d3.select(chart_selector)
            .datum(data)
            .transition().duration(500)
            .call(chart_data[selector].chart);

        $("#" + selector+"_table").html(chart_data[selector].data[state].table_data);
    }

    function set_active_field(selector, field){
        var current_state = chart_data[selector].active;
        chart_data[selector].active_field = field;
        // Change the classes in the tabs...
        var wanted_selector=selector+"_"+field;
        for (var value in chart_data[selector].data[current_state].chart_data){
            var v = selector+"_"+value;
            document.getElementById(v).className ="";
            if (v.valueOf() === wanted_selector.valueOf()){
                document.getElementById(v).className ="active";
            }
        }
        set_active_chart(selector, current_state);
    }

