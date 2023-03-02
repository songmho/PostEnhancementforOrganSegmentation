function sleep (delay) {
   var start = new Date().getTime();
   while (new Date().getTime() < start + delay);
}
(function () {

    var isPause = false;
    var idx= 0;
    var intervalSegment = null;
    var d;
    // var d =["plain_00000_0","plain_00001_0","plain_00002_0","plain_00003_0","arterial_00000_0","arterial_00001_0","arterial_00002_0","arterial_00003_0",
    // "venous_00000_0","venous_00001_0","venous_00002_0","venous_00003_0","delay_00000_0","delay_00001_0","delay_00002_0","delay_00003_0",];
    $(document).ready(function(){
        write_log_in_console("Step 4 is to remedy location violation.");
        // for (var i in d){
        //     console.log(i);
        //     if (i==0)
        //     $("#list_slices_step_4").append("<a class='list-group-item list-group-item-action active w-100'" +
        //         " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
        //     else
        //     $("#list_slices_step_4").append("<a class='list-group-item list-group-item-action w-100'" +
        //         " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"'>"+d[i]+"</a>");
        // }


        $.ajax({
            url: "/api/load_img_list_step4",
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

                $("#div_slice_step4").append("<div class=\"header \" style=\"width: 40px; vertical-align: middle; \"><h5 class='my-auto'>Slice ID</h5></div>");
                $("#div_seg_step4").append("<div class=\"header\" style=\"width: 40px;vertical-align: middle; \"><h5>Seg. Result</h5></div>");
                $("#div_seq_org_step4").append("<div class=\"header\" style=\"width: 40px; vertical-align: middle; \"><h5>Sequence ID</h5></div>");
                $("#div_enh_step4").append("<div class=\"header\" style=\"width: 40px; height:150px;vertical-align: middle;\"><h5>Rem. Result</h5></div>");
                $("#div_seq_enh_ste4").append("<div class=\"header\" style=\"width: 40px; vertical-align: middle;\"><h5>Sequence ID</h5></div>");
                for (var i in ids){
                    $("#div_slice_step4").append("<div class=\"title_seg\"><h4 class=\"h-100 mb-0\" style='width: 150px;'>"+ids[i]+"</h4></div>");
                }
                for (var i in sls){
                    $("#div_seg_step4").append("<div class=\"item\" id='step4_seg_"+ids[i]+"'>" +
                        "<img style='width: 150px; height: 150px;' src='data:image/png;base64,"+sls[i]+"'/>" +
                        "</div>");
                }
                for (var i in seqs){
                    $("#div_seq_org_step4").append("<div class=\"title_seg\"><h5 class=\"h-100 mb-0\" style='width: 150px;'>"+seqs[i]+"</h5></div>");
                }
            }, error: function (){

            }
        });

        $("#btn_detect_location").on("click", function () {
            write_log_in_console("Detecting violation is started.");
            $.ajax({
                url: "/api/detect_location_violation",
                async: false,
                method: 'POST',
                data: {"data": JSON.stringify()},
                data_type: "text",
                success: function (data) {
                    d = data["data"];
                    var diffs = d["diffs"];
                    console.log(diffs);
                    for (var i in diffs){
                        $("#step4_seg_"+diffs[i]).css("border", "4px solid #FF0000");
                    }
                    write_log_in_console("The number of violating slices is "+diffs.length+".");
                    write_log_in_console("Detecting violation is finished.");
                }, error: function (){
                    idx+=1;

                }
            });

        });
        $("#btn_remedy_location").on("click", function () {
            write_log_in_console("Remedying violation is started.");
            $.ajax({
                url: "/api/remedy_location_violation",
                async: false,
                method: 'POST',
                data: {"data": JSON.stringify({"target_img":idx})},
                data_type: "text",
                success: function (data) {
                    d = data["data"];
                    var seqs = d["seqs"];
                    var imgs = d["imgs"];
                    for (var i in imgs){
                        $("#div_enh_step4").append("<div class=\"item\">" +
                            "<img style='width: 150px; height: 150px;' src='data:image/png;base64,"+imgs[i]+"'/>" +
                            "</div>");
                    }
                    for (var i in seqs){
                        $("#div_seq_enh_ste4").append("<div class=\"title_seg\"><h5 class=\"h-100 mb-0\" style='width: 150px;'>"+seqs[i]+"</h5></div>");
                    }
                    write_log_in_console("Remedying violation is finished.");
                }, error: function (){
                    idx+=1;

                }
            });
        });


        $("#btn_step3_back").on("click", function () {
            $("#smartwizard").smartWizard("prev");
            $("#btn_step3").removeClass("done");
            $("#step-3").css("display", "none");
            $("#step-2").css("display", "block");

        });

        $("#btn_step3_next").on("click", function () {
            $("#step-4").empty();
            $("#step-3").css("display", "none");
            $("#step-4").css("display", "block");
            $.post("/view/lirads_step4/", null, function (result) {
                $("#step-4").append(result);
            });
            $("#btn_step3").removeClass("active").addClass("done");
            $("#btn_step4").addClass("active");
            $("#smartwizard").smartWizard("next");

        });
    });
})(jQuery);