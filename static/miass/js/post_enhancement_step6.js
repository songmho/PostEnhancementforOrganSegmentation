(function () {
    var idx = 0;
    var interval = null;
    var max_num_tumor = 0;
    $(document).ready(function(){
        write_log_in_console("Step 6 is to remedy HU Scale violation.");
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
                $("#step6_max_sl").text(sl_org.length);
                $("#step6_cur_sl").text(1);
                max_sl_num = sl_org.length;
                $('input[type=range]').attr("max", max_sl_num);

                for (var i = 0; i<sl_org.length; i++){
                    $("#div_slice_id_step6").append(
                        '<div class="mx-1" style="display: inline-block; width: 180px;">\n' +
                        '    <h5 class="text-center" id="step6_sl_title_"'+i+'>Slice #'+(i+1)+'</h5>\n' +
                        '</div>');
                    $("#div_slice_step6").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <img style="width: 180px; height: 180px;" class="border" id="step6_sl_'+i+'" src="data:image/png;base64,'+sl_org[i]+'">\n' +
                        '</div>');

                    $("#div_org_step6").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <img style="width: 180px; height: 180px;" class="border" id="step6_seg_'+i+'" src="data:image/png;base64,'+sl_seg[i]+'">\n' +
                        // '    <div class="mx-auto inline" style="text-align: center;"> <h5 style="display: inline">SEQ #</h5> <h5 style="display: inline">(88888)</h5> </div>' +
                        '</div>');

                    $("#div_enh_step6").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <img style="width: 180px; height: 180px;" class="border" id="step6_enh_'+i+'" src="data:image/png;base64,0">\n' +
                        // '    <div class="mx-auto inline" style="text-align: center;"> <h5 style="display: inline" id="seq_enh_step6_'+i+'">SEQ #</h5> <h5 style="display: inline" id="num_pix_enh_step6_'+i+'">(.)</h5> </div>' +
                        '</div>');
                }
            }, error: function (){

            }
        });

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
                $("#num_sl_org_step1_s6").text(step1["num_slices_organ"]);
                $("#num_seqs_step1_s6").text(step1["num_seqs"]);
                $("#size_step1_s6").text(String(step1["min_size"]) + " ↤ " + step1["avg_size"] + " ↦ " + step1["max_size"]);
                $("#num_sl_org_step2_s6").text(step2["num_slices_organ"]);
                $("#num_seqs_step2_s6").text(step2["num_seqs"]);
                $("#num_rem_sl_step2_s6").text(step2["num_remedied_slices"]);
                $("#size_step2_s6").text(String(step2["min_size"]) + " ↤ " + step2["avg_size"] + " ↦ " + step2["max_size"]);
                $("#num_sl_org_step3_s6").text(step3["num_slices_organ"]);
                $("#num_seqs_step3_s6").text(step3["num_seqs"]);
                $("#num_rem_sl_step3_s6").text(step3["num_remedied_slices"]);
                $("#size_step3_s6").text(String(step3["min_size"]) + " ↤ " + step3["avg_size"] + " ↦ " + step3["max_size"]);
                $("#num_sl_org_step4_s6").text(step4["num_slices_organ"]);
                $("#num_seqs_step4_s6").text(step4["num_seqs"]);
                $("#num_rem_sl_step4_s6").text(step4["num_remedied_slices"]);
                $("#size_step4_s6").text(String(step4["min_size"]) + " ↤ " + step4["avg_size"] + " ↦ " + step4["max_size"]);
                $("#num_sl_org_step5_s6").text(step5["num_slices_organ"]);
                $("#num_seqs_step5_s6").text(step5["num_seqs"]);
                $("#num_rem_sl_step5_s6").text(step5["num_remedied_slices"]);
                $("#size_step5_s6").text(String(step5["min_size"]) + " ↤ " + step5["avg_size"] + " ↦ " + step5["max_size"]);
            }, error: function () {

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
                        $("#step6_seg_"+diffs[i]).css("border", "4px solid #FF0000");
                    }
                    write_log_in_console("The number of violating slices is "+diffs.length+".");
                    write_log_in_console("Detecting violation is finished.");
                }, error: function (){
                    idx+=1;

                }
            });
        });

        $("#btn_task1_step6").on("click", function () {
            write_log_in_console("Remedying violation is started.");
            $.ajax({
                url: "/api/remedy_hu_violation",
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
                        $("#step6_enh_"+i).attr("src", "data:image/png;base64,"+sl_enh[i]);
                    }
                    var summary = data["data"]["summary"];
                    $("#input_step6_num_enhanced").text(summary["enh_num"]);
                    $("#input_step6_num_seq_after").text(summary["num_seqs"]);
                    write_log_in_console("Remedying violation is finished.");

                    $.ajax({
                        url: "/api/get_summary",
                        async: true,
                        method: 'POST',
                        data: {"data": JSON.stringify({"step": 6})},
                        data_type: "text",
                        success: function (data) {
                            // var data = JSON.parse(data);
                            d = data["data"];
                            var step1 = d["step1"];
                            var step2 = d["step2"];
                            var step3 = d["step3"];
                            var step4 = d["step4"];
                            var step5 = d["step5"];
                            var step6 = d["step5"];
                            console.log(d);
                            $("#num_sl_org_step1_s6").text(step1["num_slices_organ"]);
                            $("#num_seqs_step1_s6").text(step1["num_seqs"]);
                            $("#size_step1_s6").text(String(step1["min_size"]) + " ↤ " + step1["avg_size"] + " ↦ " + step1["max_size"]);
                            $("#num_sl_org_step2_s6").text(step2["num_slices_organ"]);
                            $("#num_seqs_step2_s6").text(step2["num_seqs"]);
                            $("#num_rem_sl_appearance_s6").text(step2["num_seqs"]);
                            $("#num_rem_sl_step2_s6").text(step2["num_remedied_slices"]);
                            $("#size_step2_s6").text(String(step2["min_size"]) + " ↤ " + step2["avg_size"] + " ↦ " + step2["max_size"]);
                            $("#num_sl_org_step3_s6").text(step3["num_slices_organ"]);
                            $("#num_seqs_step3_s6").text(step3["num_seqs"]);
                            $("#num_rem_sl_location_s6").text(step3["num_seqs"]);
                            $("#num_rem_sl_step3_s6").text(step3["num_remedied_slices"]);
                            $("#size_step3_s6").text(String(step3["min_size"]) + " ↤ " + step3["avg_size"] + " ↦ " + step3["max_size"]);
                            $("#num_sl_org_step4_s6").text(step4["num_slices_organ"]);
                            $("#num_seqs_step4_s6").text(step4["num_seqs"]);
                            $("#num_rem_sl_size_s6").text(step4["num_seqs"]);
                            $("#num_rem_sl_step4_s6").text(step4["num_remedied_slices"]);
                            $("#size_step4_s6").text(String(step4["min_size"]) + " ↤ " + step4["avg_size"] + " ↦ " + step4["max_size"]);
                            $("#num_sl_org_step5_s6").text(step5["num_slices_organ"]);
                            $("#num_seqs_step5_s6").text(step5["num_seqs"]);
                            $("#num_rem_sl_shape_s6").text(step5["num_seqs"]);
                            $("#num_rem_sl_step5_s6").text(step5["num_remedied_slices"]);
                            $("#size_step5_s6").text(String(step5["min_size"]) + " ↤ " + step5["avg_size"] + " ↦ " + step5["max_size"]);
                            $("#num_sl_org_step6_s6").text(step6["num_slices_organ"]);
                            $("#num_seqs_step6_s6").text(step6["num_seqs"]);
                            $("#num_rem_sl_hu_scale_s6").text(step6["num_seqs"]);
                            $("#num_rem_sl_step6_s6").text(step6["num_remedied_slices"]);
                            $("#size_step6_s6").text(String(step6["min_size"]) + " ↤ " + step6["avg_size"] + " ↦ " + step6["max_size"]);
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
            $("#step6_cur_sl").text(value);
            var val_move = 180*Number.parseInt(value-1);

            $('#div_slice_id_step6').scrollLeft(val_move);
            $('#div_slice_step6').scrollLeft(val_move);
            $('#div_org_step6').scrollLeft(val_move);
            $('#div_enh_step6').scrollLeft(val_move);
        });

        $("#btn_step6_back").on("click", function () {
            $("#smartwizard").smartWizard("prev");
            $("#btn_step6").removeClass("done");
            $("#step-6").css("display", "none");
            $("#step-5").css("display", "block");

        });

        $("#btn_lirads_step6_done").on("click", function () {

            // $.ajax({
            //     url:"/api/register_diagnosis_liver",
            //     async: true,
            //     method: "POST",
            //     data: {"data": JSON.stringify({"tumor_types":$("#txt_tumor_type").text(), "aphe_types":$("#txt_tumor_aphe_type").text(),
            //              "tumor_sizes":$("#txt_tumor_size").text(), "num_mfs":$("#txt_number_major_feature").text(),
            //             "stages":$("#txt_lirad_stage").text()})},
            //     data_type: "text",
            //     success: function (data) {
            //
            //     }, error: function () {
            //     clearInterval(interval);
            //     }
            // });

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

        $("#btn_statistics").on("click", function () {
            $("#modal_statistics").modal("show");
            $.ajax({
                url: "/api/summarize_statistics",
                async: false,
                method: 'POST',
                data: {"data": JSON.stringify()},
                data_type: "text",
                success: function (data) {
                    var d = data["data"];
                    console.log(d);
                    $("#num_sl_before_appearance").html(d["step2_before"]);
                    $("#num_sl_after_appearance").html(d["step2_after"]);
                    $("#num_sl_before_location").html(d["step3_before"]);
                    $("#num_sl_after_location").html(d["step3_after"]);
                    $("#num_sl_before_size").html(d["step4_before"]);
                    $("#num_sl_after_size").html(d["step4_after"]);
                    $("#num_sl_before_shape").html(d["step5_before"]);
                    $("#num_sl_after_shape").html(d["step5_after"]);
                    $("#num_sl_before_hu_scale").html(d["step6_before"]);
                    $("#num_sl_after_hu_scale").html(d["step6_after"]);
                    write_log_in_console("The number of violating slices is "+diffs.length+".");
                    write_log_in_console("Detecting violation is finished.");
                }, error: function (){
                    idx+=1;

                }
            });
        });
    });
})(jQuery);