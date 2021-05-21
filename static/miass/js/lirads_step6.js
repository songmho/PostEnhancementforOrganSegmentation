(function () {

    var d = ["Tumor Group 1", "TUmor Group 2", "Tumor Group 3"];
    $(document).ready(function(){

        for (var i in d){
            if (i==0)
            $("#list_slices_step_6").append("<a class='list-group-item list-group-item-action active w-100'" +
                " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
            else
            $("#list_slices_step_6").append("<a class='list-group-item list-group-item-action w-100'" +
                " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
        }
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