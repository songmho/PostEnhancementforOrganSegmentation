/**
 * Created by hanter on 2016. 3. 12..
 */

var imageDirs = null;
var $imageViewer = null;

$(document).ready(function() {

});

function openImageViewer() {
    $.LoadingOverlay('show');

    setTimeout(function() {
        var listExplorer = $('#image-view-list');
        listExplorer.empty();

        for (var rootName in imageDirs) {
            var rootImgInfo = imageDirs[rootName];

            if (rootImgInfo['type'] == 'folder') {
                for (var dirName in rootImgInfo['file_list']) {
                    var dirs = rootImgInfo['file_list'][dirName];
                    listExplorer.append('<li>').append(
                        generateExplorer(dirs, dirName)
                    ).append('</li>');
                }
            } else {
                listExplorer.append('<span><a data-dir="' + rootImgInfo['dir']
                    + '" data-type="' + rootImgInfo['type'] + '">'
                    + imageInfo['subject'] + '<a/></span>');
            }
            break;
        }

        $.LoadingOverlay('hide');
        $('#imageViewModal').modal({backdrop: 'static'});
    }, 0);
}

function generateExplorer(dirs, name) {
    if (dirs['type'] == 'folder') {
        var htmlString = '<span>'+name+'</span><ul>';
        for (var dirName in dirs['file_list']) {
            var childDirs = dirs['file_list'][dirName];
            htmlString += '<li>'+generateExplorer(childDirs, dirName)+'</li>'
        }
        htmlString += '</ul>';
        return htmlString;
    } else {
        return '<a data-dir="'+dirs['dir']+'" data-type="'+dirs['type']+'">'+name+'</a>';
    }
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
                        openImageViewer();
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