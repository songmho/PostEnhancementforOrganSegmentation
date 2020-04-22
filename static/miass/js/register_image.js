(function () {
    function getfolder(e) {
    var files = e.target.files;
    var path = files[0].webkitRelativePath;
    var Folder = path.split("/");
    alert("Files in " + Folder[0] + " are uploaded.")
}
})(jQuery);

