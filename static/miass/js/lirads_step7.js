(function () {

    $(document).ready(function(){

        write_log_in_console("Step 7. Predicting LR stage is started.");
        $("#btn_generate_report").on("click", function(){

        });
        $("#btn_pred_stage").on("click", function(){

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