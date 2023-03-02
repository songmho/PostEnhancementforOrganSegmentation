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
        console.log(type);
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
                if (type === "srs"){
                    $("#input_num_slices").text(data["data"]["num_slices"]);
                } else if (type === "label") {
                    $("#input_num_slices_having_organ_label").text(data["data"]["num_slices"]);
                } else{
                    $("#input_num_slices_having_organ").text(data["data"]["num_slices"]);
                }
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

        $("#input_loader_srs").on("change", function () {
            console.log("btn_loader_seg_result");
            upload_img("test", "srs","#form_loader_srs", this);
        });
        $("#btn_loader_seg_result").on("change", function () {
            upload_img("test", "seg_result","#form_loader_seg_result", this);
        });

        $("#btn_loader_mask").on("change", function () {
            upload_img("test", "label","#form_loader_mask", this);
        });

        $("#btn_identify_sequence").on("click", function () {
            $.ajax({
                url: "/api/identify_continuity_sequence",
                async: true,
                method: 'POST',
                data: JSON.stringify({"uid": null}),
                success: function (data) {
                    console.log(data);
                    var d = data["data"];
                    var d1 = d["seg_result"];
                    var d2 = d["label"];

                    $("#inputNumSequences").text(d1["num_seqs"]);
                    for (var i = 1; i<=Number.parseInt(d1["num_seqs"]); i++){
                        $("#thead_step1").append('<th class="">'+(i)+'</th>\n');
                        $("#tr_step1").append('<td >'+d1["seq"][String(i-1)]["start"]+' - '+d1["seq"][String(i-1)]["end"]+'</td>\n');
                    }

                    $("#inputNumSequences_label").text(d2["num_seqs"]);
                    for (var i = 1; i<=Number.parseInt(d2["num_seqs"]); i++){
                        $("#thead_step1_lb").append('<th class="">'+(i)+'</th>\n');
                        $("#tr_step1_lb").append('<td >'+d2["seq"][String(i-1)]["start"]+' - '+d2["seq"][String(i-1)]["end"]+'</td>\n');
                    }
                }, error: function (){

                }

            });

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

            });


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