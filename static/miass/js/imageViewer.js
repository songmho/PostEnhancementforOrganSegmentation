/**
 * Created by hanter on 2016. 3. 12..
 */

var imageDirs = null;
var $imageViewer = null;

$(document).ready(function() {

});

function openImageViewer() {
    $('#dicomViewModal').modal({backdrop: 'static'});

}

function setOpenImageViewerListener(id) {
    $imageViewer = $('#'+id);
    $imageViewer.click(function() {
        if (imageDirs == null) {
            $.LoadingOverlay('show');
            $.ajax("/api/medical_image", {
                method: 'GET',
                data: {
                    action: 'getImageDirs',
                    user_id: user['user_id'],
                    image_id: imageInfo['image_id']
                }, dataType: 'json',
                    success: function (res) {
                    $.LoadingOverlay('hide');
                    if(res['code'] == 'SUCCESS') {
                        $('#dicomViewModal').modal({backdrop: 'static'});
                        imageDirs = res['image_list'];
                        console.log(imageDirs);
                    } else {
                        openModal(res['msg'], "Image Loading Failed");
                    }
                }
            });
        } else {
            openImageViewer();
        }
    });
}

function resetViewer() {
    $imageViewer.unbind('click');
    $imageViewer = null;
    imageDirs = null;
}