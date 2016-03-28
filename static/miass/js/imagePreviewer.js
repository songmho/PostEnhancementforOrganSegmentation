/**
 * Created by hanter on 2016. 3. 18..
 */

function showThumbnail() {
    var imageContainer = $('#image-previewer').get(0);
    cornerstone.disable(imageContainer);

    $('#image-previewer').empty();

    var thumbnail = getThumbnailImage();
    if(thumbnail != null) {
        var url = makeURL(thumbnail);
        //console.log(url);
        //console.log(thumbnail['type']);
        setTimeout(function() {
            if (thumbnail['type'] == 'dcm') {
                cornerstone.enable(imageContainer);

                var wadoUrl = "wadouri:" + url;
                showDicomThumbnail(wadoUrl);
            } else if (thumbnail['type'] == 'csv') {
                showCsvThumbnail(url);
            } else {
                $('#image-previewer').append('<canvas></canvas>');
                showImageThumbnail(url);
            }
        });
    }
}

function showImageThumbnail(url) {
    var canvas = $('#image-previewer canvas');
    canvas.attr('width', $('#image-previewer').width())
          .attr('height', $('#image-previewer').height());
    canvas = canvas[0];
    var ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    console.log('image');

    var image = new Image();
    image.addEventListener("load", function() {
        var drawingWidth = image.width;
        var drawingHeight = image.height;
        var magni = 1;
        var widthMagni = 1, heightMagni = 1;

        widthMagni = canvas.width / image.width;
        heightMagni = canvas.height / image.height;

        if (widthMagni > heightMagni) magni = heightMagni;
        else magni = widthMagni;

        drawingWidth *= magni;
        drawingHeight *= magni;
        ctx.drawImage(image, 0, 0, drawingWidth, drawingHeight);
        //ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
    });
    image.src = url;
}

function showDicomThumbnail(url) {
    var element = $('#image-previewer').get(0);
    try {
        cornerstone.loadAndCacheImage(url).then(function(image) {
            //console.log(image);
            //console.log(element);
            var viewport = cornerstone.getDefaultViewportForImage(element, image);
            cornerstone.displayImage(element, image, viewport);
            cornerstoneTools.mouseInput.disable(element);
            cornerstoneTools.mouseWheelInput.disable(element);
        }, function(err) {
            console.log(err);
            openModal(err, "DICOM thumbnail Loading Failed");
        });
    }
    catch(err) {
        console.log(err);
        openModal(err, "DICOM thumbnail Loading Failed");
    }
    showImageViewerLoader(false);
}

function showCsvThumbnail(url) {
    smoothPlotter.smoothing = 0.2;
    var elem = document.getElementById("image-previewer");

    var g = new Dygraph(
        elem,
        url, {
            width: $('#image-previewer').width(),
            height: $('#image-previewer').height(),
            //valueRange: [-3, 5.1],
            axes: {
                y: {
                    drawAxis: false
                }, x: {
                    drawAxis: false,
                    drawGrid: false
                }
            },
            strokeWidth: 1,
            color: '#D76474',
            displayAnnotations: false,
            highlightCircleSize: 0,
            showLabelsOnHighlight: false,
            plotter: smoothPlotter,
            interactionModel: {}
        }
    );
}

function getThumbnailImage() {
    for (var rootName in imageDirs) {
        var rootImgInfo = imageDirs[rootName];

        if (rootImgInfo['type'] == 'folder') {
            for (var dirName in rootImgInfo['file_list']) {
                var dirs = rootImgInfo['file_list'][dirName];
                var firstImage = nextImageNotFolder(dirs, dirName);
                if (firstImage != null) return firstImage;
            }
        } else {
            return {
                type: rootImgInfo['type'],
                dir: rootImgInfo['dir'],
                name: imageInfo['subject']
            };
        }
        return null;
    }
}

function nextImageNotFolder(dirs, name) {
    if (dirs['type'] == 'folder') {
        var firstImage = null;
        var dirKeys = [];
        for (var dirkey in dirs['file_list']) {
            dirKeys.push(dirkey);
        }
        //if (dirKeys.length <= 0) return null;
        for (var i=0; i<dirKeys.length; i++) {
            var dirName = dirKeys[i];
            var childDirs = dirs['file_list'][dirName];
            firstImage = nextImageNotFolder(childDirs, dirName)
        }
        return firstImage;
    } else {
        return {
            type: dirs['type'],
            dir: dirs['dir'],
            name: name
        };
    }
}