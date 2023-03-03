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
                    $("#div_slice_step4").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <h5 class="text-center" id="step4_sl_title_"'+i+'>Slice #'+(i+1)+'</h5>\n' +
                        '    <img style="width: 150px; height: 150px;" class="border" id="step4_sl_'+i+'" src="data:image/png;base64,'+sl_org[i]+'">\n' +
                        '</div>');

                    $("#div_org_step4").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <h5 class="text-center" id="step4_seg_title_"'+i+'>Slice #'+(i+1)+'</h5>\n' +
                        '    <img style="width: 150px; height: 150px;" class="border" id="step4_seg_'+i+'" src="data:image/png;base64,'+sl_seg[i]+'">\n' +
                        '</div>');

                    $("#div_enh_step4").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <h5 class="text-center" id="step4_enh_title_"'+i+'>Slice #'+(i+1)+'</h5>\n' +
                        '    <img style="width: 150px; height: 150px;" class="border" id="step4_enh_'+i+'" src="data:image/png;base64,0">\n' +
                        '</div>');
                }
            }, error: function (){

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
                }, error: function (){
                    idx+=1;

                }
            });
        });

        $('input[type=range]').on('change input', function() {
            var value = $(this).val();
            $("#step4_cur_sl").text(value);
            var val_move = 150*Number.parseInt(value-1);

            console.log(value, val_move);
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