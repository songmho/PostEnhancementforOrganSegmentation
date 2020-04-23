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


})(jQuery);

