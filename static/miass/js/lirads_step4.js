(function () {
    $(document).ready(function(){
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