(function () {

    var isPause = false;
    var idx= 0;
    var d;
    var intervalSegment = null;
    $(document).ready(function(){
        write_log_in_console("Step 4 is to remedy size violation.");
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
                $("#step4_max_sl").text(sl_org.length);
                $("#step4_cur_sl").text(1);
                max_sl_num = sl_org.length;
                $('input[type=range]').attr("max", max_sl_num);

                for (var i = 0; i<sl_org.length; i++){
                    console.log(i);
                    $("#div_slice_id_step4").append(
                        '<div class="mx-1" style="display: inline-block; width: 180px;">\n' +
                        '    <h5 class="text-center" id="step4_sl_title_"'+i+'>Slice #'+(i+1)+'</h5>\n' +
                        '</div>');
                    $("#div_slice_step4").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <img style="width: 180px; height: 180px;" class="border" id="step4_sl_'+i+'" src="data:image/png;base64,'+sl_org[i]+'">\n' +
                        '</div>');

                    $("#div_org_step4").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <img style="width: 180px; height: 180px;" class="border" id="step4_seg_'+i+'" src="data:image/png;base64,'+sl_seg[i]+'">\n' +
                        // '    <div class="mx-auto inline" style="text-align: center;"> <h5 style="display: inline">SEQ #</h5> <h5 style="display: inline">(88888)</h5> </div>' +
                        '</div>');

                    $("#div_enh_step4").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <img style="width: 180px; height: 180px;" class="border" id="step4_enh_'+i+'" src="data:image/png;base64,0">\n' +
                        // '    <div class="mx-auto inline" style="text-align: center;"> <h5 style="display: inline" id="seq_enh_step4_'+i+'">SEQ #</h5> <h5 style="display: inline" id="num_pix_enh_step4_'+i+'">(.)</h5> </div>' +
                        '</div>');
                }
            }, error: function (){

            }
        });


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
                $("#num_sl_org_step1_s4").text(step1["num_slices_organ"]);
                $("#num_seqs_step1_s4").text(step1["num_slices_organ"]);
                $("#size_step1_s4").text(String(step1["min_size"]) + " ↤ " + step1["avg_size"] + " ↦ " + step1["max_size"]);
                $("#num_sl_org_step2_s4").text(step2["num_slices_organ"]);
                $("#num_rem_sl_step2_s4").text(step2["num_remedied_slices"]);
                $("#size_step2_s4").text(String(step2["min_size"]) + " ↤ " + step2["avg_size"] + " ↦ " + step2["max_size"]);
                $("#num_sl_org_step3_s4").text(step3["num_slices_organ"]);
                $("#num_seqs_step3_s4").text(step3["num_slices_organ"]);
                $("#num_rem_sl_step3_s4").text(step3["num_remedied_slices"]);
                $("#size_step3_s4").text(String(step3["min_size"]) + " ↤ " + step3["avg_size"] + " ↦ " + step3["max_size"]);
            }, error: function () {

            }
        });

        $("#btn_detect_size").on("click", function () {
            write_log_in_console("Detecting violation is started.");
            $.ajax({
                url: "/api/detect_size_violation",
                async: false,
                method: 'POST',
                data: {"data": JSON.stringify()},
                data_type: "text",
                success: function (data) {
                    d = data["data"];
                    var diffs = d["diffs"];
                    console.log(diffs);
                    for (var i in diffs){
                        $("#step5_seg_"+diffs[i]).css("border", "4px solid #FF0000");
                    }
                    write_log_in_console("The number of violating slices is "+diffs.length+".");
                    write_log_in_console("Detecting violation is finished.");
                }, error: function (){
                    idx+=1;

                }
            });

        });
        $("#btn_task1_step4").on("click", function () {
            write_log_in_console("Remedying violation is started.");
            $.ajax({
                url: "/api/remedy_size_violation",
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
                        $("#step4_enh_"+i).attr("src", "data:image/png;base64,"+sl_enh[i]);
                    }
                    var summary = data["data"]["summary"];
                    $("#input_step4_num_enhanced").text(summary["enh_num"]);
                    $("#input_step4_num_seq_after").text(summary["num_seqs"]);
                    write_log_in_console("Remedying violation is finished.");

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
                            $("#num_sl_org_step1_s4").text(step1["num_slices_organ"]);
                            $("#num_seqs_step1_s4").text(step1["num_slices_organ"]);
                            $("#size_step1_s4").text(String(step1["min_size"]) + " ↤ " + step1["avg_size"] + " ↦ " + step1["max_size"]);
                            $("#num_sl_org_step2_s4").text(step2["num_slices_organ"]);
                            $("#num_seqs_step2_s4").text(step2["num_slices_organ"]);
                            $("#num_rem_sl_step2_s4").text(step2["num_remedied_slices"]);
                            $("#size_step2_s4").text(String(step2["min_size"]) + " ↤ " + step2["avg_size"] + " ↦ " + step2["max_size"]);
                            $("#num_sl_org_step3_s4").text(step3["num_slices_organ"]);
                            $("#num_seqs_step3_s4").text(step3["num_slices_organ"]);
                            $("#num_rem_sl_step3_s4").text(step3["num_remedied_slices"]);
                            $("#size_step3_s4").text(String(step3["min_size"]) + " ↤ " + step3["avg_size"] + " ↦ " + step3["max_size"]);
                            $("#num_sl_org_step4_s4").text(step4["num_slices_organ"]);
                            $("#num_seqs_step4_s4").text(step4["num_slices_organ"]);
                            $("#num_rem_sl_step4_s4").text(step4["num_remedied_slices"]);
                            $("#size_step4_s4").text(String(step4["min_size"]) + " ↤ " + step4["avg_size"] + " ↦ " + step4["max_size"]);
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
            $("#step4_cur_sl").text(value);
            var val_move = 180*Number.parseInt(value-1);

            $('#div_slice_id_step4').scrollLeft(val_move);
            $('#div_slice_step4').scrollLeft(val_move);
            $('#div_org_step4').scrollLeft(val_move);
            $('#div_enh_step4').scrollLeft(val_move);
        });

        $("#btn_step4_back").on("click", function () {
            $("#smartwizard").smartWizard("prev");
            $("#btn_step4").removeClass("done");
            $("#step-4").css("display", "none");
            $("#step-3").css("display", "block");

        });

        $("#btn_step4_next").on("click", function () {
            $("#step-5").empty();
            $("#step-4").css("display", "none");
            $("#step-4").css("display", "block");
            $.post("/view/lirads_step5/", null, function (result) {
                $("#step-5").append(result);
            });
            $("#btn_step4").removeClass("active").addClass("done");
            $("#btn_step5").addClass("active");
            $("#smartwizard").smartWizard("next");
        });
    });
})(jQuery);