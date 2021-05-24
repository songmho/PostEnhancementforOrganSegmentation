(function () {

    var isPause = false;
    var idx= 0;
    var d;
    var intervalSegment = null;
    $(document).ready(function(){
        write_log_in_console("Step 5. Determining tumor type is started.");
        write_log_in_console("The tumor type classification model is being prepared.");

        $.ajax({
        url:"/api/get_tumor_group_data",
        async: true,
        method: "POST",
        data: {"data": JSON.stringify({})},
        data_type: "text",
        success: function (data) {
            d = data["data"];
            var img_list = data["imgs"];
            numImgs = d.length;
            console.log(img_list);
            var img_list_keys = Object.keys(img_list);
            for (var i in d){
                slice = img_list[img_list_keys[i]];

                console.log(slice);
                if (i==0){
                    $("#list_slices_step_5").append("<a class='list-group-item list-group-item-action active w-100'" +
                        " role='tab' id='list_"+i+"_list_tumors_step5"+"' data-toggle='list' href='#list_"+i+"_step5'>"+d[i]+"</a>");


                    var structure =
                        "            <div class=\"h-100 tab-pane show active\" id=\"list_"+i+"_step5\" role=\"tabpanel\" aria-labelledby=\"list_"+i+"_list_tumors_step5\">\n" +
                        "                <div class=\"row h-100\">\n" +
                        "                    <div style='width: 2.56%'></div>\n" +
                        "                    <div id=\"div_img\" class='border border-dark p-2' style=\"width: 47.44%; height: 75%\">\n"+
                        "                            <h5  class='text-center'>Tumor Images</h5>" +
                        "                        <div style=\"height: 50%;\" class=\"row mx-0\">\n";
                    if (Object.keys(slice).includes("plain")){
                        structure+=                         "                            <div class=\"w-50\">\n" +
                        "                            <img id=\"img_plain_"+i+"\" src=data:image/png;base64,"+slice["plain"]+" class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Plain</h6>\n" +
                        "                            </div>\n";
                    }else{
                                                structure+=                         "                            <div class=\"w-50\">\n" +
                        "                            <img id=\"img_plain_"+i+"\" src=data: class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Plain</h6>\n" +
                        "                            </div>\n";
                    }
                    if(Object.keys(slice).includes("arterial")){
                        structure+=                         "                            <div class=\"w-50 mx-auto\">\n" +
                        "                            <img id=\"img_ap_"+i+"\"  src=data:image/png;base64,"+slice["arterial"]+" class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Arterial Phase</h6>\n" +
                        "                            </div>\n" ;
                    }else{
                        structure+=                         "                            <div class=\"w-50 mx-auto\">\n" +
                        "                            <img id=\"img_ap_"+i+"\"  src=data: class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Arterial Phase</h6>\n" +
                        "                            </div>\n" ;

                    }
                    structure +=
                        "                        </div>\n" +
                        "                        <div style=\"height: 50%;\"  class=\"row mx-0\">\n";
                    if (Object.keys(slice).includes("venous")){
                        structure+=
                        "                            <div class=\"w-50\" >\n" +
                        "\n" +
                        "                            <img id=\"img_pvp_"+i+"\" src=data:image/png;base64,"+slice["venous"]+" class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Portal Venous Phase</h6>\n" +
                        "                            </div>\n";
                    }else{
                        structure+=
                        "                            <div class=\"w-50\" >\n" +
                        "\n" +
                        "                            <img id=\"img_pvp_"+i+"\" src=data: class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Portal Venous Phase</h6>\n" +
                        "                            </div>\n";
                    }
                    if (Object.keys(slice).includes("delay")){
                        structure +=
                        "                            <div class=\"w-50\">\n" +
                        "\n" +
                        "                            <img id=\"img_dp_"+i+"\"  src=data:image/png;base64,"+slice["delay"]+" class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Delayed Phase</h6>\n" +
                        "                            </div>\n";
                    }else{
                        structure +=
                        "                            <div class=\"w-50\">\n" +
                        "\n" +
                        "                            <img id=\"img_dp_"+i+"\"  src=data: class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Delayed Phase</h6>\n" +
                        "                            </div>\n";

                    }
                    structure+=    "                        </div>\n" +
                        "                    </div>\n" +
                        "                    <div style='width: 2.56%'></div>\n" +
                        "                    <div id=\"div_features_"+i+"\" style='width: 47.44%' class=\"mx-0 p-2 border border-dark h-75\">\n" +
                        "                        <h5 class='text-center'>Predicted Tumor Type</h5>\n" +
                        "<h6 id='txt_tumor_type"+i+"'></h6>"+
                        "                    </div>\n" +
                        "                </div>\n" +
                        "            </div>\n" +
                        "        " +
                        "";

                    $("#sl_id_tumor_groups").append(structure);

                }else{
                    $("#list_slices_step_5").append("<a class='list-group-item list-group-item-action w-100'" +
                        " role='tab' id='list_"+i+"_list_tumors_step5"+"' data-toggle='list' href='#list_"+i+"_step5'>"+d[i]+"</a>");

                    var structure =
                        "            <div class=\"h-100 tab-pane\" id=\"list_"+i+"_step5\" role=\"tabpanel\" aria-labelledby=\"list_"+i+"_list_tumors_step5\">\n" +
                        "                <div class=\"row h-100\">\n" +
                        "                    <div style='width: 2.56%'></div>\n" +
                        "                    <div id=\"div_img\" class='border border-dark p-2' style=\"width: 47.44%; height: 75%\">\n"+
                        "                            <h5  class='text-center'>Tumor Images</h5>" +
                        "                        <div style=\"height: 50%;\" class=\"row mx-0\">\n";
                    if (Object.keys(slice).includes("plain")){
                        structure+=                         "                            <div class=\"w-50\">\n" +
                        "                            <img id=\"img_plain_"+i+"\" src=data:image/png;base64,"+slice["plain"]+" class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Plain</h6>\n" +
                        "                            </div>\n";
                    }else{
                        structure+=                         "                            <div class=\"w-50\">\n" +
                        "                            <img id=\"img_plain_"+i+"\" src=data: class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Plain</h6>\n" +
                        "                            </div>\n";
                    }
                    if(Object.keys(slice).includes("arterial")){
                        structure+=                         "                            <div class=\"w-50 mx-auto\">\n" +
                        "                            <img id=\"img_ap_"+i+"\"  src=data:image/png;base64,"+slice['arterial']+" class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Arterial Phase</h6>\n" +
                        "                            </div>\n" ;
                    }else{
                        structure+=                         "                            <div class=\"w-50 mx-auto\">\n" +
                        "                            <img id=\"img_ap_"+i+"\"  src=data: class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Arterial Phase</h6>\n" +
                        "                            </div>\n" ;

                    }
                    structure +=
                        "                        </div>\n" +
                        "                        <div style=\"height: 50%;\"  class=\"row mx-0\">\n";
                    if (Object.keys(slice).includes("venous")){
                        structure+=
                        "                            <div class=\"w-50\" >\n" +
                        "\n" +
                        "                            <img id=\"img_pvp_"+i+"\" src=data:image/png;base64,"+slice["venous"]+" class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Portal Venous Phase</h6>\n" +
                        "                            </div>\n";
                    }else{
                        structure+=
                        "                            <div class=\"w-50\" >\n" +
                        "\n" +
                        "                            <img id=\"img_pvp_"+i+"\" src=data: class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Portal Venous Phase</h6>\n" +
                        "                            </div>\n";
                    }
                    if (Object.keys(slice).includes("delay")){
                        structure +=
                        "                            <div class=\"w-50\">\n" +
                        "\n" +
                        "                            <img id=\"img_dp_"+i+"\"  src=data:image/png;base64,"+slice["delay"]+" class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Delayed Phase</h6>\n" +
                        "                            </div>\n";
                    }else{
                        structure +=
                        "                            <div class=\"w-50\">\n" +
                        "\n" +
                        "                            <img id=\"img_dp_"+i+"\"  src=data: class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                        "                                <h6 class=\"text-center\">Delayed Phase</h6>\n" +
                        "                            </div>\n";

                    }
                    structure+=    "                        </div>\n" +
                        "                    </div>\n" +
                        "                    <div style='width: 2.56%'></div>\n" +
                        "                    <div id=\"div_features_"+i+"\" style='width: 47.44%' class=\"mx-0 p-2 border border-dark h-75\">\n" +
                        "                        <h5 class='text-center'>Predicted Tumor Type</h5>\n" +
                        "<h6 id='txt_tumor_type"+i+"'></h6>"+
                        "                    </div>\n" +
                        "                </div>\n" +
                        "            </div>\n" +
                        "        " +
                        "";

                    $("#sl_id_tumor_groups").append(structure);


                    // $("#sl_id_tumor_groups").append(
                    //     "            <div class=\"h-100  ml-2 mt-4 tab-pane\" id=\"list_"+i+"\" role=\"tabpanel\" aria-labelledby=\"list_"+i+"_list_tumors_step5\">\n" +
                    //     "                <div class=\"row h-100\">\n" +
                    //     "                    <div id=\"div_img\" style=\"width: 50%; height: 70%\">\n" +
                    //     "                        <div style=\"height: 50%;\" class=\"row mx-0\">\n" +
                    //     "                            <div class=\"w-50\">\n" +
                    //     "                            <img id=\"img_plain_"+i+"\"  class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                    //     "                                <h6 class=\"text-center\">Plain</h6>\n" +
                    //     "                            </div>\n" +
                    //     "                            <div class=\"w-50 mx-auto\">\n" +
                    //     "                            <img id=\"img_ap_"+i+"\"  class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                    //     "                                <h6 class=\"text-center\">Arterial Phase</h6>\n" +
                    //     "                            </div>\n" +
                    //     "                        </div>\n" +
                    //     "                        <div style=\"height: 50%;\"  class=\"row mx-0\">\n" +
                    //     "                            <div class=\"w-50\" >\n" +
                    //     "\n" +
                    //     "                            <img id=\"img_pvp_"+i+"\" class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                    //     "                                <h6 class=\"text-center\">Portal Venous Phase</h6>\n" +
                    //     "                            </div>\n" +
                    //     "                            <div class=\"w-50\">\n" +
                    //     "\n" +
                    //     "                            <img id=\"img_dp_"+i+"\"  class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                    //     "                                <h6 class=\"text-center\">Delayed Phase</h6>\n" +
                    //     "                            </div>\n" +
                    //     "                        </div>\n" +
                    //     "                    </div>\n" +
                    //     "                    <div id=\"div_features_"+i+"\" class=\"w-50 mx-0 p-2 border border-info h-75\">\n" +
                    //     "                        <h5>Predicted Tumor Type</h5>\n" +
                    //     "                    </div>\n" +
                    //     "                </div>\n" +
                    //     "            </div>\n" +
                    //     "        " +
                    //     "")

                }

            }

            write_log_in_console("Loading tumor groups is finished.");
        },error: function (err) {

        }
    });

    $("#btn_determine_type").on("click", function () {
        write_log_in_console("Classifying tumor type is started.");
        $("#div_init_step5").css("display", "none");
        $("#div_start_step5").css("display", "block");
        $("#div_pause_step5").css("display", "none");
        isPause = false;
        intervalSegment = setInterval(function () {
            if (!isPause) {
                    $.ajax({
                        url: "/api/determin_tumor_type",
                        async: false,
                        method: "POST",
                        data: {"data": JSON.stringify({})},
                        data_type: "text",
                        success: function (data) {
                            var tumor_type = data["data"];
                            write_log_in_console("Tumor type of the "+d[idx]+" is classified to "+tumor_type.split(" ")[0]+".");

                            $("#list_slices_step_5").children().removeClass("active");
                            $("#sl_id_tumor_groups").children().removeClass("active");
                            $("#list_"+idx+"_list_tumors_step5").addClass("active");
                            $("#list_"+idx+"_step5").addClass("active");
                            $("#txt_tumor_type"+idx).text(tumor_type);

                            try{
                                let y_position = document.querySelector("#list_"+(idx-1)+"_list_tumors_step5").offsetTop;
                                $("#list_slices_step_5").scrollTop(y_position);
                            }catch (e) {
                               let y_position = document.querySelector("#list_"+(idx)+"_list_tumors_step5").offsetTop;
                               $("#list_slices_step_5").scrollTop(y_position);
                            }



                            if (idx >= (numImgs-1)){
                                // $("#div_process").css("display", "none");
                               $("#div_start_step5").css("display", "none");
                                $("#div_init_step5").css("display", "block");
                                isPause = false;
                                idx = 0;
                                clearInterval(intervalSegment);
                                write_log_in_console("Classifying tumor type is finished.");
                            }
                            idx+=1;
                        }, error: function () {

                        }
                    });

                }
            }, 500);
        });

        $("#btn_pause_step5").on("click", function () {
            write_log_in_console("Classifying tumor type is paused.");
            $("#div_init_step5").css("display", "none");
            $("#div_start_step5").css("display", "none");
            $("#div_pause_step5").css("display", "block");
            isPause = true;
        });
        $("#btn_stop_step5").on("click", function () {
            idx=0;
            write_log_in_console("Classifying tumor type is stopped.");
            $("#div_init_step5").css("display", "block");
            $("#div_start_step5").css("display", "none");
            $("#div_pause_step5").css("display", "none");
            isPause = false;
            clearInterval(intervalSegment);
        });
        $("#btn_resume_step5").on("click", function () {

            write_log_in_console("Classifying tumor type is resumed.");
            $("#div_init_step5").css("display", "none");
            $("#div_start_step5").css("display", "block");
            $("#div_pause_step5").css("display", "none");
            isPause = false;
        });


        $("#btn_lirads_step5_back").on("click", function () {
            $("#smartwizard").smartWizard("prev");
            $("#btn_step5").removeClass("done");
            $("#step-5").css("display", "none");
            $("#step-4").css("display", "block");

        });

        $("#btn_lirads_step5_next").on("click", function () {
            $("#step-6").empty();
            $("#step-5").css("display", "none");
            $("#step-6").css("display", "block");
            $.post("/view/lirads_step6/", null, function (result) {
                $("#step-6").append(result);
            });
            $("#btn_step5").removeClass("active").addClass("done");
            $("#btn_step6").addClass("active");
            $("#smartwizard").smartWizard("next");

        });
    });
})(jQuery);