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


// ------------------------------------------------
// --- Remove dupplicate from array
// ------------------------------------------------
function uniq(a) {
    return a.sort().filter(function(item, pos, ary) {
        return !pos || item != ary[pos - 1];
    })
}


// ------------------------------------------------
// --- Loading gif when a page is loading
// ------------------------------------------------
function loading_gif(time){
  $body.addClass("loading");;
  setTimeout(function(){
      $body.removeClass("loading");
  }, time);
}


// ------------------------------------------------
// --- Get the whole list of actions available
// ------------------------------------------------
function get_all_digos(){
  ajax_function("get_all_digos","GET", false, false).done(function(json) {
   all_actions = json;
 });
 return all_actions;
}



// ------------------------------------------------
//--  Get digo result
// ------------------------------------------------
function get_digo_result(action, value){
  ajax_function("get_digo_result","GET", "digo="+action+"&input="+value, false).done(function(json) {
    data = json;
  });
  return data;
}



// ------------------------------------------------
//--  Get the whole list of types
// ------------------------------------------------
function get_all_nodes_types(async){
  ajax_function("get_all_nodes_types","GET", false, false).done(function(json) {
   all_types = json
  });
  return all_types;
}


// ------------------------------------------------
//--  Delete node
// ------------------------------------------------
function delete_node(id){
  ajax_function("delete_node","POST", 'id='+id, false).complete(function(json) {
    data = json;
  });
  return data;
}


// ------------------------------------------------
//--  Add node
// ------------------------------------------------
function add_node(valuesToSubmit){
  ajax_function("add_node","POST", valuesToSubmit, false).complete(function(json) {
    data = json;
  });
  return data;
}


// ------------------------------------------------
//--  Add relationship
// ------------------------------------------------
function add_relationship(id1, id2){
  ajax_function("add_relationship","POST", 'id1='+id1+'&id2='+id2, false).complete(function(json) {
    data = json;
  });
  return data;
}



// ------------------------------------------------
//--  Add property
// ------------------------------------------------
function add_property(id, propertykey, propertyvalue){
  ajax_function("add_property","POST", 'id='+id+'&propertykey='+propertykey+'&propertyvalue='+propertyvalue, false).complete(function(json) {
    data = json;
  });
  return data;
}




// ------------------------------------------------
//--  Edit Node
// ------------------------------------------------
function edit_node(array){
  ajax_function("edit_node","POST", array, false).complete(function(json) {
    data = json;
  });
  return data;
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
//--  Get indicators for specific campaign
// ------------------------------------------------
function get_indicators_specific_campaign(campaign){
  ajax_function("get_indicators_specific_campaign","GET", 'campaign='+campaign, false).done(function(json) {
    data = json;
  });
  return data;
}


// ------------------------------------------------
//--  Get indicators by type for specific campaign
// ------------------------------------------------
function get_number_of_indicator_by_node_type_for_specific_campaign(campaign){
  ajax_function("get_number_of_indicator_by_node_type_for_specific_campaign","GET", 'campaign='+campaign, false).done(function(json) {
    data = json;
  });
  return data;
}
