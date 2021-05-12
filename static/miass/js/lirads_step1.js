(function () {

    var list_console = [];
    function write_log_in_console(text){
        var dt = new Date();
        list_console.push("["+dt.getFullYear()+"."+(dt.getMonth()+1).toString().padStart(2,"0")+"."+dt.getDate().toString().padStart(2,"0")+" "
            +dt.getHours().toString().padStart(2,"0")+":"+dt.getMinutes().toString().padStart(2,"0")+":"+dt.getSeconds().toString().padStart(2,"0")+"]  "+text);
        if (list_console.length >9)
            list_console.shift();

        $("#div_console").empty();
        for (var i in list_console)
            $("#div_console").append("<p class='mb-0'>"+list_console[i]+"</p>");
    };

    function upload_img(pat_name,pat_birth, acq_date , phase, form_loader_name, cur) {
        var cur_form_data_tmp = new FormData($(form_loader_name)[0]);
        var fileList= cur.files;
        isAnnoFileSelect = true;
        selected_img = [];

        for(var i=0; i<fileList.length;i++){
            selected_img.push(fileList[i].name);
        }
        var data = {"img":selected_img, "phase":phase, "pat_name": pat_name, "pat_birth":pat_birth, "acq_date":acq_date}
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
        console.log("IIHHH");
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
        $.when(ajax1(), ajax2(), ajax3()).done(function (r1, r2, r3) {
        });
        });
        
        $("#btn_loader_plain").on("change", function () {
            upload_img($("#input_pat_name").val(), $("#input_pat_birth").val(), $("#input_acq_date").val(), "plain", "#form_loader_plain", this);
        });
        $("#btn_loader_arterial").on("change", function () {
            upload_img($("#input_pat_name").val(), $("#input_pat_birth").val(), $("#input_acq_date").val(), "arterial", "#form_loader_arterial", this);
        });
        $("#btn_loader_pvp").on("change", function () {
            upload_img($("#input_pat_name").val(), $("#input_pat_birth").val(), $("#input_acq_date").val(), "venous", "#form_loader_pvp", this);
        });
        $("#btn_loader_delay").on("change", function () {
            upload_img($("#input_pat_name").val(), $("#input_pat_birth").val(), $("#input_acq_date").val(), "delay", "#form_loader_delay", this);
        });
    });
})(jQuery);