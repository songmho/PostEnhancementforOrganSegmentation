(function () {
    var table_prv_imgs = null;
    var is_prv_data_selected = false;
    var cur_img_path = -1;

    function upload_img(pat_name, pat_birth, mrn, acq_date , phase, form_loader_name, cur) {
        var cur_form_data_tmp = new FormData($(form_loader_name)[0]);
        var fileList= cur.files;
        isAnnoFileSelect = true;
        selected_img = [];

        for(var i=0; i<fileList.length;i++){
            selected_img.push(fileList[i].name);
        }
        var data = {"img":selected_img, "phase":phase, "pat_name": pat_name, "mrn":mrn, "pat_birth":pat_birth, "acq_date":acq_date}
        cur_form_data_tmp.append("data", JSON.stringify(data));
        var splited = selected_img[0].split(".");
        let format = splited[splited.length-1];

        $("#lb_num_img").html("&nbsp;"+fileList.length);
        $("#lb_format").html("&nbsp;"+format);

        $.ajax({
            type:"POST",
            enctype: 'multipart/form-data',
            url: '/api/load_lirads_img_nii/',
            data: cur_form_data_tmp,
            processData: false,
            contentType: false,
            cache: false,
            timeout: 600000,
            async: false,
            success: function (data) {
                write_log_in_console("CT slices in "+phase+" phase are uploaded.");
            }, error: function (){
            }
        });
    }
    function ajax1() {
        console.log("ajax1");
        return $.ajax({
            url: "/api/check_extension",
            async: false,
            method: 'POST',
            data: {},
            data_type: "text",
            success: function (data) {
                write_log_in_console("Checking extension of uploaded CT study is finished.");
            }
        });
    }
    function ajax2() {
        console.log("ajax2");
        return $.ajax({
            url: "/api/load_medical_img",
            async: false,
            method: 'POST',
            data: {},
            data_type: "text",
            success: function (data) {
                write_log_in_console("Loading CT slices to memory is finished.");
            }
        });
    }
    function ajax3() {
        console.log("ajax3");
        return $.ajax({
            url: "/api/convert_color_depth",
            async: false,
            method: 'POST',
            data: {},
            data_type: "text",
            success: function (data) {
                write_log_in_console("Converting CT slices considering color depth is finished.");
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

        write_log_in_console("Step 1. Loading target medical image is started.");
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
        $("#btn_start_step1").on("click", function () {
            if (!is_prv_data_selected){
                $.when(ajax1(), ajax2(), ajax3()).done(function (r1, r2, r3) {
                });
            }else{
                $.when(ajax1(), ajax2(), ajax3()).done(function ( r1, r2, r3) {
                });
            }
        });
        
        $("#btn_loader_plain").on("change", function () {
            upload_img($("#input_pat_name").val(), $("#input_pat_birth").val(), $("#input_mrn").val(), $("#input_acq_date").val(), "plain", "#form_loader_plain", this);
        });
        $("#btn_loader_arterial").on("change", function () {
            upload_img($("#input_pat_name").val(), $("#input_pat_birth").val(), $("#input_mrn").val(), $("#input_acq_date").val(), "arterial", "#form_loader_arterial", this);
        });
        $("#btn_loader_pvp").on("change", function () {
            upload_img($("#input_pat_name").val(), $("#input_pat_birth").val(), $("#input_mrn").val(), $("#input_acq_date").val(), "venous", "#form_loader_pvp", this);
        });
        $("#btn_loader_delay").on("change", function () {
            upload_img($("#input_pat_name").val(), $("#input_pat_birth").val(), $("#input_mrn").val(), $("#input_acq_date").val(), "delay", "#form_loader_delay", this);
        });

        $("#btn_load_prv_dat").on("click", function(){
            $.ajax({
                url: "/api/retrieve_images",
                async: true,
                method: 'POST',
                data: JSON.stringify({"uid": null,}),
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


        $("#table_prv_img").on("draw.dt", function () {
            $(".class_hide").css("display", "none");
        });

        $(document.body).delegate("#table_prv_img tbody tr", "click", function(){
            var item = $(this);
            if(item.children().eq(1).html()!==undefined) {
                var mrn = item.children().eq(1).html();
                var fir_name = item.children().eq(3).html();
                var last_name = item.children().eq(4).html();
                var birthday = item.children().eq(2).html();
                var acq_date = item.children().eq(6).html();
                cur_img_path = item.children().eq(8).html();

                console.log(fir_name, last_name, birthday, cur_img_path);
                $("#input_pat_name").val(fir_name+" "+last_name);
                $("#input_mrn").val(mrn);
                $("#input_pat_birth").val(birthday);
                $("#input_acq_date").val(acq_date);
                // console.log(cur_car_model);
                // $("#modal_car_item").val("");
                // $("#modal_car_model").val(item.children().eq(2).html() + " " + item.children().eq(4).html());
                is_prv_data_selected = true;

                $("#btn_load_plain_text").removeClass("btn-outline-info").addClass("btn-secondary").addClass("disabled");
                $("#btn_load_arterial_text").removeClass("btn-outline-info").addClass("btn-secondary").addClass("disabled");
                $("#btn_load_pvp_text").removeClass("btn-outline-info").addClass("btn-secondary").addClass("disabled");
                $("#btn_load_delay_text").removeClass("btn-outline-info").addClass("btn-secondary").addClass("disabled");
                $("#btn_loader_plain").prop("disabled", true);
                $("#btn_loader_arterial").prop("disabled", true);
                $("#btn_loader_pvp").prop("disabled", true);
                $("#btn_loader_delay").prop("disabled", true);
                console.log({"img_path": cur_img_path, "pat_name":$("#input_pat_name").val(), "pat_birth":$("#input_pat_birth").val(),"mrn":$("#input_mrn").val()});
                return $.ajax({
                    url: "/api/load_prv_img_data_from_local",
                    async: true,
                    method: 'POST',
                    data: {"data": JSON.stringify({"img_path": cur_img_path, "pat_name":$("#input_pat_name").val(), "pat_birth":$("#input_pat_birth").val(),"mrn":$("#input_mrn").val()})},
                    data_type: "text",
                    success: function (data) {
                        $("#modal_prv_data").modal("hide");
                    }, error: function (){
                    }
                });
            }
        });
    });
})(jQuery);