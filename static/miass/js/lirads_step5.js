(function () {

    var d = ["Tumor Group 1", "TUmor Group 2", "Tumor Group 3"];
    $(document).ready(function(){
        write_log_in_console("Step 5. Determining tumor type is started.");

            $.ajax({
            url:"/api/load_tumor_group_list",
            async: true,
            method: "POST",
            data: {"data": JSON.stringify({})},
            data_type: "text",
            success: function (data) {
                var d = data["data"];
                var img_list = data["imgs"];
                numImgs = d.lenght;

                for (var i in d){
                    slice = img_list[i];

                    if (i==0){
                        $("#list_slices_step_5").append("<a class='list-group-item list-group-item-action active w-100'" +
                            " role='tab' id='list_"+i+"_list_tumors_step5"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
                        $("#sl_id_tumor_groups").append(
                            "            <div class=\"h-100  ml-2 mt-4 tab-pane show active\" id=\"list_"+i+"\" role=\"tabpanel\" aria-labelledby=\"list_"+i+"_list_tumors_step5\">\n" +
                            "                <div class=\"row h-100\">\n" +
                            "                    <div id=\"div_img\" style=\"width: 50%; height: 70%\">\n" +
                            "                        <div style=\"height: 50%;\" class=\"row mx-0\">\n" +
                            "                            <div class=\"w-50\">\n" +
                            "                            <img id=\"img_plain_"+i+"\"  class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                            "                                <h6 class=\"text-center\">Plain</h6>\n" +
                            "                            </div>\n" +
                            "                            <div class=\"w-50 mx-auto\">\n" +
                            "                            <img id=\"img_ap_"+i+"\"  class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                            "                                <h6 class=\"text-center\">Arterial Phase</h6>\n" +
                            "                            </div>\n" +
                            "                        </div>\n" +
                            "                        <div style=\"height: 50%;\"  class=\"row mx-0\">\n" +
                            "                            <div class=\"w-50\" >\n" +
                            "\n" +
                            "                            <img id=\"img_pvp_"+i+"\" class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                            "                                <h6 class=\"text-center\">Portal Venous Phase</h6>\n" +
                            "                            </div>\n" +
                            "                            <div class=\"w-50\">\n" +
                            "\n" +
                            "                            <img id=\"img_dp_"+i+"\"  class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                            "                                <h6 class=\"text-center\">Delayed Phase</h6>\n" +
                            "                            </div>\n" +
                            "                        </div>\n" +
                            "                    </div>\n" +
                            "                    <div id=\"div_features_"+i+"\" class=\"w-50 mx-0 p-2 border border-info h-75\">\n" +
                            "                        <h5>Predicted Tumor Type</h5>\n" +
                            "                    </div>\n" +
                            "                </div>\n" +
                            "            </div>\n" +
                            "        " +
                            "")

                    }else{
                        $("#list_slices_step_5").append("<a class='list-group-item list-group-item-action w-100'" +
                            " role='tab' id='list_"+i+"_list_tumors_step5"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
                        $("#sl_id_tumor_groups").append(
                            "            <div class=\"h-100  ml-2 mt-4 tab-pane\" id=\"list_"+i+"\" role=\"tabpanel\" aria-labelledby=\"list_"+i+"_list_tumors_step5\">\n" +
                            "                <div class=\"row h-100\">\n" +
                            "                    <div id=\"div_img\" style=\"width: 50%; height: 70%\">\n" +
                            "                        <div style=\"height: 50%;\" class=\"row mx-0\">\n" +
                            "                            <div class=\"w-50\">\n" +
                            "                            <img id=\"img_plain_"+i+"\"  class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                            "                                <h6 class=\"text-center\">Plain</h6>\n" +
                            "                            </div>\n" +
                            "                            <div class=\"w-50 mx-auto\">\n" +
                            "                            <img id=\"img_ap_"+i+"\"  class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                            "                                <h6 class=\"text-center\">Arterial Phase</h6>\n" +
                            "                            </div>\n" +
                            "                        </div>\n" +
                            "                        <div style=\"height: 50%;\"  class=\"row mx-0\">\n" +
                            "                            <div class=\"w-50\" >\n" +
                            "\n" +
                            "                            <img id=\"img_pvp_"+i+"\" class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                            "                                <h6 class=\"text-center\">Portal Venous Phase</h6>\n" +
                            "                            </div>\n" +
                            "                            <div class=\"w-50\">\n" +
                            "\n" +
                            "                            <img id=\"img_dp_"+i+"\"  class=\"mx-auto d-block\" height=\"160px\" width=\"160px\">\n" +
                            "                                <h6 class=\"text-center\">Delayed Phase</h6>\n" +
                            "                            </div>\n" +
                            "                        </div>\n" +
                            "                    </div>\n" +
                            "                    <div id=\"div_features_"+i+"\" class=\"w-50 mx-0 p-2 border border-info h-75\">\n" +
                            "                        <h5>Predicted Tumor Type</h5>\n" +
                            "                    </div>\n" +
                            "                </div>\n" +
                            "            </div>\n" +
                            "        " +
                            "")

                    }

                }

            },error: function (err) {

            }
        });

        // for (var i in d){
        //     if (i==0)
        //     $("#list_slices_step_5").append("<a class='list-group-item list-group-item-action active w-100'" +
        //         " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
        //     else
        //     $("#list_slices_step_5").append("<a class='list-group-item list-group-item-action w-100'" +
        //         " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
        // }

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