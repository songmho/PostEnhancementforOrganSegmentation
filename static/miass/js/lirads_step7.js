(function () {

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
                $("#txt_tumor_type").text(d["tumor_type"]);
                $("#txt_tumor_aphe_type").text(d["AHPE_type"]);
                $("#txt_tumor_size").text(d["tumor_size"]);
                $("#txt_number_major_feature").text(d["number_m_f"]);
                write_log_in_console("Target tumor's LI-RADS features are loaded.");
            }, error: function () {

            }
        });

        $("#btn_generate_report").on("click", function(){

        });
        $("#btn_pred_hcc_stage").on("click", function(){
            $.ajax({
                url:"/api/predict_stage",
                async: true,
                method: "POST",
                data: {"data": JSON.stringify({})},
                data_type: "text",
                success: function (data) {
                    var stage = data["stage"];
                    $("#txt_lirad_stage").text(stage);
                    write_log_in_console("Stage of Tumor: "+stage);

                }, error: function () {

                }
            });

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