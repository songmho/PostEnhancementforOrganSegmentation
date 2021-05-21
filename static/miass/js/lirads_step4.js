(function () {
    var d =["plain_2_0","plain_3_0","plain_4_0","arterial_2_0","arterial_3_0","arterial_4_0","venous_2_0","venous_3_0","venous_4_0","delayed_2_0","delayed_3_0","delayed_4_0"];
    $(document).ready(function(){

        for (var i in d){
            if (i==0)
            $("#list_slices_step_4").append("<a class='list-group-item list-group-item-action active w-100'" +
                " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
            else
            $("#list_slices_step_4").append("<a class='list-group-item list-group-item-action w-100'" +
                " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
        }

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