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
        write_log_in_console("Step 3 is to remedy location violation.");

        $.ajax({
            url: "/api/load_img_list_with_seqs",
            async: true,
            method: 'POST',
            data: {"data": JSON.stringify({})},
            data_type: "text",
            success: function (data) {
                // var data = JSON.parse(data);
                d = data["data"];
                var sl_org = d["sl_org"];
                var sl_seg = d["sl_seg"];
                $("#step3_max_sl").text(sl_org.length);
                $("#step3_cur_sl").text(1);
                max_sl_num = sl_org.length;
                $('input[type=range]').attr("max", max_sl_num);

                for (var i = 0; i<sl_org.length; i++){
                    console.log(i);
                    $("#div_slice_id_step3").append(
                        '<div class="mx-1" style="display: inline-block; width: 180px;">\n' +
                        '    <h5 class="text-center" id="step3_sl_title_"'+i+'>Slice #'+(i+1)+'</h5>\n' +
                        '</div>');
                    $("#div_slice_step3").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <img style="width: 180px; height: 180px;" class="border" id="step3_sl_'+i+'" src="data:image/png;base64,'+sl_org[i]+'">\n' +
                        '</div>');

                    $("#div_org_step3").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <img style="width: 180px; height: 180px;" class="border" id="step3_seg_'+i+'" src="data:image/png;base64,'+sl_seg[i]+'">\n' +
                        // '    <div class="mx-auto inline" style="text-align: center;"> <h5 style="display: inline">SEQ #</h5> <h5 style="display: inline">(88888)</h5> </div>' +
                        '</div>');

                    $("#div_enh_step3").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <img style="width: 180px; height: 180px;" class="border" id="step3_enh_'+i+'" src="data:image/png;base64,0">\n' +
                        // '    <div class="mx-auto inline" style="text-align: center;"> <h5 style="display: inline" id="seq_enh_step3_'+i+'">SEQ #</h5> <h5 style="display: inline" id="num_pix_enh_step3_'+i+'">(.)</h5> </div>' +
                        '</div>');
                }
            }, error: function (){

            }
        });

        $.ajax({
            url: "/api/get_summary",
            async: true,
            method: 'POST',
            data: {"data": JSON.stringify({"step": 2})},
            data_type: "text",
            success: function (data) {
                // var data = JSON.parse(data);
                d = data["data"];
                var step1 = d["step1"];
                var step2 = d["step2"];
                console.log(d);
                $("#num_sl_org_step1_s3").text(step1["num_slices_organ"]);
                $("#num_seqs_step1_s3").text("-");
                $("#size_step1_s3").text("-");
                $("#num_sl_org_step2_s3").text(step1["num_slices_organ"]);
                $("#num_seqs_step2_s3").text(step2["num_seqs"]);
                $("#num_rem_sl_step2_s3").text("-");
                $("#size_step2_s3").text(String(step2["min_size"]) + " ↤ " + step2["avg_size"] + " ↦ " + step2["max_size"]);
            }, error: function () {

            }
        });

        $("#btn_task1_step3").on("click", function () {
            write_log_in_console("Remedying violation is started.");
            $.ajax({
                url: "/api/remedy_location_violation",
                async: false,
                method: 'POST',
                data: {"data": JSON.stringify()},
                data_type: "text",
                success: function (data) {
                    console.log(data);
                    var sl_enh = data["data"]["sl_enh"];
                    console.log(sl_enh.length);
                    for (var i = 0; i<sl_enh.length; i++){
                        console.log(sl_enh[i]);
                        $("#step3_enh_"+i).attr("src", "data:image/png;base64,"+sl_enh[i]);
                    }
                    var summary = data["data"]["summary"];
                    $("#input_step3_num_enhanced").text(summary["enh_num"]);
                    $("#input_step3_num_seq_after").text(summary["num_seqs"]);
                    write_log_in_console("Remedying violation is finished.");

                    $.ajax({
                        url: "/api/get_summary",
                        async: true,
                        method: 'POST',
                        data: {"data": JSON.stringify({"step": 3})},
                        data_type: "text",
                        success: function (data) {
                            // var data = JSON.parse(data);
                            d = data["data"];
                            var step1 = d["step1"];
                            var step2 = d["step2"];
                            var step3 = d["step3"];
                            console.log(d);
                            $("#num_sl_org_step1_s3").text(step1["num_slices_organ"]);
                            $("#num_seqs_step1_s3").text("-");
                            $("#size_step1_s3").text("-");
                            $("#num_sl_org_step2_s3").text(step1["num_slices_organ"]);
                            $("#num_rem_sl_step2_s3").text("-");
                            $("#num_seqs_step2_s3").text(step2["num_seqs"]);
                            $("#size_step2_s3").text(String(step2["min_size"]) + " ↤ " + step2["avg_size"] + " ↦ " + step2["max_size"]);
                            $("#num_sl_org_step3_s3").text(step3["num_slices_organ"]);
                            $("#num_rem_sl_step3_s3").text(step3["num_remedied_slices"]);
                            $("#num_seqs_step3_s3").text(step3["num_seqs"]);
                            $("#size_step3_s3").text(String(step3["min_size"]) + " ↤ " + step3["avg_size"] + " ↦ " + step3["max_size"]);
                        }, error: function () {

                        }
                    });
                }, error: function (){
                    idx+=1;

                }
            });
        });


        $('input[type=range]').on('change input', function() {
            var value = $(this).val();
            $("#step3_cur_sl").text(value);
            var val_move = 180*Number.parseInt(value-1);

            $('#div_slice_id_step3').scrollLeft(val_move);
            $('#div_slice_step3').scrollLeft(val_move);
            $('#div_org_step3').scrollLeft(val_move);
            $('#div_enh_step3').scrollLeft(val_move);
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