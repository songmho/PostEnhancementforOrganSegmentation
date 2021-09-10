(function () {
    var isPause = false;
    var isPause_pp = false;
    var idx= 0;
    var intervalSegment = null;
    var d;
    var is_segment_finished = false;
    var pp_step = 0;
    var intervalPP = null;
    var phase_info = null;

    $(document).ready(function(){
        write_log_in_console("Step 2. segmenting liver organ is started.");
        write_log_in_console("The liver organ segmentation model is being prepared.");
        $.ajax({
            url: "/api/load_file_list",
            async: true,
            method: 'POST',
            data: {"data": JSON.stringify({})},
            data_type: "text",
            success: function (data) {
                // var data = JSON.parse(data);
                d = data["data"];
                img_list = data["imgs"];
                phase_info = data["phase_info"];

                numImgs = d.length;
                for (var i in d){
                    // var slice = toUTF8Array(img_list[i]);
                    slice = img_list[i];
                    // $("#list_slice_id").append("<div><a class='list-group-item list-group-item-action active' data-toggle='list'>"+i+"</a></div>");
                    if (i==0){
                        $("#list_img_part").append("<a class='list-group-item list-group-item-action active w-100' role='tab' id='list_"+i+"_list"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");

                        $("#sl_id_part").append("<div class='tab-pane show active mx-0' id='list_"+i+"' role='tabpanel' aria-labelledby='list_"+i+"_list'>" +
                    "   <div class='row'>" +
                    "            <div class=\"\" style=\"width: 2.56%\"></div>\n" +
                    "            <div class=\"border border-dark p-2\" style=\"width: 47.44%\" id=\"img_slice\">\n" +
                                    "<div class=\"h-100 w-100\" style='display: inline-block'>" +
                                    "    <h5 class=\"mx-auto px-auto text-center\">Original Image</h5>" +
                    "                   <div class='mx-auto text-center'>" +
                                    "       <img class='mx-auto' style=\"width:358px; height:358px; \" src='"+"data:image/png;base64,"+slice+"'/>" +
                                    "   </div>"+
                                    "</div>" +
                    "            </div>\n" +
                    "            <div class=\"\" style=\"width: 2.56%\"></div>\n" +
                    "            <div class=\"border border-dark p-2\" style=\"width: 47.44%\" id=\"img_seg_result\">\n" +
                                    "<div class=\"h-100  w-100 box_enhanced\" style='display: inline-block'>" +
                                    "    <h5 class=\"mx-auto px-auto text-center\">Segmented Result</h5>" +
                    "                   <div class='mx-auto text-center'>" +
                                    "       <img class='img_enhanced mx-auto' id='img_liver_seg_"+i+"' style=\"min-width:358px; height:358px; background-color: #cccccc;\"/>" +
                                    "   </div>"+
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
                    "            <div class=\"border border-dark p-2\" style=\"width: 47.44%\" id=\"img_slice\">\n" +
                                    "<div class=\"h-100 w-100\" style='display: inline-block'>" +
                                    "    <h5 class=\"mx-auto px-auto text-center\">Original Image</h5>" +
                    "                   <div class='mx-auto text-center'>" +
                                    "       <img class='mx-auto' style=\"width:358px; height:358px; \" src='"+"data:image/png;base64,"+slice+"'/>" +
                                    "   </div>"+
                                    "</div>" +
                    "            </div>\n" +
                    "            <div class=\"\" style=\"width: 2.56%\"></div>\n" +
                    "            <div class=\"border border-dark p-2\" style=\"width: 47.44%\" id=\"img_seg_result\">\n" +
                                    "<div class=\"h-100  w-100 box_enhanced\" style='display: inline-block'>" +
                                    "    <h5 class=\"mx-auto px-auto text-center\">Segmented Result</h5>" +
                    "                   <div class='mx-auto text-center'>" +
                                    "       <img class='img_enhanced mx-auto' id='img_liver_seg_"+i+"' style=\"min-width:358px; height:358px; background-color: #cccccc;\"/>" +
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

        $("#btn_segment_liver").on("click", function () {
            $("#div_init").css("display", "none");
            $("#div_start").css("display", "block");
            $("#div_pause").css("display", "none");
            write_log_in_console("Segmenting liver organ is started.");
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
                            if (text>0)
                                write_log_in_console("Liver organ in CT slice "+d[idx]+" is segmented. (Area: "+text.toLocaleString()+" mm^2)");
                            else
                                write_log_in_console("Liver organ in CT slice "+d[idx]+" is not detected.");

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
                                is_segment_finished = true;
                                write_log_in_console("Segmenting liver organ is finished.");
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
            write_log_in_console("Segmenting liver organ is paused.");
            isPause = true;
        });
        $("#btn_stop_segment_liver").on("click", function () {
            idx=0;
            $("#div_init").css("display", "block");
            $("#div_start").css("display", "none");
            $("#div_pause").css("display", "none");
            write_log_in_console("Segmenting liver organ is stopped.");
            isPause = false;
            clearInterval(intervalSegment);
        });
        $("#btn_resume_segment_liver").on("click", function () {
            $("#div_init").css("display", "none");
            $("#div_start").css("display", "block");
            $("#div_pause").css("display", "none");
            write_log_in_console("Segmenting liver organ is resumed.");
            isPause = false;
        });


        $("#btn_post_process_liver").on("click", function () {
            console.log(phase_info);
            if (is_segment_finished){   // Segmentation is not finished
                $("#div_pp_init").css("display", "none");
                $("#div_pp_start").css("display", "block");
                $("#div_pp_pause").css("display", "none");
                write_log_in_console("Post-processing of segmenting liver is started.");
                isPause_pp = false;
                var cur_phase_id = 0;
                var cur_img_num = 0;
                intervalPP = setInterval(function () {
                    if (pp_step === 0)
                        pp_step = 1;
                    if(!isPause_pp){
                        $.ajax({
                            url: "/api/post-process_liver",
                            async: false,
                            method: 'POST',
                            data: {"data": JSON.stringify({"cur_phase_id":cur_phase_id, "step":pp_step})},
                            data_type: "text",
                            success: function (data) {

                                var text = data["console"];
                                write_log_in_console("Step "+String(pp_step)+" of post-processing for "+String(Object.keys(phase_info)[cur_phase_id])+" phase is done.")
                                if (pp_step >= 4){
                                    pp_step = 0;
                                    var slice = data["img"]

                                    for (let i=0; i<Object.keys(phase_info)[cur_phase_id]; i++){
                                        cur_img_num+=phase_info[Object.keys(phase_info)[cur_phase_id]];
                                    }
                                    console.log(cur_img_num, slice.length)
                                    for (var i in slice){
                                        console.log(String(parseInt(cur_img_num)+parseInt(i)), "#img_liver_seg_"+String(parseInt(cur_img_num)+parseInt(i)))
                                        // $("#img_liver_seg_"+String(parseInt(cur_img_num)+parseInt(i))).attr("src","");
                                        $("#img_liver_seg_"+String(parseInt(cur_img_num)+parseInt(i))).attr("src","data:image/png;base64,"+slice[i]);
                                    }
                                    write_log_in_console("Post-processing of segmenting liver for "+String(Object.keys(phase_info)[cur_phase_id])+" phase is done.");
                                    cur_phase_id++;
                                }
                                pp_step+=1;
                                if (cur_phase_id >= Object.keys(phase_info).length){
                                    $("#div_start").css("display", "none");
                                    $("#div_init").css("display", "block");
                                    isPause = false;
                                    pp_step = 0;
                                    cur_phase_id = 0;
                                    write_log_in_console("Post-processing of segmenting liver is done.");
                                    clearInterval(intervalPP);
                                }
                            }, error: function (){
                            }
                        });

                    }

                }, 500);
            }
            else{

            }

        });

        $("#btn_pause_post_process_liver").on("click", function () {
            $("#div_pp_init").css("display", "none");
            $("#div_pp_start").css("display", "none");
            $("#div_pp_pause").css("display", "block");
            write_log_in_console("Post-processing of segmenting liver is paused.");
            isPause_pp = true;
        });
        $("#btn_stop_post_process_liver").on("click", function () {
            idx=0;
            $("#div_pp_init").css("display", "block");
            $("#div_pp_start").css("display", "none");
            $("#div_pp_pause").css("display", "none");
            write_log_in_console("Post-processing of segmenting liver  is stopped.");
            isPause_pp = false;
            clearInterval(intervalPP);
        });
        $("#btn_resume_post_process_liver").on("click", function () {
            $("#div_pp_init").css("display", "none");
            $("#div_pp_start").css("display", "block");
            $("#div_pp_pause").css("display", "none");
            write_log_in_console("Post-processing of segmenting liver is resumed.");
            isPause_pp = false;
        });

        $("#btn_lirads_step2_back").on("click", function () {
            $.ajax({
                url: "/api/initialize_diagnosis_env",
                async: true,
                method: 'POST',
                data_type: "text",
                success: function (data) {
                    console.log("INITIALIZED");
                }, error: function (){
                }
            });
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