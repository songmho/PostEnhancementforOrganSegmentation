(function () {
    var idx = 0;
    var interval = null;
    var max_num_tumor = 0;
    $(document).ready(function(){
        write_log_in_console("Step 7 is to remedy HU Scale violation.");
        $.ajax({
            url: "/api/load_img_list_step7",
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

                $("#div_slice_step7").append("<div class=\"header \" style=\"width: 40px; vertical-align: middle; \"><h5 class='my-auto'>Slice ID</h5></div>");
                $("#div_seg_step7").append("<div class=\"header\" style=\"width: 40px;vertical-align: middle; \"><h5>Seg. Result</h5></div>");
                $("#div_seq_org_step7").append("<div class=\"header\" style=\"width: 40px; vertical-align: middle; \"><h5>Sequence ID</h5></div>");
                $("#div_enh_step7").append("<div class=\"header\" style=\"width: 40px; height:150px;vertical-align: middle;\"><h5>Rem. Result</h5></div>");
                $("#div_seq_enh_ste7").append("<div class=\"header\" style=\"width: 40px; vertical-align: middle;\"><h5>Sequence ID</h5></div>");
                for (var i in ids){
                    $("#div_slice_step7").append("<div class=\"title_seg\"><h4 class=\"h-100 mb-0\" style='width: 150px;'>"+ids[i]+"</h4></div>");
                }
                for (var i in sls){
                    $("#div_seg_step7").append("<div class=\"item\" id='step7_seg_"+ids[i]+"'>" +
                        "<img style='width: 150px; height: 150px;' src='data:image/png;base64,"+sls[i]+"'/>" +
                        "</div>");
                }
                for (var i in seqs){
                    $("#div_seq_org_step7").append("<div class=\"title_seg\"><h5 class=\"h-100 mb-0\" style='width: 150px;'>"+seqs[i]+"</h5></div>");
                }
            }, error: function (){

            }
        });

        $("#btn_detect_hu").on("click", function () {
            write_log_in_console("Detecting violation is started.");
            $.ajax({
                url: "/api/detect_hu_violation",
                async: false,
                method: 'POST',
                data: {"data": JSON.stringify()},
                data_type: "text",
                success: function (data) {
                    d = data["data"];
                    var diffs = d["diffs"];
                    console.log(diffs);
                    for (var i in diffs){
                        $("#step3_seg_"+diffs[i]).css("border", "4px solid #FF0000");
                    }
                    write_log_in_console("The number of violating slices is "+diffs.length+".");
                    write_log_in_console("Detecting violation is finished.");
                }, error: function (){
                    idx+=1;

                }
            });
        });

        $("#btn_remedy_hu").on("click", function () {
            write_log_in_console("Remedying violation is started.");
            $.ajax({
                url: "/api/remedy_hu_violation",
                async: false,
                method: 'POST',
                data: {"data": JSON.stringify({"target_img":idx})},
                data_type: "text",
                success: function (data) {
                    d = data["data"];
                    var seqs = d["seqs"];
                    var imgs = d["imgs"];
                    for (var i in imgs){
                        $("#div_enh_step7").append("<div class=\"item\">" +
                            "<img style='width: 150px; height: 150px;' src='data:image/png;base64,"+imgs[i]+"'/>" +
                            "</div>");
                    }
                    for (var i in seqs){
                        $("#div_seq_enh_ste7").append("<div class=\"title_seg\"><h5 class=\"h-100 mb-0\" style='width: 150px;'>"+seqs[i]+"</h5></div>");
                    }
                    write_log_in_console("Remedying violation is finished.");
                }, error: function (){
                    idx+=1;

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

            $.ajax({
                url:"/api/register_diagnosis_liver",
                async: true,
                method: "POST",
                data: {"data": JSON.stringify({"tumor_types":$("#txt_tumor_type").text(), "aphe_types":$("#txt_tumor_aphe_type").text(),
                         "tumor_sizes":$("#txt_tumor_size").text(), "num_mfs":$("#txt_number_major_feature").text(),
                        "stages":$("#txt_lirad_stage").text()})},
                data_type: "text",
                success: function (data) {

                }, error: function () {
                clearInterval(interval);
                }
            });

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