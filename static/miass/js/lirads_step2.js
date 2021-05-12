(function () {
    var list_console = [];
    var isPause = false;
    var idx= 0;
    var intervalSegment = null;
    function write_log_in_console(text){
        var dt = new Date();
        list_console.push("["+dt.getFullYear()+"."+(dt.getMonth()+1).toString().padStart(2,"0")+"."+dt.getDate().toString().padStart(2,"0")+" "
            +dt.getHours().toString().padStart(2,"0")+":"+dt.getMinutes().toString().padStart(2,"0")+":"+dt.getSeconds().toString().padStart(2,"0")+"]  "+text);
        if (list_console.length >9)
            list_console.shift();

        $("#div_console").empty();
        for (var i in list_console)
            $("#div_console").append("<p class='mb-0'>"+list_console[i]+"</p>");
    };
    $(document).ready(function(){
        $.ajax({
            url: "/api/load_file_list",
            async: true,
            method: 'POST',
            data: {"data": JSON.stringify({})},
            data_type: "text",
            success: function (data) {
                // var data = JSON.parse(data);
                var d = data["data"];
                img_list = data["imgs"];
                numImgs = d.length;
                console.log("State: ", data["state"], numImgs, img_list.length);
                for (var i in d){
                    // var slice = toUTF8Array(img_list[i]);
                    slice = img_list[i];
                    // $("#list_slice_id").append("<div><a class='list-group-item list-group-item-action active' data-toggle='list'>"+i+"</a></div>");
                    if (i==0){
                        $("#list_img_part").append("<a class='list-group-item list-group-item-action active w-100' role='tab' id='list_"+i+"_list"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");

                        $("#sl_id_part").append("<div class='tab-pane show active mx-0' id='list_"+i+"' role='tabpanel' aria-labelledby='list_"+i+"_list'>" +
                    "   <div class='row'>" +
                    "            <div class=\"\" style=\"width: 2.56%\"></div>\n" +
                    "            <div class=\"border border-dark mx-0 \" style=\"width: 47.44%\" id=\"img_slice\">\n" +
                                    "<div class=\"h-100 w-100\" style='display: inline-block'>" +
                                    "    <h5 class=\"mx-auto px-auto text-center\">Original Image</h5>" +
                                    "    <img class='mx-auto' style=\"width:358px; height:358px; \" src='"+"data:image/png;base64,"+slice+"'/>" +
                                    "</div>" +
                    "            </div>\n" +
                    "            <div class=\"\" style=\"width: 2.56%\"></div>\n" +
                    "            <div class=\"border border-dark \" style=\"width: 47.44%\" id=\"img_seg_result\">\n" +
                                    "<div class=\"h-100  w-100 box_enhanced\" style='display: inline-block'>" +
                                    "    <h5 class=\"mx-auto px-auto text-center\">Segmented Result</h5>" +
                                    "    <img class='img_enhanced mx-auto' id='img_liver_seg_"+i+"' style=\"min-width:358px; height:358px; background-color: #cccccc;\"/>" +
                                    "</div>" +
                    "            </div>"+
                            "</div>"+
                            "</div>");
                    }
                    else {
                        $("#list_img_part").append("<a class='list-group-item list-group-item-action w-100' role='tab' id='list_" + i + "_list" + "' data-toggle='list' href='#list_" + i + "'>" + d[i] + "</a>");
                        $("#sl_id_part").append("<div class='tab-pane none mx-0' id='list_"+i+"' role='tabpanel' aria-labelledby='list_"+i+"_list'>" +
                    "   <div class='row'>" +
                    "            <div class=\"\" style=\"width: 2.56%\"></div>\n" +
                    "            <div class=\"border border-dark mx-0 \" style=\"width: 47.44%\" id=\"img_slice\">\n" +
                                    "<div class=\"h-100 w-100\" style='display: inline-block'>" +
                                    "    <h5 class=\"mx-auto px-auto text-center\">Original Image</h5>" +
                                    "    <img class=' mx-auto' style=\"width:358px; height:358px; \" src='"+"data:image/png;base64,"+slice+"'/>" +
                                    "</div>" +
                    "            </div>\n" +
                    "            <div class=\"\" style=\"width: 2.56%\"></div>\n" +
                    "            <div class=\"border border-dark \" style=\"width: 47.44%\" id=\"img_seg_result\">\n" +
                                    "<div class=\"h-100  w-100 box_enhanced\" style='display: inline-block'>" +
                                    "    <h5 class=\"mx-auto px-auto text-center\">Segmented Result</h5>" +
                                    "    <img class='img_enhanced mx-auto' id='img_liver_seg_"+i+"' style=\"min-width:358px; height:358px; background-color: #cccccc;\"/>" +
                                    "</div>" +
                    "            </div>"+
                            "</div>"+
                            "</div>");
                    }
                }
                $("#load_information").css("display","none");
                write_log_in_console("Loading medical images is finished.");
            }, error: function (){

            }
        });
        $("#btn_segment_liver").on("click", function () {
            $("#div_init").css("display", "none");
            $("#div_start").css("display", "block");
            $("#div_pause").css("display", "none");
            isPause = false;
            intervalSegment = setInterval(function () {
                if(!isPause){
                    $.ajax({
                        url: "/api/segment_liver",
                        async: false,
                        method: 'POST',
                        data: {"data": JSON.stringify({"target_img":idx})},
                        data_type: "text",
                        success: function (data) {
                            var text = data["console"];
                            var slice = data["img"]

                            write_log_in_console(text);
                            $("#list_img_part").children().removeClass("active");
                            $("#sl_id_part").children().removeClass("active");
                            $("#list_"+idx+"_list").addClass("active");
                            $("#list_"+idx).addClass("active");
                            $("#img_liver_seg_"+idx).attr("src","data:image/png;base64,"+slice);

                            try{
                                let y_position = document.querySelector("#list_"+(idx-1)+"_list").offsetTop;
                                $("#list_img_part").scrollTop(y_position);
                            }catch (e) {
                               let y_position = document.querySelector("#list_"+(idx)+"_list").offsetTop;
                               $("#list_img_part").scrollTop(y_position);
                            }

                            if (idx >= (numImgs-1)){
                                // $("#div_process").css("display", "none");
                               $("#div_start").css("display", "none");
                                $("#div_init").css("display", "block");
                                isPause = false;
                                idx = 0;
                                clearInterval(intervalSegment);
                                write_log_in_console("Target segmentation is finished.");
                            }
                            idx+=1;
                        }, error: function (){
                            idx+=1;

                        }
                    });
                }
            });
        });
        $("#btn_pause_segment_liver").on("click", function () {
            $("#div_init").css("display", "none");
            $("#div_start").css("display", "none");
            $("#div_pause").css("display", "block");
            isPause = true;
        });
        $("#btn_stop_segment_liver").on("click", function () {
            idx=0;
            $("#div_init").css("display", "block");
            $("#div_start").css("display", "none");
            $("#div_pause").css("display", "none");
            isPause = false;
            clearInterval(intervalSegment);
        });
        $("#btn_resume_segment_liver").on("click", function () {
            $("#div_init").css("display", "none");
            $("#div_start").css("display", "block");
            $("#div_pause").css("display", "none");
            isPause = false;
        });


        $("#btn_lirads_step2_back").on("click", function () {
            $("#smartwizard").smartWizard("prev");
            $("#btn_step2").removeClass("done");
            $("#step-2").css("display", "none");
            $("#step-1").css("display", "block");

        });

        $("#btn_lirads_step2_next").on("click", function () {
            $("#step-3").empty();
            $("#step-2").css("display", "none");
            $("#step-3").css("display", "block");
            $.post("/view/lirads_step3/", null, function (result) {
                $("#step-3").append(result);
            });
            $("#btn_step2").removeClass("active").addClass("done");
            $("#btn_step3").addClass("active");
            $("#smartwizard").smartWizard("next");

        });
    });
})(jQuery);