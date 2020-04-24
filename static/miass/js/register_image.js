(function () {
    // function getfolder(e) {
    //     var files = e.target.files;
    //     var path = files[0].webkitRelativePath;
    //     var Folder = path.split("/");
    //     alert("Files in " + Folder[0] + " are uploaded.")
    // }

    $("#btn_submit").click(function () {
        var uploader_id = $("#uploader_id").val();
        var taken_date = $("#taken_date").val();
        var taken_place = $("#taken_place").val();
        var image_path = $("#image_path").val();
        // alert(uploader_id + taken_date + taken_place + image_path);
        var folder_list = $("#image_folder").val();
        alert(folder_list);
    })

    // $("#image_folder").
    $('#btn_img_loader').on('change', function (e) {
        var fileList = this.files;
        var fileReader = new FileReader();
        var fileName = e.target.files[0];
        $('#img_slider').attr('min', 0);
        $('#img_slider').attr('max', fileList.length-1);


        console.log("name: ", $('#btn_img_loader').prop('files'));
        fileReader.readAsDataURL($('#btn_img_loader').prop('files')[0]);
        fileReader.onload = function () {
            $('#img_preview').attr("src",fileReader.result);
        };
    });

    $('#img_slider').on("input", function () {
        var fileReader = new FileReader();
        fileReader.readAsDataURL($('#btn_img_loader').prop('files')[$('#img_slider').val()]);
        fileReader.onload = function () {
            $('#img_preview').attr("src",fileReader.result);
        };
        $('#txt_num').attr("value", $('#img_slider').val());
        $('#txt_num').text($('#img_slider').val());
    });

    $('#')

})(jQuery);

