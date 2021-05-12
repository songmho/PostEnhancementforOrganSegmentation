(function () {
    $(document).ready(function(){
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