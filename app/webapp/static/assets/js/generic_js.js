// ------------------------------------------------
// --- Variables
// ------------------------------------------------
var colors_nodes = {
  "ipv4":"#FF756E",
  "ipv6":"#DE9BF9",
  "domain": "#68BDF6",
  "email": "#6DCE9E",
  "hash": "#FFD86E",
  "country": "#FF756E",
  "entity": "#FB95AF",
  "threat_actor": "#A5ABB6"
};

var colors_edges = "#A5ABB6";

var colors_node_array = [
          "#A5ABB6",
          "#FF756E",
          "#DE9BF9",
          "#68BDF6",
          "#6DCE9E",
          "#FFD86E",
          "#FF756E",
          "#FB95AF",
          "#A5ABB6"
        ]


// ------------------------------------------------
// --- Ajax function
// ------------------------------------------------
ajax_function = function(uri, method, data, async_value) {
 if(async_value == undefined)
 {
   async_value = true;
 }
 var request = {
     url: uri,
     type: method,
     cache: false,
     async: async_value,
     data: data,
     success: function(d){
       ajax_return = d
     }
 };
 return $.ajax(request);
}


function ajaxMaskUI(settings) {

    function maskPageOn(color) { // color can be ie. 'rgba(176,176,176,0.7)' or 'transparent'
        var div = $('#maskPageDiv');
        if (div.length === 0) {
            $(document.body).append('<div id="maskPageDiv" style="position:fixed;width:100%;height:100%;left:0;top:0;display:none"></div>'); // create it
            div = $('#maskPageDiv');
        }
        if (div.length !== 0) {
            div[0].style.zIndex = 2147483647;
            div[0].style.backgroundColor=color;
            div[0].style.display = 'inline';
        }
    }

    function maskPageOff() {
        var div = $('#maskPageDiv');
        if (div.length !== 0) {
            div[0].style.display = 'none';
            div[0].style.zIndex = 'auto';
        }
    }

    function hourglassOn() {
        if ($('style:contains("html.hourGlass")').length < 1) $('<style>').text('html.hourGlass, html.hourGlass * { cursor: wait !important; }').appendTo('head');
        $('html').addClass('hourGlass');
    }

    function hourglassOff() {
        $('html').removeClass('hourGlass');
    }

    if (settings.maskUI===true) settings.maskUI='transparent';

    if (!!settings.maskUI) {
        maskPageOn(settings.maskUI);
        hourglassOn();
    }

    var dfd = new $.Deferred();
    $.ajax(settings)
        .fail(function(jqXHR, textStatus, errorThrown) {
            if (!!settings.maskUI) {
                maskPageOff();
                hourglassOff();
            }
            dfd.reject(jqXHR, textStatus, errorThrown);
        }).done(function(data, textStatus, jqXHR) {
            if (!!settings.maskUI) {
                maskPageOff();
                hourglassOff();
            }
            dfd.resolve(data, textStatus, jqXHR);
        });

    return dfd.promise();
}



// ------------------------------------------------
// --- Remove dupplicate from array
// ------------------------------------------------
function uniq(a) {
    return a.sort().filter(function(item, pos, ary) {
        return !pos || item != ary[pos - 1];
    })
}



// ------------------------------------------------
//--  Get campaigns
// ------------------------------------------------
function get_all_campaigns(){
  ajax_function("get_all_campaigns","GET", false, false).done(function(json) {
    data = json;
  });
  return data;
}


// ------------------------------------------------
//--  Get indicators for specific campaign for table
// ------------------------------------------------
function get_indicators_specific_campaign_for_table_view(campaign){
  ajax_function("get_indicators_specific_campaign_for_table_view","GET", 'campaign='+campaign, false).done(function(json) {
    data = json;
  });
  return data;
}


// ------------------------------------------------
//--  Get indicators by node type for specific campaign
// ------------------------------------------------
function get_number_of_indicator_by_node_type_for_specific_campaign(campaign){
  ajax_function("get_number_of_indicator_by_node_type_for_specific_campaign","GET", 'campaign='+campaign, false).done(function(json) {
    data = json;
  });
  return data;
}


// ------------------------------------------------
//--  Get indicators by node type for specific campaign
// ------------------------------------------------
function get_neo4j_json_for_table(arg){
  ajax_function("get_neo4j_json_for_table","GET", arg, false).done(function(json) {
    data = json;
  });
  return data;
}
