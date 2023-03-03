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
                    console.log(i);
                    $("#div_slice_step5").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <h5 class="text-center" id="step5_sl_title_"'+i+'>Slice #'+(i+1)+'</h5>\n' +
                        '    <img style="width: 150px; height: 150px;" class="border" id="step5_sl_'+i+'" src="data:image/png;base64,'+sl_org[i]+'">\n' +
                        '</div>');

                    $("#div_org_step5").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <h5 class="text-center" id="step5_seg_title_"'+i+'>Slice #'+(i+1)+'</h5>\n' +
                        '    <img style="width: 150px; height: 150px;" class="border" id="step5_seg_'+i+'" src="data:image/png;base64,'+sl_seg[i]+'">\n' +
                        '</div>');

                    $("#div_enh_step5").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <h5 class="text-center" id="step5_enh_title_"'+i+'>Slice #'+(i+1)+'</h5>\n' +
                        '    <img style="width: 150px; height: 150px;" class="border" id="step5_enh_'+i+'" src="data:image/png;base64,0">\n' +
                        '</div>');
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
                }, error: function (){
                    idx+=1;

                }
            });
        });

        $('input[type=range]').on('change input', function() {
            var value = $(this).val();
            $("#step5_cur_sl").text(value);
            var val_move = 150*Number.parseInt(value-1);

            console.log(value, val_move);
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