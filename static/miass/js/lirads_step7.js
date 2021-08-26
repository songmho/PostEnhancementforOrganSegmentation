(function () {
    var idx = 0;
    var interval = null;
    var max_num_tumor = 0;
    $(document).ready(function(){

        write_log_in_console("Step 7. Predicting LR stage is started.");
        write_log_in_console("The tumor stage classification model is being prepared.");

        $.ajax({
            url:"/api/get_tumor_info",
            async: false,
            method: "POST",
            data: {"data": JSON.stringify({})},
            data_type: "text",
            success: function (data) {
                var d = data["data"];
                console.log(d);
                max_num_tumor = Object.keys(d).length;
                var tumor_type = "";
                var aphe_type = "";
                var tumor_size = "";
                var num_m_f = "";
                var count = 0;
                for (var i in d){
                    tumor_type += d[i]["tumor_type"];
                    aphe_type += d[i]["APHE_Type"];
                    tumor_size += d[i]["tumor_size"];
                    num_m_f += d[i]["number_m_f"];
                    if (count < max_num_tumor-1){
                        tumor_size += ", "
                        tumor_type += ", "
                        aphe_type += ", "
                        num_m_f += ", "
                    }
                    count++;
                }
                $("#txt_tumor_type").text(tumor_type);
                $("#txt_tumor_aphe_type").text(aphe_type);
                $("#txt_tumor_size").text(tumor_size);
                $("#txt_number_major_feature").text(num_m_f);
                write_log_in_console("Target tumor's LI-RADS features are loaded.");
            }, error: function () {

            }
        });

        $("#btn_generate_report").on("click", function(){

        });
        var total_stages = "";
        $("#btn_pred_hcc_stage").on("click", function(){
            interval = setInterval(function () {
                $.ajax({
                    url:"/api/predict_stage",
                    async: true,
                    method: "POST",
                    data: {"data": JSON.stringify({"tumor_id":idx})},
                    data_type: "text",
                    success: function (data) {
                        var stage = data["stage"];
                        if (!stage.include("LR"))
                            stage = "LR-"+stage
                        total_stages += stage
                        idx +=1;
                        write_log_in_console("Stage of Tumor: "+stage);
                        if (idx >= max_num_tumor){
                            clearInterval(interval);
                            $("#txt_lirad_stage").text(stage);
                        }else
                            total_stages+=", "

                    }, error: function () {
                    clearInterval(interval);
                    }
                });
            }, 500);
        });

        $("#btn_lirads_step7_back").on("click", function () {
            $("#smartwizard").smartWizard("prev");
            $("#btn_step7").removeClass("done");
            $("#step-7").css("display", "none");
            $("#step-6").css("display", "block");

        });

        $("#btn_lirads_step7_done").on("click", function () {
            // $("#step-7").empty();
            // $("#step-6").css("display", "none");
            // $("#step-7").css("display", "block");
            // $.post("/view/lirads_step7/", null, function (result) {
            //     $("#step-7").append(result);
            // });
            // $("#btn_step6").removeClass("active").addClass("done");
            // $("#btn_step7").addClass("active");
            // $("#smartwizard").smartWizard("next");

        });
    });
})(jQuery);