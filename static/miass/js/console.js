var list_console = [];
var voices = [];

function setVoiceList(){
    voices = window.speechSynthesis.getVoices();
}

if(window.speechSynthesis.onvoiceschanged !== undefined){
    window.speechSynthesis.onvoiceschanged = setVoiceList;
}
function speech(txt) {
    if(!window.speechSynthesis) {
        return;
    }
    setVoiceList();
    var utterThis = new SpeechSynthesisUtterance();
    // utterThis.voice = voices[1];
    utterThis.voice = window.speechSynthesis.getVoices()[5];

    utterThis.lang = 'en-US';
    utterThis.pitch = 1;
    utterThis.rate = 1; //속도
    utterThis.text = txt;
    // window.speechSynthesis.speak(utterThis);
}



function write_log_in_console(text){
    var dt = new Date();
    var dict_data = {};
    dict_data["date"] ="["+dt.getFullYear()+"."+(dt.getMonth()+1).toString().padStart(2,"0")+"."+dt.getDate().toString().padStart(2,"0")+" "
        +dt.getHours().toString().padStart(2,"0")+":"+dt.getMinutes().toString().padStart(2,"0")+":"+dt.getSeconds().toString().padStart(2,"0")+"]";
    dict_data["text"] = text

    // if (text.includes("start") || text.includes("finish") || text.includes("stop") || text.includes("prepare")  || text.includes("upload")  || text.includes("Stage")){
    speech(text);
    // }
    list_console.push(dict_data);
    if (list_console.length >8)
        list_console.shift();

    $("#div_console").empty();
    for (var i in list_console){
        var text = list_console[i]["text"];
        if (text.includes("^")){
            var def = text.split("^")
            text = def[0]+"<sup>"+def[1].slice(0, 1)+"</sup>"+def[1].slice(1, def[1].length);
        }
        $("#div_console").append("<p class='mb-0' style='color:white;'>" +
            "<span class='mr-2' style='font-weight: bold; font-size: large'>"+list_console[i]['date']+"</span> " +
            "<span style='font-size: large'>"+text+"</span></p>");
    }
};