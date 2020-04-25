var is_uploaded= false;
var path = "";
(function () {
    // function getfolder(e) {
    //     var files = e.target.files;
    //     var path = files[0].webkitRelativePath;
    //     var Folder = path.split("/");
    //     alert("Files in " + Folder[0] + " are uploaded.")
    // }

    $("#btn_submit").click(function () {
        var fir_name = $("#txt_fir_name").val();
        var last_name = $("#txt_last_name").val();
        var birthday = $("#txt_Birthday").val();
        var gender = $("#txt_gender").val();
        var acq_date = $("#txt_acq_date").val();
        var exam_src = $("#txt_exam_src").val();
        var interpretation = $("#txt_interpret").val();
        var description = $("#txt_desc").val();
        var img_type = $("#txt_img_type").val();

        var form_upload = $("#form_upload")[0];
        var file_data = new FormData(form_upload);

        if (img_type==="" || fir_name==="" || last_name === "" || acq_date==="" || exam_src==="" ) {
        $("#txt_fir_name").addClass("is-invalid");
        $("#txt_last_name").addClass("is-invalid");
        $("#txt_img_type").addClass("is-invalid");
        $("#txt_acq_date").addClass("is-invalid");
        $("#txt_exam_src").addClass("is-invalid");

        }else{
            $.ajax({
                type:"POST",
                enctype: 'multipart/form-data',
                url: '/api/upload/',
                data: file_data,
                processData: false,
                contentType: false,
                cache: false,
                timeout: 600000,
                async: false,
                success: function (data) {
                    console.log(data)
                    if(data['state']){
                        is_uploaded = true;
                        path= data['path'];
                    }else{
                        is_uploaded = false;

                    }
                }, error: function (err) {
                        is_uploaded = false;

                }
            });

            if (is_uploaded){
                $.ajax({
                    type:"POST",
                    url: '/api/upload_txt/',
                    data: JSON.stringify({"fir_name": fir_name, "last_name": last_name, "birthday": birthday,
                        "gender": gender, "img_path":path, "acquisition_date": acq_date, "examination_source":exam_src, "interpretation":interpretation,
                        "description": description, 'uploader_id':1, "img_type":img_type}),
                    async: false,
                    success: function (data) {
                        console.log(data)
                        if(data['state']){
                            location.reload();
                        }else{
                        }
                    },
                    error: function (e) {
                    }
                });
            }

        }


    });

    // $("#image_folder").
    $('#btn_img_loader').on('change', function (e) {
        var fileList = this.files;
        var fileReader = new FileReader();
        var fileName = e.target.files[0];
        $('#img_slider').attr('min', 0);
        $('#img_slider').attr('max', fileList.length-1);
        $('#txt_max_num').text(fileList.length);
        $('#txt_num').text(1);


        console.log("name: ", $('#btn_img_loader').prop('files'));
        fileReader.readAsDataURL($('#btn_img_loader').prop('files')[0]);
        fileReader.onload = function () {
            $('#img_preview').attr("src", fileReader.result);
        };
    });

    $('#img_slider').on("input", function () {
        var fileReader = new FileReader();
        fileReader.readAsDataURL($('#btn_img_loader').prop('files')[$('#img_slider').val()]);
        fileReader.onload = function () {
            $('#img_preview').attr("src",fileReader.result);
        };
        var num = Number($('#img_slider').val())+1;
        $('#txt_num').text(num);
    });

})(jQuery);

