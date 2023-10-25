(function () {

    var isPause = false;
    var idx= 0;
    var intervalSegment = null;
    var d;
    // var d = ["Tumor Group 1", "Tumor Group 2", "Tumor Group 3", "Tumor Group 4"];
    $(document).ready(function(){
        write_log_in_console("Step 5 is to remedy shape violation.");
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
                $("#step5_max_sl").text(sl_org.length);
                $("#step5_cur_sl").text(1);
                max_sl_num = sl_org.length;
                $('input[type=range]').attr("max", max_sl_num);

                for (var i = 0; i<sl_org.length; i++){
                    $("#div_slice_id_step5").append(
                        '<div class="mx-1" style="display: inline-block; width: 180px;">\n' +
                        '    <h5 class="text-center" id="step5_sl_title_"'+i+'>Slice #'+(i+1)+'</h5>\n' +
                        '</div>');
                    $("#div_slice_step5").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <img style="width: 180px; height: 180px;" class="border" id="step5_sl_'+i+'" src="data:image/png;base64,'+sl_org[i]+'">\n' +
                        '</div>');

                    $("#div_org_step5").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <img style="width: 180px; height: 180px;" class="border" id="step5_seg_'+i+'" src="data:image/png;base64,'+sl_seg[i]+'">\n' +
                        // '    <div class="mx-auto inline" style="text-align: center;"> <h5 style="display: inline">SEQ #</h5> <h5 style="display: inline">(88888)</h5> </div>' +
                        '</div>');

                    $("#div_enh_step5").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <img style="width: 180px; height: 180px;" class="border" id="step5_enh_'+i+'" src="data:image/png;base64,0">\n' +
                        // '    <div class="mx-auto inline" style="text-align: center;"> <h5 style="display: inline" id="seq_enh_step5_'+i+'">SEQ #</h5> <h5 style="display: inline" id="num_pix_enh_step5_'+i+'">(.)</h5> </div>' +
                        '</div>');
                }
            }, error: function (){

            }
        });

        $.ajax({
            url: "/api/get_summary",
            async: true,
            method: 'POST',
            data: {"data": JSON.stringify({"step": 4})},
            data_type: "text",
            success: function (data) {
                // var data = JSON.parse(data);
                d = data["data"];
                var step1 = d["step1"];
                var step2 = d["step2"];
                var step3 = d["step3"];
                var step4 = d["step4"];
                console.log(d);
                $("#num_sl_org_step1_s5").text(step1["num_slices_organ"]);
                $("#num_seqs_step1_s5").text("-");
                $("#size_step1_s5").text("-");
                $("#num_sl_org_step2_s5").text(step1["num_slices_organ"]);
                $("#num_seqs_step2_s5").text(step2["num_seqs"]);
                $("#num_rem_sl_step2_s5").text("-");
                $("#size_step2_s5").text(String(step2["min_size"]) + " ↤ " + step2["avg_size"] + " ↦ " + step2["max_size"]);
                $("#num_sl_org_step3_s5").text(step3["num_slices_organ"]);
                $("#num_seqs_step3_s5").text(step3["num_seqs"]);
                $("#num_rem_sl_step3_s5").text(step3["num_remedied_slices"]);
                $("#size_step3_s5").text(String(step3["min_size"]) + " ↤ " + step3["avg_size"] + " ↦ " + step3["max_size"]);
                $("#num_sl_org_step4_s5").text(step4["num_slices_organ"]);
                $("#num_seqs_step4_s5").text(step4["num_seqs"]);
                $("#num_rem_sl_step4_s5").text(step4["num_remedied_slices"]);
                $("#size_step4_s5").text(String(step4["min_size"]) + " ↤ " + step4["avg_size"] + " ↦ " + step4["max_size"]);
            }, error: function () {

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
        $("#btn_task1_step5").on("click", function () {
            write_log_in_console("Remedying violation is started.");
            $.ajax({
                url: "/api/remedy_shape_violation",
                async: false,
                method: 'POST',
                data: {"data": JSON.stringify({"target_img":idx})},
                data_type: "text",
                success: function (data) {
                    console.log(data);
                    var sl_enh = data["data"]["sl_enh"];
                    console.log(sl_enh.length);
                    for (var i = 0; i<sl_enh.length; i++){
                        console.log(sl_enh[i]);
                        $("#step5_enh_"+i).attr("src", "data:image/png;base64,"+sl_enh[i]);
                    }
                    var summary = data["data"]["summary"];
                    $("#input_step5_num_enhanced").text(summary["enh_num"]);
                    $("#input_step5_num_seq_after").text(summary["num_seqs"]);
                    write_log_in_console("Remedying violation is finished.");
                    $.ajax({
                        url: "/api/get_summary",
                        async: true,
                        method: 'POST',
                        data: {"data": JSON.stringify({"step": 5})},
                        data_type: "text",
                        success: function (data) {
                            // var data = JSON.parse(data);
                            d = data["data"];
                            var step1 = d["step1"];
                            var step2 = d["step2"];
                            var step3 = d["step3"];
                            var step4 = d["step4"];
                            var step5 = d["step5"];
                            console.log(d);
                            $("#num_sl_org_step1_s5").text(step1["num_slices_organ"]);
                            $("#num_seqs_step1_s5").text("-");
                            $("#size_step1_s5").text("-");
                            $("#num_sl_org_step2_s5").text(step1["num_slices_organ"]);
                            $("#num_seqs_step2_s5").text(step2["num_seqs"]);
                            $("#num_rem_sl_step2_s5").text("-");
                            $("#size_step2_s5").text(String(step2["min_size"]) + " ↤ " + step2["avg_size"] + " ↦ " + step2["max_size"]);
                            $("#num_sl_org_step3_s5").text(step3["num_slices_organ"]);
                            $("#num_seqs_step3_s5").text(step3["num_seqs"]);
                            $("#num_rem_sl_step3_s5").text(step3["num_remedied_slices"]);
                            $("#size_step3_s5").text(String(step3["min_size"]) + " ↤ " + step3["avg_size"] + " ↦ " + step3["max_size"]);
                            $("#num_sl_org_step4_s5").text(step4["num_slices_organ"]);
                            $("#num_seqs_step4_s5").text(step4["num_seqs"]);
                            $("#num_rem_sl_step4_s5").text(step4["num_remedied_slices"]);
                            $("#size_step4_s5").text(String(step4["min_size"]) + " ↤ " + step4["avg_size"] + " ↦ " + step4["max_size"]);
                            $("#num_sl_org_step5_s5").text(step5["num_slices_organ"]);
                            $("#num_seqs_step5_s5").text(step5["num_seqs"]);
                            $("#num_rem_sl_step5_s5").text(step5["num_remedied_slices"]);
                            $("#size_step5_s5").text(String(step5["min_size"]) + " ↤ " + step5["avg_size"] + " ↦ " + step5["max_size"]);
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
            $("#step5_cur_sl").text(value);
            var val_move = 180*Number.parseInt(value-1);

            $('#div_slice_id_step5').scrollLeft(val_move);
            $('#div_slice_step5').scrollLeft(val_move);
            $('#div_org_step5').scrollLeft(val_move);
            $('#div_enh_step5').scrollLeft(val_move);
        });


        $("#btn_step5_back").on("click", function () {
            $("#smartwizard").smartWizard("prev");
            $("#btn_step5").removeClass("done");
            $("#step-5").css("display", "none");
            $("#step-4").css("display", "block");

        });

        $("#btn_step5_next").on("click", function () {
            $("#step-6").empty();
            $("#step-5").css("display", "none");
            $("#step-5").css("display", "block");
            $.post("/view/lirads_step6/", null, function (result) {
                $("#step-6").append(result);
            });
            $("#btn_step5").removeClass("active").addClass("done");
            $("#btn_step6").addClass("active");
            $("#smartwizard").smartWizard("next");
        });
    });
})(jQuery);