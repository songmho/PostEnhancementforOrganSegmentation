/**
 * Created by hanter on 2016. 3. 12..
 */

var imageDirs = null;
var $imageViewer = null;
var lastImageData = null;

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
    lastImageData = tagData;
    if(tagData['type'] == 'dcm') {
        var url = makeURL(tagData);

        // prefix the url with wadouri: so cornerstone can find the image loader
        url = "wadouri:" + url;

        // image enable the dicomImage element and activate a few tools
        dicomloadAndViewImage(url);
        $('#imageViewModalTitleName').text(tagData['name']);
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
    resizeViewer();
    window.addEventListener("resize", resizeViewer);

    $('#imageViewModal').on('show.bs.modal', function(e) {
        resizeViewer();
        console.log('image view modal opened');

        if (lastImageData != null) {
            downloadAndView(lastImageData);
        }
    });

    var imageContainer = $('#imageViewer').get(0);
    cornerstone.enable(imageContainer);
});

function openImageViewer() {
    $.LoadingOverlay('show');

    setTimeout(function() {
        resizeViewer();

        var listExplorer = $('#image-view-list');
        listExplorer.empty();
        for (var rootName in imageDirs) {
            var rootImgInfo = imageDirs[rootName];

            if (rootImgInfo['type'] == 'folder') {
                for (var dirName in rootImgInfo['file_list']) {
                    var dirs = rootImgInfo['file_list'][dirName];
                    listExplorer.append('<li>'+generateExplorer(dirs, dirName)+'</li>');
                }
            } else {
                listExplorer.append('<span><a data-dir="' + rootImgInfo['dir']
                    + '" data-type="' + rootImgInfo['type'] + '">'
                    + imageInfo['subject'] + '<a/></span>');
                lastImageData = {
                    type: rootImgInfo['type'],
                    dir: rootImgInfo['dir'],
                    name: imageInfo['subject']
                };
            }
            break;
        }

        $('#image-view-list a').each(function(elem) {
            $(this).off('click');
            $(this).click(function() {
                //console.log($(this).data());
                var imageData = $(this).data();
                imageData['name'] = $(this).text();
                downloadAndView(imageData);
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
    console.log('set listener');
    $imageViewer = elem;
    $imageViewer.click(function() {
        if (imageDirs == null) {
            $.LoadingOverlay('show');
            $.ajax("/api/medical_image", {
                method: 'GET',
                data: {
                    action: 'getImageDirs',
                    user_id: user['user_id'],
                    image_id: imageInfo['image_id'],
                    image_dir: imageInfo['image_dir']
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

function resizeViewer() {
    //console.log($(window).width() + ', ' + $(window).height())
    var windowWidth = $(window).width();
    var size = 512;
    if (windowWidth < 768) {
        size = 320;
    } else if (windowWidth < 992) {
        size = 360;
    } else {
        size = 512;
    }
    var sizeStyle = {width: size+'px', height: size+'px'};
    $('#imageViewer').css(sizeStyle);
    $('#imageViewer canvas').attr('width',size).attr('height',size).css(sizeStyle);
}

function resetViewer() {
    $('#image-view-list a').each(function(elem) {
        $(this).off('click');
    });
    $imageViewer.off('click');
    imageDirs = null;
    lastImageData = null;
    $('#imageViewModalTitleName').text('');
    //console.log('reset view');
    setOpenImageViewerListener($imageViewer);
}