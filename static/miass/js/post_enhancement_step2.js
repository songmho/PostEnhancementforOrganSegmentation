(function () {
    var idx= 0;
    var d;
    var max_sl_num = 0;

    $(document).ready(function(){
        $(".class_step2_task2").css("display", "None");
        $(".class_step2_task3").css("display", "None");
        write_log_in_console("Step 2 is to remedy appearance violation.");
        $.ajax({
            url: "/api/load_img_list",
            async: true,
            method: 'POST',
            data: {"data": JSON.stringify({})},
            data_type: "text",
            success: function (data) {
                // var data = JSON.parse(data);
                d = data["data"];
                var sl_org = d["sl_org"];
                var sl_seg = d["sl_seg"];
                $("#step2_max_sl").text(sl_org.length);
                $("#step2_cur_sl").text(1);
                max_sl_num = sl_org.length;
                $('input[type=range]').attr("max", max_sl_num);

                for (var i = 0; i<sl_org.length; i++){
                    console.log(i);
                    $("#div_slice_id_step2").append(
                        '<div class="mx-1" style="display: inline-block; width: 180px;">\n' +
                        '    <h5 class="text-center" id="step2_sl_title_"'+i+'>Slice #'+(i+1)+'</h5>\n' +
                        '</div>');
                    $("#div_slice_step2").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <img style="width: 180px; height: 180px;" class="border" id="step2_sl_'+i+'" src="data:image/png;base64,'+sl_org[i]+'">\n' +
                        '</div>');

                    $("#div_org_step2").append(
                    '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <img style="width: 180px; height: 180px;" class="border" id="step2_seg_'+i+'" src="data:image/png;base64,'+sl_seg[i]+'">\n' +
                        // '    <div class="mx-auto inline" style="text-align: center;"> <h5 style="display: inline">SEQ #</h5> <h5 style="display: inline">(88888)</h5> </div>' +
                        '</div>');

                    $("#div_enh_step2").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <img style="width: 180px; height: 180px;" class="border" id="step2_enh_'+i+'" src="data:image/png;base64,0">\n' +
                        // '    <div class="mx-auto inline" style="text-align: center;"> <h5 style="display: inline" id="seq_enh_step2_'+i+'">SEQ #</h5> <h5 style="display: inline" id="num_pix_enh_step2_'+i+'">(.)</h5> </div>' +
                        '</div>');
                }

            }, error: function (){

            }
        });

        $.ajax({
            url: "/api/get_summary",
            async: true,
            method: 'POST',
            data: {"data": JSON.stringify({"step": 1})},
            data_type: "text",
            success: function (data) {
                // var data = JSON.parse(data);
                d = data["data"];
                var step1 = d["step1"];
                console.log(d);
                $("#num_sl_org_step1_s2").text(step1["num_slices_organ"]);
                $("#num_seqs_step1_s2").text(step1["num_seqs"]);
                $("#size_step1_s2").text(String(step1["min_size"]) + " ↤ " + step1["avg_size"] + " ↦ " + step1["max_size"]);
            }, error: function () {

            }
        });

        $('input[type=range]').on('change input', function() {
            var value = $(this).val();
            $("#step2_cur_sl").text(value);
            var val_move = 180*Number.parseInt(value-1);

            $('#div_slice_id_step2').scrollLeft(val_move);
            $('#div_slice_step2').scrollLeft(val_move);
            $('#div_org_step2').scrollLeft(val_move);
            $('#div_enh_step2').scrollLeft(val_move);
        });

        $("#btn_detect_appearance").on("click", function () {
            write_log_in_console("Detecting violation is started.");
            $.ajax({
                url: "/api/detect_appearance_violation",
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

        $("#btn_task1_step2").on("click", function () {
            write_log_in_console("Remedying violation is started.");
            $.ajax({
                url: "/api/remedy_appearance_violation",
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
                        $("#step2_enh_"+i).attr("src", "data:image/png;base64,"+sl_enh[i]);
                    }
                    var summary = data["data"]["summary"];
                    $("#input_step2_num_enhanced").text(summary["enh_num"]);
                    $("#input_step2_num_seq_after").text(summary["num_seqs"]);
                    write_log_in_console("Remedying violation is finished.");

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
                            $("#num_sl_org_step1_s2").text(step1["num_slices_organ"]);
                            $("#num_seqs_step1_s2").text(step1["num_seqs"]);
                            $("#size_step1_s2").text(String(step1["min_size"]) + " ↤ " + step1["avg_size"] + " ↦ " + step1["max_size"]);
                            $("#num_sl_org_step2_s2").text(step2["num_slices_organ"]);
                            $("#num_seqs_step2_s2").text(step2["num_seqs"]);
                            $("#num_rem_sl_step2_s2").text(step2["num_remedied_slices"]);
                            $("#size_step2_s2").text(String(step2["min_size"]) + " ↤ " + step2["avg_size"] + " ↦ " + step2["max_size"]);
                        }, error: function () {

                        }
                    });
                }, error: function (){
                    idx+=1;

                }
            });
        });


        $("#btn_step2_back").on("click", function () {
            $("#smartwizard").smartWizard("prev");
            $("#btn_step2").removeClass("done");
            $("#step-2").css("display", "none");
            $("#step-1").css("display", "block");

        });

        $("#btn_step2_next").on("click", function () {
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