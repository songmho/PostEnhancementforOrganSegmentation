(function () {
    var isPause = false;
    var isPause_pp = false;
    var idx= 0;
    var intervalSegment = null;
    var d;
    var is_segment_finished = false;
    var pp_step = 0;
    var intervalPP = null;
    var phase_info = null;

    $(document).ready(function(){
        write_log_in_console("Step 2 is to identify continuity sequences.");
        $.ajax({
            url: "/api/load_img_list_step2",
            async: true,
            method: 'POST',
            data: {"data": JSON.stringify({})},
            data_type: "text",
            success: function (data) {
                // var data = JSON.parse(data);
                d = data["data"];
                var ids = d["ids"];
                var sls = d["sls"];
                var segs = d["segs"];
                $("#div_slice").append("<div class=\"header \" style=\"width: 40px; vertical-align: middle; \"><h5 class='my-auto'>Slice ID</h5></div>");
                $("#div_org").append("<div class=\"header\" style=\"width: 40px;vertical-align: middle; \"><h5>Slice</h5></div>");
                $("#div_seg").append("<div class=\"header\" style=\"width: 40px; vertical-align: middle; \"><h5>Seg. Result</h5></div>");
                $("#div_seg1").append("<div class=\"header\" style=\"width: 40px; vertical-align: middle;\"><h5>Sequence ID</h5></div>");
                for (var i in ids){
                    $("#div_slice").append("<div class=\"title_seg\"><h5 class=\"h-100 mb-0\" style='width: 150px;'>"+ids[i]+"</h5></div>");
                }
                for (var i in sls){
                    $("#div_org").append("<div class=\"item\">" +
                        "<img style='width: 150px; height: 150px;' src='data:image/png;base64,"+sls[i]+"'/>" +
                        "</div>");
                }
                for (var i in segs){
                    $("#div_seg").append("<div class=\"item\">" +
                        "<img style='width: 150px; height: 150px;' src='data:image/png;base64,"+segs[i]+"'/>" +
                        "</div>");
                }
            }, error: function (){

            }
        });

        $("#btn_segment_liver").on("click", function () {
            write_log_in_console("Identifying continuity sequences is started.");
            $.ajax({
                url: "/api/identify_continuity_sequence",
                async: false,
                method: 'POST',
                data: {"data": JSON.stringify({"target_img":idx})},
                data_type: "text",
                success: function (data) {
                    d = data["data"];
                    var seqs = d["seqs"];
                    for (var i in seqs){
                        $("#div_seg1").append("<div class=\"title_seg\"><h5 class=\"h-100 mb-0\" style='width: 150px;'>"+seqs[i]+"</h5></div>");
                    }

                write_log_in_console("The number of continuity sequences is "+d["num_seq"]+".");
                write_log_in_console("Identifying continuity sequences is finished.");
                }, error: function (){
                    idx+=1;
                    console.log("EERRORR");
                }
            });
        });


        $("#btn_lirads_step2_back").on("click", function () {
            $.ajax({
                url: "/api/initialize_diagnosis_env",
                async: true,
                method: 'POST',
                data_type: "text",
                success: function (data) {
                    console.log("INITIALIZED");
                }, error: function (){
                }
            });
            $("#smartwizard").smartWizard("prev");
            $("#btn_step2").removeClass("done");
            $("#step-2").css("display", "none");
            $("#step-1").css("display", "block");

        });

        $("#btn_lirads_step2_next").on("click", function () {
            $("#step-3").empty();
            $("#step-2").css("display", "none");
            $("#step-3").css("display", "block");
            $.post("/view/lirads_step3/", null, function (result) {
                $("#step-3").append(result);
            });
            $("#btn_step2").removeClass("active").addClass("done");
            $("#btn_step3").addClass("active");
            $("#smartwizard").smartWizard("next");

        });
    });
})(jQuery);