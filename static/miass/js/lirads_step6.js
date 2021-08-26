(function () {

    var isPause = false;
    var idx= 0;
    var intervalSegment = null;
    var d;
    // var d = ["Tumor Group 1", "Tumor Group 2", "Tumor Group 3", "Tumor Group 4"];
    $(document).ready(function(){

        write_log_in_console("Step 6. Computing Li-RADS features is started.");
        write_log_in_console("The tumor data is being loaded.");
        $.ajax({
        url:"/api/load_tumor_group_list_step6",
        async: true,
        method: "POST",
        data: {"data": JSON.stringify({})},
        data_type: "text",
        success: function (data) {
            d = data["data"];
            numImgs = d.length;
            console.log(d);
            console.log(numImgs);
            for (var i in d) {
                if (i == 0) {
                    $("#list_slices_step_6").append("<a class='list-group-item list-group-item-action active w-100'" +
                        " role='tab' id='list_"+i+"_list_tumors_step6"+"' data-toggle='list' href='#list_"+i+"_lirads'>"+d[i]+"</a>");
                    $("#sl_id_lirads_features").append("" +
                "            <div class=\"tab-pane show active\" id=\"list_"+i+"_lirads\" role=\"tabpanel\" aria-labelledby=\"list_"+i+"_list_tumors_step6"+"\">\n" +
                "                <div class=\"row mx-0\">\n" +
                "                    <h6>Type of APHE: </h6>\n" +
                "                    <h6 id=\"txt_aphe_type_"+i+"\" class='ml-1'</h6>\n" +
                "                </div>\n" +
                "                <div class=\"row mx-0\">\n" +
                "                    <h6>Tumor Size: </h6>\n" +
                "                    <h6 id=\"txt_tumor_size_"+i+"\" class='ml-1'></h6>\n" +
                "                </div>\n" +
                "                <div class=\"mx-0\">\n" +
                "                    <h6>Major Features </h6>\n" +
                "                    <div class=\"row mx-0 ml-2\">\n" +
                "                        <h6>Existence of Capsule: </h6>\n" +
                "                        <h6 id=\"txt_capsule_"+i+"\" class='ml-1'></h6>\n" +
                "                    </div>\n" +
                "                    <div class=\"row mx-0 ml-2\">\n" +
                "                        <h6>Existence of Washout: </h6>\n" +
                "                        <h6 id=\"txt_washout_"+i+"\" class='ml-1'></h6>\n" +
                "                    </div>\n" +
                "                    <div class=\"row mx-0 ml-2\">\n" +
                "                        <h6>Existence of Threshold Growth: </h6>\n" +
                "                        <h6 id=\"txt_th_growth_"+i+"\" class='ml-1'></h6>\n" +
                "                    </div>\n" +
                "                </div>\n" +
                "            </div>" +
                "");

                } else {
                    $("#list_slices_step_6").append("<a class='list-group-item list-group-item-action w-100'" +
                        " role='tab' id='list_"+i+"_list_tumors_step6"+"' data-toggle='list' href='#list_"+i+"_lirads'>"+d[i]+"</a>");
                    $("#sl_id_lirads_features").append("" +
                "            <div class=\"tab-pane\" id=\"list_"+i+"_lirads\" role=\"tabpanel\" aria-labelledby=\"list_"+i+"_list_tumors_step6"+"\">\n" +
                "                <div class=\"row mx-0\">\n" +
                "                    <h6>Type of APHE: </h6>\n" +
                "                    <h6 id=\"txt_aphe_type_"+i+"\" class='ml-1'</h6>\n" +
                "                </div>\n" +
                "                <div class=\"row mx-0\">\n" +
                "                    <h6>Tumor Size: </h6>\n" +
                "                    <h6 id=\"txt_tumor_size_"+i+"\" class='ml-1'></h6>\n" +
                "                </div>\n" +
                "                <div class=\"mx-0\">\n" +
                "                    <h6>Major Features </h6>\n" +
                "                    <div class=\"row mx-0 ml-2\">\n" +
                "                        <h6>Existence of Capsule: </h6>\n" +
                "                        <h6 id=\"txt_capsule_"+i+"\" class='ml-1'></h6>\n" +
                "                    </div>\n" +
                "                    <div class=\"row mx-0 ml-2\">\n" +
                "                        <h6>Existence of Washout: </h6>\n" +
                "                        <h6 id=\"txt_washout_"+i+"\" class='ml-1'></h6>\n" +
                "                    </div>\n" +
                "                    <div class=\"row mx-0 ml-2\">\n" +
                "                        <h6>Existence of Threshold Growth: </h6>\n" +
                "                        <h6 id=\"txt_th_growth_"+i+"\" class='ml-1'></h6>\n" +
                "                    </div>\n" +
                "                </div>\n" +
                "            </div>" +
                "");
                }
            }

            write_log_in_console("Finished loading tumor group data.");
        }, error:function () {

            }
        });


        $("#btn_load_prv_data").on("click", function () {

        });
        $("#btn_compute_feature").on("click", function () {
            write_log_in_console("Computing LI-RADS features of tumors is started.");
            $("#div_init_step6").css("display", "none");
            $("#div_start_step6").css("display", "block");
            $("#div_pause_step6").css("display", "none");
            isPause = false;
            intervalSegment = setInterval(function () {
                if (!isPause) {
                        $.ajax({
                            url: "/api/compute_lirads_feature",
                            async: false,
                            method: "POST",
                            data: {"data": JSON.stringify({"tumor_id":idx})},
                            data_type: "text",
                            success: function (data) {
                                var features = data["data"];
                                var num_major = 0;
                                if (features["capsule"])
                                    num_major+=1;
                                if (features["washout"])
                                    num_major+=1;
                                if (features["threshold_growth"])
                                    num_major+=1;
                                write_log_in_console("LI-RADS features for "+d[idx]+"is computed; APHE Type: "+ features["APHE_Type"]+ ", Size: "+features["tumor_size"]+" , # of Major Features: "+num_major);
                                $("#txt_aphe_type_"+idx).text(features["APHE_Type"]);
                                $("#txt_tumor_size_"+idx).text(features["tumor_size"]);
                                $("#txt_capsule_"+idx).text(features["capsule"]);
                                $("#txt_washout_"+idx).text(features["washout"]);
                                if (features["threshold_growth"]==null)
                                    $("#txt_th_growth_"+idx).text("Not Input");
                                else
                                    $("#txt_th_growth_"+idx).text(features["threshold_growth"]);


                                $("#list_slices_step_6").children().removeClass("active");
                                $("#sl_id_lirads_features").children().removeClass("active");
                                $("#list_"+idx+"_list_tumors_step6").addClass("active");
                                $("#list_"+idx+"_lirads").addClass("active");

                                try{
                                    let y_position = document.querySelector("#list_"+(idx-1)+"_list_tumors_step6").offsetTop;
                                    $("#list_slices_step_6").scrollTop(y_position);
                                }catch (e) {
                                   let y_position = document.querySelector("#list_"+(idx)+"_list_tumors_step6").offsetTop;
                                   $("#list_slices_step_6").scrollTop(y_position);
                                }

                                if (idx >= (numImgs-1)){
                                    // $("#div_process").css("display", "none");
                                   $("#div_start_step5").css("display", "none");
                                    $("#div_init_step5").css("display", "block");
                                    isPause = false;
                                    idx = 0;
                                    clearInterval(intervalSegment);
                                    write_log_in_console("Computing LI-RADS features of tumors is finished.");
                                }
                                idx+=1;
                            }, error: function () {

                            }
                        });

                    }
                }, 500);
            });

        $("#btn_pause_step6").on("click", function () {
            write_log_in_console("Computing LI-RADS features of tumors is paused.");
            $("#div_init_step6").css("display", "none");
            $("#div_start_step6").css("display", "none");
            $("#div_pause_step6").css("display", "block");
            isPause = true;
        });
        $("#btn_stop_step6").on("click", function () {
            write_log_in_console("Computing LI-RADS features of tumors is stopped.");
            idx=0;
            $("#div_init_step6").css("display", "block");
            $("#div_start_step6").css("display", "none");
            $("#div_pause_step6").css("display", "none");
            isPause = false;
            clearInterval(intervalSegment);
        });
        $("#btn_resume_step6").on("click", function () {
            write_log_in_console("Computing LI-RADS features of tumors is resumed.");
            $("#div_init_step6").css("display", "none");
            $("#div_start_step6").css("display", "block");
            $("#div_pause_step6").css("display", "none");
            isPause = false;
        });



        $("#btn_lirads_step6_back").on("click", function () {
            $("#smartwizard").smartWizard("prev");
            $("#btn_step6").removeClass("done");
            $("#step-6").css("display", "none");
            $("#step-5").css("display", "block");

        });

        $("#btn_lirads_step6_next").on("click", function () {
            $("#step-7").empty();
            $("#step-6").css("display", "none");
            $("#step-7").css("display", "block");
            $.post("/view/lirads_step7/", null, function (result) {
                $("#step-7").append(result);
            });
            $("#btn_step6").removeClass("active").addClass("done");
            $("#btn_step7").addClass("active");
            $("#smartwizard").smartWizard("next");

        });
    });
})(jQuery);