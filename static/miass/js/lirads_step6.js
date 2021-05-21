(function () {

    var d = ["Tumor Group 1", "TUmor Group 2", "Tumor Group 3"];
    $(document).ready(function(){

        write_log_in_console("Step 6. Computing Li-RADS features is started.");
        for (var i in d){
            if (i==0)
            $("#list_slices_step_6").append("<a class='list-group-item list-group-item-action active w-100'" +
                " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
            else
            $("#list_slices_step_6").append("<a class='list-group-item list-group-item-action w-100'" +
                " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
        }

        $.ajax({
        url:"/api/load_tumor_group_list_step6",
        async: true,
        method: "POST",
        data: {"data": JSON.stringify({})},
        data_type: "text",
        success: function (data) {
            var d = data["data"];
            var img_list = data["imgs"];
            numImgs = d.lenght;

            for (var i in d) {
                slice = img_list[i];

                if (i == 0) {
                    $("#list_slices_step_6").append("<a class='list-group-item list-group-item-action active w-100'" +
                        " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
                    $("#sl_id_lirads_features").append("" +
                "            <div class=\"tab-pane show active\" id=\"list_"+i+"\" role=\"tabpanel\" aria-labelledby=\"...\">\n" +
                "                <div class=\"row mx-0\">\n" +
                "                    <h6>Type of APHE: </h6>\n" +
                "                    <h6 id=\"txt_aphe_type_"+i+"\"</h6>\n" +
                "                </div>\n" +
                "                <div class=\"row mx-0\">\n" +
                "                    <h6>Tumor Size: </h6>\n" +
                "                    <h6 id=\"txt_tumor_size_"+i+"\"></h6>\n" +
                "                </div>\n" +
                "                <div class=\"mx-0\">\n" +
                "                    <h6>Major Features </h6>\n" +
                "                    <div class=\"row mx-0 ml-2\">\n" +
                "                        <h6>Existence of Capsule: </h6>\n" +
                "                        <h6 id=\"txt_capsule_"+i+"\"></h6>\n" +
                "                    </div>\n" +
                "                    <div class=\"row mx-0 ml-2\">\n" +
                "                        <h6>Existence of Washout: </h6>\n" +
                "                        <h6 id=\"txt_washout_"+i+"\"></h6>\n" +
                "                    </div>\n" +
                "                    <div class=\"row mx-0 ml-2\">\n" +
                "                        <h6>Existence of Threshold Growth: </h6>\n" +
                "                        <h6 id=\"txt_th_growth_"+i+"\"></h6>\n" +
                "                    </div>\n" +
                "                </div>\n" +
                "            </div>" +
                "");

                } else {
                    $("#list_slices_step_6").append("<a class='list-group-item list-group-item-action w-100'" +
                        " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
                    $("#sl_id_lirads_features").append("" +
                "            <div class=\"tab-pane\" id=\"list_"+i+"\" role=\"tabpanel\" aria-labelledby=\"...\">\n" +
                "                <div class=\"row mx-0\">\n" +
                "                    <h6>Type of APHE: </h6>\n" +
                "                    <h6 id=\"txt_aphe_type_"+i+"\"</h6>\n" +
                "                </div>\n" +
                "                <div class=\"row mx-0\">\n" +
                "                    <h6>Tumor Size: </h6>\n" +
                "                    <h6 id=\"txt_tumor_size_"+i+"\"></h6>\n" +
                "                </div>\n" +
                "                <div class=\"mx-0\">\n" +
                "                    <h6>Major Features </h6>\n" +
                "                    <div class=\"row mx-0 ml-2\">\n" +
                "                        <h6>Existence of Capsule: </h6>\n" +
                "                        <h6 id=\"txt_capsule_"+i+"\"></h6>\n" +
                "                    </div>\n" +
                "                    <div class=\"row mx-0 ml-2\">\n" +
                "                        <h6>Existence of Washout: </h6>\n" +
                "                        <h6 id=\"txt_washout_"+i+"\"></h6>\n" +
                "                    </div>\n" +
                "                    <div class=\"row mx-0 ml-2\">\n" +
                "                        <h6>Existence of Threshold Growth: </h6>\n" +
                "                        <h6 id=\"txt_th_growth_"+i+"\"></h6>\n" +
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