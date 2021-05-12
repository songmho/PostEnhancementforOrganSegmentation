(function () {


    $(document).ready(function () {
        $("#smartwizard").smartWizard({selected:0, darkMode: false, theme:"arrows", autoAdjustHeight: false, toolbarSettings: {showNextButton: false,showPreviousButton: false }});
    });
    $.post("/view/lirads_step1/",null, function (result) {
        $("#step-1").append(result);
    });
    $("#step1_box").on("click", function () {
        $("#btn_step2").removeClass("done");
        $("#btn_step3").removeClass("done");
        $("#btn_step4").removeClass("done");
        $("#btn_step5").removeClass("done");
        $("#btn_step6").removeClass("done");
        $("#btn_step7").removeClass("done");
    });
    $("#step2_box").on("click", function () {
        $("#btn_step3").removeClass("done");
        $("#btn_step4").removeClass("done");
        $("#btn_step5").removeClass("done");
        $("#btn_step6").removeClass("done");
        $("#btn_step7").removeClass("done");
    });
    $("#step3_box").on("click", function () {
        $("#btn_step4").removeClass("done");
        $("#btn_step5").removeClass("done");
        $("#btn_step6").removeClass("done");
        $("#btn_step7").removeClass("done");
    });
    $("#step4_box").on("click", function () {
        $("#btn_step5").removeClass("done");
        $("#btn_step6").removeClass("done");
        $("#btn_step7").removeClass("done");
    });
    $("#step5_box").on("click", function () {
        $("#btn_step6").removeClass("done");
        $("#btn_step7").removeClass("done");
    });
    $("#step6_box").on("click", function () {
        $("#btn_step7").removeClass("done");
    });
    $("#step7_box").on("click", function () {
    });
})(jQuery);