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
                    $("#div_slice_step3").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <h5 class="text-center" id="step3_sl_title_"'+i+'>Slice #'+(i+1)+'</h5>\n' +
                        '    <img style="width: 150px; height: 150px;" class="border" id="step3_sl_'+i+'" src="data:image/png;base64,'+sl_org[i]+'">\n' +
                        '</div>');

                    $("#div_org_step3").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <h5 class="text-center" id="step3_seg_title_"'+i+'>Slice #'+(i+1)+'</h5>\n' +
                        '    <img style="width: 150px; height: 150px;" class="border" id="step3_seg_'+i+'" src="data:image/png;base64,'+sl_seg[i]+'">\n' +
                        '</div>');

                    $("#div_enh_step3").append(
                        '<div class="mx-1" style="display: inline-block;">\n' +
                        '    <h5 class="text-center" id="step3_enh_title_"'+i+'>Slice #'+(i+1)+'</h5>\n' +
                        '    <img style="width: 150px; height: 150px;" class="border" id="step3_enh_'+i+'" src="data:image/png;base64,0">\n' +
                        '</div>');
                }
            }, error: function (){

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
                }, error: function (){
                    idx+=1;

                }
            });
        });


        $('input[type=range]').on('change input', function() {
            var value = $(this).val();
            $("#step3_cur_sl").text(value);
            var val_move = 150*Number.parseInt(value-1);

            console.log(value, val_move);
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