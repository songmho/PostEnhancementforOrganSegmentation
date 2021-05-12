(function () {
    $(document).ready(function(){
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