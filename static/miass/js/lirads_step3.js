(function () {
    var isPause = false;
    var idx= 0;
    var d;
    var intervalSegment = null;
    $(document).ready(function(){
        write_log_in_console("Step 3. segmenting tumor regions is started.");
        write_log_in_console("The tumor region segmentation model is being prepared.");
        $.ajax({
            url: "/api/load_setCT_a",
            async: true,
            method: 'POST',
            data: {"data": JSON.stringify({})},
            data_type: "text",
            success: function (data) {
                // var data = JSON.parse(data);
                d = data["data"];
                img_list = data["imgs"];
                numImgs = d.length;
                console.log("State: ", data["state"], numImgs, img_list.length);
                for (var i in d){
                    // var slice = toUTF8Array(img_list[i]);
                    slice = img_list[i];
                    // $("#list_slice_id").append("<div><a class='list-group-item list-group-item-action active' data-toggle='list'>"+i+"</a></div>");
                    if (i==0){
                        $("#list_img_part_tumor").append("<a class='list-group-item list-group-item-action active w-100' role='tab' id='list_"+i+"_list_tumor"+"' data-toggle='list' href='#list_"+i+"_tumor'>"+d[i]+"</a>");

                        $("#sl_id_part_tumor").append("<div class='tab-pane show active mx-0' id='list_"+i+"_tumor' role='tabpanel' aria-labelledby='list_"+i+"_list_tumor'>" +
                    "   <div class='row'>" +
                    "            <div class=\"\" style=\"width: 2.56%\"></div>\n" +
                    "            <div class=\"border border-dark p-2\" style=\"width: 47.44%\" id=\"img_slice_tumor\">\n" +
                                    "<div class=\"h-100 w-100\" style='display: inline-block'>" +
                                    "    <h5 class=\"mx-auto px-auto text-center\">Original Image</h5>" +
                    "                   <div class='mx-auto text-center'>" +
                                    "       <img class='mx-auto' style=\"width:358px; height:358px; \" src='"+"data:image/png;base64,"+slice+"'/>" +
                                    "   </div>"+
                                    "</div>" +
                    "            </div>\n" +
                    "            <div class=\"\" style=\"width: 2.56%\"></div>\n" +
                    "            <div class=\"border border-dark p-2\" style=\"width: 47.44%\" id=\"img_seg_result_tumor\">\n" +
                                    "<div class=\"h-100  w-100 box_enhanced\" style='display: inline-block'>" +
                                    "    <h5 class=\"mx-auto px-auto text-center\">Segmented Result</h5>" +
                    "                   <div class='mx-auto text-center'>" +
                                    "       <img class='img_enhanced mx-auto' id='img_tumor_seg_"+i+"' style=\"min-width:358px; height:358px; background-color: #cccccc;\"/>" +
                                    "   </div>"+
                                    "</div>" +
                    "            </div>"+
                            "</div>"+
                            "</div>");
                    }
                    else {
                        $("#list_img_part_tumor").append("<a class='list-group-item list-group-item-action w-100' role='tab' id='list_" + i + "_list_tumor" + "' data-toggle='list' href='#list_" + i + "_tumor'>" + d[i] + "</a>");
                        $("#sl_id_part_tumor").append("<div class='tab-pane none mx-0' id='list_"+i+"_tumor' role='tabpanel' aria-labelledby='list_"+i+"_list_tumor'>" +
                    "   <div class='row'>" +
                    "            <div class=\"\" style=\"width: 2.56%\"></div>\n" +
                    "            <div class=\"border border-dark p-2\" style=\"width: 47.44%\" id=\"img_slice_tumor\">\n" +
                                    "<div class=\"h-100 w-100\" style='display: inline-block'>" +
                                    "    <h5 class=\"mx-auto px-auto text-center\">Original Image</h5>" +
                    "                   <div class='mx-auto text-center'>" +
                                    "       <img class='mx-auto' style=\"width:358px; height:358px; \" src='"+"data:image/png;base64,"+slice+"'/>" +
                                    "   </div>"+
                                    "</div>" +
                    "            </div>\n" +
                    "            <div class=\"\" style=\"width: 2.56%\"></div>\n" +
                    "            <div class=\"border border-dark p-2\" style=\"width: 47.44%\" id=\"img_seg_result_tumor\">\n" +
                                    "<div class=\"h-100  w-100 box_enhanced\" style='display: inline-block'>" +
                                    "    <h5 class=\"mx-auto px-auto text-center\">Segmented Result</h5>" +
                    "                   <div class='mx-auto text-center'>" +
                                    "       <img class='img_enhanced mx-auto' id='img_tumor_seg_"+i+"' style=\"min-width:358px; height:358px; background-color: #cccccc;\"/>" +
                                    "   </div>"+
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
        $("#btn_segment_tumor").on("click", function () {
            write_log_in_console("Segmenting  tumor region is started.");
            $("#div_init_tumor").css("display", "none");
            $("#div_start_tumor").css("display", "block");
            $("#div_pause_tumor").css("display", "none");
            isPause = false;
            intervalSegment = setInterval(function () {
                if(!isPause){
                    $.ajax({
                        url: "/api/segment_tumor",
                        async: false,
                        method: 'POST',
                        data: {"data": JSON.stringify({"target_img":idx})},
                        data_type: "text",
                        success: function (data) {
                            var text = data["console"];
                            var slice = data["img"];
                            console.log(text);
                            if (text["count"]>0)
                                write_log_in_console("Tumor regions in CT slice "+d[idx]+" is segmented. (# of Tumors:"+text["count"]+", Whole Area: "+text["area"].toLocaleString()+" mm)");
                            else
                                write_log_in_console("Any tumor region in CT slice "+d[idx]+" is not detected.");

                            $("#list_img_part_tumor").children().removeClass("active");
                            $("#sl_id_part_tumor").children().removeClass("active");
                            $("#list_"+idx+"_list_tumor").addClass("active");
                            $("#list_"+idx+"_tumor").addClass("active");
                            $("#img_tumor_seg_"+idx).attr("src","data:image/png;base64,"+slice);

                            try{
                                let y_position = document.querySelector("#list_"+(idx-1)+"_list_tumor").offsetTop;
                                $("#list_img_part_tumor").scrollTop(y_position);
                            }catch (e) {
                               let y_position = document.querySelector("#list_"+(idx)+"_list_tumor").offsetTop;
                               $("#list_img_part_tumor").scrollTop(y_position);
                            }

                            if (idx >= (numImgs-1)){
                                // $("#div_process").css("display", "none");
                               $("#div_start_tumor").css("display", "none");
                                $("#div_init_tumor").css("display", "block");
                                isPause = false;
                                idx = 0;
                                clearInterval(intervalSegment);
                                write_log_in_console("Segmenting  tumor region is finished.");
                            }
                            idx+=1;
                        }, error: function (){
                            idx+=1;

                        }
                    });
                }
            });
        });
        $("#btn_pause_segment_tumor").on("click", function () {
            $("#div_init_tumor").css("display", "none");
            $("#div_start_tumor").css("display", "none");
            $("#div_pause_tumor").css("display", "block");
            write_log_in_console("Segmenting  tumor region is paused.");
            isPause = true;
        });
        $("#btn_stop_segment_tumor").on("click", function () {
            idx=0;
            $("#div_init_tumor").css("display", "block");
            $("#div_start_tumor").css("display", "none");
            $("#div_pause_tumor").css("display", "none");
            write_log_in_console("Segmenting  tumor region is stopped.");
            isPause = false;
            clearInterval(intervalSegment);
        });
        $("#btn_resume_segment_tumor").on("click", function () {
            $("#div_init_tumor").css("display", "none");
            $("#div_start_tumor").css("display", "block");
            $("#div_pause_tumor").css("display", "none");
            write_log_in_console("Segmenting  tumor region is resumed.");
            isPause = false;
        });

        $("#btn_lirads_step3_back").on("click", function () {
            $("#smartwizard").smartWizard("prev");
            $("#btn_step3").removeClass("done");
            $("#step-3").css("display", "none");
            $("#step-2").css("display", "block");

        });

        $("#btn_lirads_step3_next").on("click", function () {
            $("#step-4").empty();
            $("#step-3").css("display", "none");
            $("#step-4").css("display", "block");
            $.post("/view/lirads_step4/", null, function (result) {
                $("#step-4").append(result);
            });
            $("#btn_step3").removeClass("active").addClass("done");
            $("#btn_step4").addClass("active");
            $("#smartwizard").smartWizard("next");

        });
    });
})(jQuery);