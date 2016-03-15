/**
 * Created by hanter on 2016. 3. 12..
 */

var imageDirs = null;
var $imageViewer = null;

cornerstoneWADOImageLoader.configure({
    beforeSend: function(xhr) {
        console.log('beforesend');
        // Add custom headers here (e.g. auth tokens)
        //xhr.setRequestHeader('x-auth-token', 'my auth token');
    }
});

var conerstoneloaded = false;

function dicomloadAndViewImage(imageId) {
    var element = $('#imageViewer').get(0);
    try {
        cornerstone.loadAndCacheImage(imageId).then(function(image) {
            console.log(image);
            var viewport = cornerstone.getDefaultViewportForImage(element, image);
            $('#toggleModalityLUT').attr("checked",viewport.modalityLUT !== undefined);
            $('#toggleVOILUT').attr("checked",viewport.voiLUT !== undefined);
            cornerstone.displayImage(element, image, viewport);
            if(conerstoneloaded === false) {
                cornerstoneTools.mouseInput.enable(element);
                cornerstoneTools.mouseWheelInput.enable(element);
                cornerstoneTools.wwwc.activate(element, 1); // ww/wc is the default tool for left mouse button
                cornerstoneTools.pan.activate(element, 2); // pan is the default tool for middle mouse button
                cornerstoneTools.zoom.activate(element, 4); // zoom is the default tool for right mouse button
                cornerstoneTools.zoomWheel.activate(element); // zoom is the default tool for middle mouse wheel
                conerstoneloaded = true;
            }
        }, function(err) {
            console.log(err);
            openModal(err, "DICOM Loading Failed");
        });
    }
    catch(err) {
        console.log(err);
        openModal(err, "DICOM Loading Failed");
    }
}

function downloadAndView(tagData)
{
    if(tagData['type'] == 'dcm') {
        var url = makeURL(tagData);
        console.log(url);

        // prefix the url with wadouri: so cornerstone can find the image loader
        //url = "wadouri:" + url;


        // image enable the dicomImage element and activate a few tools
        //dicomloadAndViewImage(url);
    }
}

function makeURL(tagData) {
    return SERVER_ADDRESS + '/api/archive?image_user_id=' + imageInfo['user_id']
        + '&image_id=' + imageInfo['image_id']
        + '&image_dir=' + tagData['dir'];
}

$(cornerstone).bind('CornerstoneImageLoadProgress', function(eventData) {
    console.log(eventData);
    console.log('Image Load Progress: ' + eventData.percentComplete + "%");
    $('#loadProgress').text('Image Load Progress: ' + eventData.percentComplete + "%");
});

$(document).ready(function() {
    var imageContainer = $('#imageViewer').get(0);
    cornerstone.enable(imageContainer);
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

        $('#image-view-list a').each(function(elem) {
            $(this).click(function() {
                //console.log($(this).data());
                downloadAndView($(this).data());
            });
        });

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

function setOpenImageViewerListener(elem) {
    $imageViewer = elem;
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
    $('#image-view-list a').each(function(elem) {
        $(this).unbind('click');
    });
    $imageViewer.unbind('click');
    imageDirs = null;
    setOpenImageViewerListener($imageViewer);
}