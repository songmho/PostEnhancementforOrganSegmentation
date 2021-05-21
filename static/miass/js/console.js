var list_console = [];
function write_log_in_console(text){
    var dt = new Date();
    var dict_data = {};
    dict_data["date"] ="["+dt.getFullYear()+"."+(dt.getMonth()+1).toString().padStart(2,"0")+"."+dt.getDate().toString().padStart(2,"0")+" "
        +dt.getHours().toString().padStart(2,"0")+":"+dt.getMinutes().toString().padStart(2,"0")+":"+dt.getSeconds().toString().padStart(2,"0")+"]";
    dict_data["text"] = text
    list_console.push(dict_data);
    if (list_console.length >9)
        list_console.shift();

    $("#div_console").empty();
    for (var i in list_console)
        $("#div_console").append("<p class='mb-0' style='color:white;'>" +
            "<span style='font-weight: bold'>"+list_console[i]['date']+"</span> " +
            "<span >"+list_console[i]["text"]+"</span></p>");
};