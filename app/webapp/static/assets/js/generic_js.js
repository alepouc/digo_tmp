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
