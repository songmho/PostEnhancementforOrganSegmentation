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
        write_log_in_console("Step 4. Evaluating image features of tumors is started.");
        write_log_in_console("The tumor image features classification model is being prepared.");
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
            url:"/api/load_tumor_list",
            async: true,
            method: "POST",
            data: {"data": JSON.stringify({})},
            data_type: "text",
            success: function (data) {
                d = data["data"];
                var img_list = data["imgs"];
                numImgs = d.length;

                for (var i in d){
                    slice = img_list[i];

                    if (i==0){
                        $("#list_slices_step_4").append("<a class='list-group-item list-group-item-action active w-100'" +
                            " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"_step4'>"+d[i]+"</a>");
                        $("#sl_id_tumors").append("<div class=\"h-100 tab-pane show active\" id=\"list_"+i+"_step4\" role=\"tabpanel\" aria-labelledby=\"list_"+i+"_list_tumors_step4\">\n" +
                            "                <div class=\"row h-100\">\n" +
                            "                    <div style='width: 2.56%'></div>\n" +
                            "                    <div id=\"div_img\" style='width: 47.44%' class=\"mr-0 border border-dark p-2\">\n" +
                            "                        <div class=\"div_area text-center h-100\">\n" +
                            "                          <h5 class=\"mx-auto px-auto text-center\">Tumor Image</h5>" +
                            "                          <div class='mx-auto text-center'>" +
                            "                            <img src=data:image/png;base64,"+slice+" height=\"220px\" width=\"220px\">\n" +
                            "                          </div>"+
                            "                        </div>\n" +
                            "                    </div>\n" +
                            "                    <div style='width: 2.56%'></div>\n" +
                            "                    <div id=\"div_features\" style='width: 47.44%' class=\"border border-dark p-2\">\n" +
                            "                      <h5 class='mx-auto px-auto text-center'>Predicted Image Features</h5>\n" +
                            "                        <div id=\"div_img_features"+i+"_step4\" class=\"ml-2\">\n" +
                            "                        </div>\n" +
                            "                    </div>\n" +
                            "                </div>\n" +
                            "            </div>");

                    }else{
                        $("#list_slices_step_4").append("<a class='list-group-item list-group-item-action w-100'" +
                            " role='tab' id='list_"+i+"_list_tumors_step4"+"' data-toggle='list' href='#list_"+i+"_step4'>"+d[i]+"</a>");

                        $("#sl_id_tumors").append("<div class=\"h-100  tab-pane\" id=\"list_"+i+"_step4\" role=\"tabpanel\" aria-labelledby=\"list_"+i+"_list_tumors_step4\">\n" +
                            "                <div class=\"row h-100\">\n" +
                            "                    <div style='width: 2.56%'></div>\n" +
                            "                    <div id=\"div_img\" style='width: 47.44%' class=\"mr-0 border border-dark p-2\">\n" +
                            "                        <div class=\"div_area text-center h-100\">\n" +
                            "                          <h5 class=\"mx-auto px-auto text-center\">Tumor Image</h5>" +
                            "                          <div class='mx-auto text-center'>" +
                            "                            <img src=data:image/png;base64,"+slice+" height=\"220px\" width=\"220px\">\n" +
                            "                          </div>"+
                            "                        </div>\n" +
                            "                    </div>\n" +
                            "                    <div style='width: 2.56%'></div>\n" +
                            "                    <div id=\"div_features\" style='width: 47.44%' class=\"border border-dark p-2\">\n" +
                            "                      <h5 class='mx-auto px-auto text-center'>Predicted Image Features</h5>\n" +
                            "                        <div id=\"div_img_features"+i+"_step4\" class=\"ml-2\">\n" +
                            "                          <h6></h6>\n" +
                            "                        </div>\n" +
                            "                    </div>\n" +
                            "                </div>\n" +
                            "            </div>");
                    }

                }
                write_log_in_console("Loading tumor images is finished.");

            },error: function (err) {

            }
        });

        $("#btn_evaluate_step4").on("click", function () {
            write_log_in_console("Classifying image features of tumors is started.");
            $("#div_init_step4").css("display", "none");
            $("#div_start_step4").css("display", "block");
            $("#div_pause_step4").css("display", "none");
            isPause = false;
            intervalSegment = setInterval(function () {
                if(!isPause){
                    $.ajax({
                    url: "/api/evaluate_img_feature",
                    async: false,
                    method: 'POST',
                    data: {"data": JSON.stringify({"target_img":idx})},
                    data_type: "text",
                    success: function (data) {
                        var text = data["console"];
                        console.log(data["img"]);
                        var slice = data["img"];
                        write_log_in_console("Image features of the tumor in "+d[idx]+" is evaluated; "+text);


                        $("#list_slices_step_4").children().removeClass("active");
                        $("#sl_id_tumors").children().removeClass("active");
                        $("#list_"+idx+"_list_tumors_step4").addClass("active");
                        $("#list_"+idx+"_step4").addClass("active");
                        for (var i in slice){
                            var data = slice[i].split(",");
                            for (var j in data)
                                $("#div_img_features"+idx+"_step4").append("<h6>"+data[j]+"</h6>");
                        }

                        try{
                            let y_position = document.querySelector("#list_"+(idx-1)+"_list_tumors_step4").offsetTop;
                            $("#list_slices_step_4").scrollTop(y_position);
                        }catch (e) {
                           let y_position = document.querySelector("#list_"+(idx)+"_list_tumors_step4").offsetTop;
                           $("#list_slices_step_4").scrollTop(y_position);
                        }
                        if (idx >= (numImgs-1)){
                            // $("#div_process").css("display", "none");
                           $("#div_start_step4").css("display", "none");
                            $("#div_init_step4").css("display", "block");
                            isPause = false;
                            idx = 0;
                            clearInterval(intervalSegment);
                            write_log_in_console("Classifying image features of tumors is finished.");
                        }
                        idx+=1;
                    }, error: function (){
                        // idx+=1;
                        clearInterval(intervalSegment);
                    }
                    });
                }
            },500);
        });
        $("#btn_pause_evaluate_step4").on("click", function () {
            write_log_in_console("Classifying image features of tumors is paused.");
            $("#div_init_step4").css("display", "none");
            $("#div_start_step4").css("display", "none");
            $("#div_pause_step4").css("display", "block");
            isPause = true;
        });
        $("#btn_stop_evaluate_step4").on("click", function () {
            write_log_in_console("Classifying image features of tumors is stopped.");
            idx=0;
            $("#div_init_step4").css("display", "block");
            $("#div_start_step4").css("display", "none");
            $("#div_pause_step4").css("display", "none");
            isPause = false;
            clearInterval(intervalSegment);
        });
        $("#btn_resume_evaluate_step4").on("click", function () {
            write_log_in_console("Classifying image features of tumors is resumed.");
            $("#div_init_step4").css("display", "none");
            $("#div_start_step4").css("display", "block");
            $("#div_pause_step4").css("display", "none");
            isPause = false;
        });


        $("#btn_lirads_step4_back").on("click", function () {
            $("#smartwizard").smartWizard("prev");
            $("#btn_step4").removeClass("done");
            $("#step-4").css("display", "none");
            $("#step-3").css("display", "block");

        });

        $("#btn_lirads_step4_next").on("click", function () {
            $("#step-5").empty();
            $("#step-4").css("display", "none");
            $("#step-5").css("display", "block");
            $.post("/view/lirads_step5/", null, function (result) {
                $("#step-5").append(result);
            });
            $("#btn_step4").removeClass("active").addClass("done");
            $("#btn_step5").addClass("active");
            $("#smartwizard").smartWizard("next");

        });
    });
})(jQuery);