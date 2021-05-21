(function () {
    var d =["plain_2_0","plain_3_0","plain_4_0","arterial_2_0","arterial_3_0","arterial_4_0","venous_2_0","venous_3_0","venous_4_0","delayed_2_0","delayed_3_0","delayed_4_0"];
    $(document).ready(function(){
        write_log_in_console("Step 4. Evaluating image features of tumors is started.");
        // for (var i in d){
        //     if (i==0)
        //     $("#list_slices_step_4").append("<a class='list-group-item list-group-item-action active w-100'" +
        //         " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
        //     else
        //     $("#list_slices_step_4").append("<a class='list-group-item list-group-item-action w-100'" +
        //         " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
        // }
        $.ajax({
            url:"/api/load_tumor_list",
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
                        $("#list_slices_step_4").append("<a class='list-group-item list-group-item-action active w-100'" +
                            " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
                        $("#sl_id_tumors").append("<div class=\"h-100  ml-2 mt-4 tab-pane show active\" id=\"list_"+i+"\" role=\"tabpanel\" aria-labelledby=\"list_"+i+"_list_tumors_step4\">\n" +
                            "                <div class=\"row h-100\">\n" +
                            "                    <div id=\"div_img\" class=\"w-50 mr-0\">\n" +
                            "                        <div class=\"div_area text-center h-100\">\n" +
                            "                          <img src=\"{% static \"/miass/images/tumors/HCC_2_AP 1_0.jpg\"%}\" width=\"250px\" height=\"250px\">\n" +
                            "                        </div>\n" +
                            "                    </div>\n" +
                            "                    <div id=\"div_features\" class=\"w-50 border border-info p-2\">\n" +
                            "                      <h5>Predicted Image Features</h5>\n" +
                            "                        <div id=\"div_img_features\" class=\"ml-2\">\n" +
                            "                          <h6>Hypoattenuating</h6>\n" +
                            "                        </div>\n" +
                            "                    </div>\n" +
                            "                </div>\n" +
                            "            </div>");

                    }else{
                        $("#list_slices_step_4").append("<a class='list-group-item list-group-item-action w-100'" +
                            " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");

                        $("#sl_id_tumors").append("<div class=\"h-100  ml-2 mt-4 tab-pane\" id=\"list_"+i+"\" role=\"tabpanel\" aria-labelledby=\"list_"+i+"_list_tumors_step4\">\n" +
                            "                <div class=\"row h-100\">\n" +
                            "                    <div id=\"div_img\" class=\"w-50 mr-0\">\n" +
                            "                        <div class=\"div_area text-center h-100\">\n" +
                            "                          <img src=\"{% static \"/miass/images/tumors/HCC_2_AP 1_0.jpg\"%}\" width=\"250px\" height=\"250px\">\n" +
                            "                        </div>\n" +
                            "                    </div>\n" +
                            "                    <div id=\"div_features\" class=\"w-50 border border-info p-2\">\n" +
                            "                      <h5>Predicted Image Features</h5>\n" +
                            "                        <div id=\"div_img_features\" class=\"ml-2\">\n" +
                            "                          <h6>Hypoattenuating</h6>\n" +
                            "                        </div>\n" +
                            "                    </div>\n" +
                            "                </div>\n" +
                            "            </div>");
                    }

                }

            },error: function (err) {

            }
        });

        $("#btn_btn_evaluate_tumor").on("click", function () {
            
        });


        $("#btn_lirads_step4_back").on("click", function () {
            $("#smartwizard").smartWizard("prev");
            $("#btn_step4").removeClass("done");
            $("#step-4").css("display", "none");
            $("#step-3").css("display", "block");

        });

        $("#btn_lirads_step4_next").on("click", function () {
            $("#step-5").empty();
            $("#step-4").css("display", "none");
            $("#step-5").css("display", "block");
            $.post("/view/lirads_step5/", null, function (result) {
                $("#step-5").append(result);
            });
            $("#btn_step4").removeClass("active").addClass("done");
            $("#btn_step5").addClass("active");
            $("#smartwizard").smartWizard("next");

        });
    });
})(jQuery);