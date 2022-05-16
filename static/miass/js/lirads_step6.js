(function () {

    var isPause = false;
    var idx= 0;
    var intervalSegment = null;
    var d;
    // var d = ["Tumor Group 1", "Tumor Group 2", "Tumor Group 3", "Tumor Group 4"];
    $(document).ready(function(){
        write_log_in_console("Step 3 is to remedy shape violation.");

        $.ajax({
            url: "/api/load_img_list_step6",
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
                var seqs = d["seqs"];
                console.log(seqs);

                $("#div_slice_step6").append("<div class=\"header \" style=\"width: 40px; vertical-align: middle; \"><h5 class='my-auto'>Slice ID</h5></div>");
                $("#div_seg_step6").append("<div class=\"header\" style=\"width: 40px;vertical-align: middle; \"><h5>Seg. Result</h5></div>");
                $("#div_seq_org_step6").append("<div class=\"header\" style=\"width: 40px; vertical-align: middle; \"><h5>Sequence ID</h5></div>");
                $("#div_enh_step6").append("<div class=\"header\" style=\"width: 40px; height:150px;vertical-align: middle;\"><h5>Rem. Result</h5></div>");
                $("#div_seq_enh_ste6").append("<div class=\"header\" style=\"width: 40px; vertical-align: middle;\"><h5>Sequence ID</h5></div>");
                for (var i in ids){
                    $("#div_slice_step6").append("<div class=\"title_seg\"><h4 class=\"h-100 mb-0\" style='width: 150px;'>"+ids[i]+"</h4></div>");
                }
                for (var i in sls){
                    $("#div_seg_step6").append("<div class=\"item\" id='step6_seg_"+ids[i]+"'>" +
                        "<img style='width: 150px; height: 150px;' src='data:image/png;base64,"+sls[i]+"'/>" +
                        "</div>");
                }
                for (var i in seqs){
                    $("#div_seq_org_step6").append("<div class=\"title_seg\"><h5 class=\"h-100 mb-0\" style='width: 150px;'>"+seqs[i]+"</h5></div>");
                }

            }, error: function (){

            }
        });

        $("#btn_detect_shape").on("click", function () {
            write_log_in_console("Detecting violation is started.");
            $.ajax({
                url: "/api/detect_shape_violation",
                async: false,
                method: 'POST',
                data: {"data": JSON.stringify()},
                data_type: "text",
                success: function (data) {
                    d = data["data"];
                    var diffs = d["diffs"];
                    console.log(diffs);
                    for (var i in diffs){
                        $("#step6_seg_"+diffs[i]).css("border", "4px solid #FF0000");
                    }
                    write_log_in_console("The number of violating slices is "+diffs.length+".");
                    write_log_in_console("Detecting violation is finished.");
                }, error: function (){
                    idx+=1;

                }
            });

        });
        $("#btn_remedy_shape").on("click", function () {
            write_log_in_console("Remedying violation is started.");
            $.ajax({
                url: "/api/remedy_shape_violation",
                async: false,
                method: 'POST',
                data: {"data": JSON.stringify({"target_img":idx})},
                data_type: "text",
                success: function (data) {
                    d = data["data"];
                    var seqs = d["seqs"];
                    var imgs = d["imgs"];
                    for (var i in imgs){
                        $("#div_enh_step6").append("<div class=\"item\">" +
                            "<img style='width: 150px; height: 150px;' src='data:image/png;base64,"+imgs[i]+"'/>" +
                            "</div>");
                    }
                    for (var i in seqs){
                        $("#div_seq_enh_step6").append("<div class=\"title_seg\"><h5 class=\"h-100 mb-0\" style='width: 150px;'>"+seqs[i]+"</h5></div>");
                    }

                    write_log_in_console("Remedying violation is finished.");

                }, error: function (){
                    idx+=1;

                }
            });
        });




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