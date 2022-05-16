(function () {
    var table_prv_imgs = null;
    var is_prv_data_selected = false;
    var cur_img_path = -1;

    function upload_img(pat_name,type, form_loader_name, cur) {
        var cur_form_data_tmp = new FormData($(form_loader_name)[0]);
        var fileList= cur.files;
        isAnnoFileSelect = true;
        selected_img = [];

        for(var i=0; i<fileList.length;i++){
            selected_img.push(fileList[i].name);
        }
        var data = {"img":selected_img, "pat_name": pat_name, "type": type};
        cur_form_data_tmp.append("data", JSON.stringify(data));
        var splited = selected_img[0].split(".");
        let format = splited[splited.length-1];

        $.ajax({
            type:"POST",
            enctype: 'multipart/form-data',
            url: '/api/load_img/',
            data: cur_form_data_tmp,
            processData: false,
            contentType: false,
            cache: false,
            timeout: 600000,
            async: false,
            success: function (data) {
                console.log(data["data"]);
                var type = data["data"]["type"]
                var format = data["data"]["format"]
                if (format === "nii" && type === null) {
                    $("#modal_img_type").modal("show");
                }
                write_log_in_console("Reading "+phase+" phase.");
            }, error: function (){
            }
        });
    }

    $(document).ready(function(){

        $.ajax({
            url: "/api/initialize_diagnosis_env",
            async: true,
            method: 'POST',
            data_type: "text",
            success: function (data) {
                console.log("INITIALIZED");
            }, error: function (){
            }
        });

        write_log_in_console("Step 1 is to encode medical images.");
        $("#btn_lirads_step1_next").on("click", function () {
            $("#step-2").empty();
            $("#step-1").css("display", "none");
            $("#step-2").css("display", "block");
            $.post("/view/lirads_step2/", null, function (result) {
                $("#step-2").append(result);
            });
            $("#btn_step1").removeClass("active").addClass("done");
            $("#btn_step2").addClass("active");
            $("#smartwizard").smartWizard("next");

        });

        $("#btn_load_srs").on("change", function () {
            console.log("btn_loader_seg_result");
            $("#input_num_slices").text("86");
            upload_img(get_current_profile().identification_number, "srs","#form_loader_srs", this);
        });
        $("#btn_loader_srs").on("change", function () {
            console.log("btn_loader_srs");
            upload_img(get_current_profile().identification_number, "seg_result","#form_loader_seg_result", this);
        });
        $("#btn_load_seg_result_uploaded").on("click", function () {
            console.log("btn_load_seg_result_uploaded");
            // upload_img($("#input_pat_name").val(), $("#input_pat_birth").val(), $("#input_mrn").val(), $("#input_acq_date").val(), "venous", "#form_loader_pvp", this);
        });
        $("#btn_proceed").on("click", function () {
            $.ajax({
                url: "/api/encode_medical_img",
                async: true,
                method: 'POST',
                data: JSON.stringify({"uid": null}),
                success: function (data) {
                    console.log(data);
                    var d = data["data"];
                    write_log_in_console("Loaded medical images are encoded.");
                    $("#input_num_slices").text(d["num_slice"]);
                    $("#input_applied_hu_range").text(d["hu_start"]+" ~ "+d["hu_end"]);
                }, error: function (){

                }

            })


        });

        $("#btn_load_prv_dat").on("click", function(){
            $.ajax({
                url: "/api/retrieve_images",
                async: true,
                method: 'POST',
                data: JSON.stringify({"uid": null}),
                success: function (data) {
                    var d = data["data"];
                    console.log(d);
                    $("#table_prv_img tbody").empty();
                    // for(var i in d){
                    //     $("#list_car_model tbody").append(""+
                    //         "<tr id='"+d[i]["model_code"]+"'>\n" +
                    //         "    <th scope=\"row\">"+(parseInt(i)+1)+"</th>\n" +
                    //         "    <td>"+d[i]['manufacturer']+"</td>\n" +
                    //         "    <td>"+d[i]['type']+"</td>\n" +
                    //         "    <td>"+d[i]['name']+"</td>\n" +
                    //         "</tr>"
                    //     )
                    // }
                    try{
                        table_prv_imgs.clear();
                    }catch (e){}

                    var table_d = [];
                    for (var i in d) {
                        var cur_d = [(parseInt(i)+1),
                            d[i]['medical_record_number'],
                            d[i]['birthday'],
                            d[i]['first_name'],
                            d[i]['last_name'],
                            d[i]['img_type'],
                            d[i]['acquisition_date'],
                            d[i]["examination_source"],
                            d[i]["img_path"]]
                        table_d.push(cur_d)
                    }
                    if(table_prv_imgs===null){
                        table_prv_imgs = $("#table_prv_img").DataTable({data:table_d, paging: true, searching:false, info:false,
                            columns:[{title:"No."},{title:"mrn", "class":"class_hide"},{title:"birthday", "class":"class_hide"},
                                {title:"First Name"},{title:"Last Name"},{title:"Image Type"},{title:"Acquisition Date"},
                                {title:"Examination Source"}, {title:"img_path", "class":"class_hide"}]});
                    }else{
                        table_prv_imgs.rows.add(table_d).draw();
                    }
                    $("#modal_prv_data").modal("show");
                }, error: function (){

                }
            });
        });


    });
})(jQuery);