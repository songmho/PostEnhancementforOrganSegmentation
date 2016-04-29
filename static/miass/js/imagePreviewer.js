/**
 * Created by hanter on 2016. 3. 18..
 */

var thumbnailWidth = $('#image-previewer').width();
var thumbnailHeight = $('#image-previewer').height();   //278px

function initThumbnail() {
    $('#image-previewer-image').empty();
    var imageContainer = $('#image-previewer-image').get(0);
    cornerstone.enable(imageContainer);
    showThumbnail();
}

function showThumbnail() {
    //console.log('showThumbnail');

    $('body').css('overflow', 'hidden');
    var windowWidth = $(window).width();
    $('body').css('overflow', 'auto');

    //console.log('windowWidth:'+windowWidth);
    if (windowWidth <= 768) {
        thumbnailWidth = $('body').width() - 92;
    } else if (windowWidth < 992) {
        thumbnailWidth = 486;
    } else if (windowWidth < 1200) {
        thumbnailWidth = 394;
    } else {
        thumbnailWidth = 492;
    }
    var style = {width: thumbnailWidth+'px', height: thumbnailHeight+'px'};
    $('#image-previewer, #image-previewer .medimage-previewer, #image-previewer .medimage-previewer canvas')
        .attr('width', thumbnailWidth).attr('height', thumbnailHeight).css(style);

    var thumbnail = getThumbnailImage();
    //lastImageData = thumbnail;

    console.log(thumbnail);
    if(thumbnail != null) {
        var url = makeURL(thumbnail['dir']);
        console.log(url);
        //console.log(thumbnail['type']);
        setTimeout(function() {
            if (thumbnail['type'] == 'dcm') {
                $('#image-previewer-graph').hide();
                $('#image-previewer-image').show();
                var wadoUrl = "wadouri:" + url;
                showDicomThumbnail(wadoUrl);
            } else if (thumbnail['type'] == 'csv') {
                $('#image-previewer-image').hide();
                $('#image-previewer-graph').show();
                showCsvThumbnail(url);
            } else {
                $('#image-previewer-graph').hide();
                $('#image-previewer-image').show();
                showImageThumbnail(url);
            }
        }, 10);
    }
}

function showImageThumbnail(url) {
    var canvas = $('#image-previewer-image canvas');
    //canvas.attr('width', $('#image-previewer-image').width())
    //      .attr('height', $('#image-previewer-image').height());
    canvas = canvas[0];
    var ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    //console.log('image');

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
    //console.log(url);
    var element = $('#image-previewer-image').get(0);
    //$('#image-previewer-image').empty();
    //cornerstone.enable(element);
    try {
        cornerstone.loadAndCacheImage(url).then(function(image) {
            //console.log(image);
            //console.log(element);
            var viewport = cornerstone.getDefaultViewportForImage(element, image);
            cornerstone.displayImage(element, image, viewport);
            cornerstone.updateImage(element);
            //cornerstoneTools.mouseInput.disable(element);
            //cornerstoneTools.mouseWheelInput.disable(element);
            //cornerstoneTools.wwwc.disable(element);
            //cornerstoneTools.pan.disable(element);
            //cornerstoneTools.zoom.disable(element);
            //cornerstoneTools.zoomWheel.disable(element);
        }, function(err) {
            console.log(err);
            openModal(err, "DICOM thumbnail Loading Failed");
        });
    }
    catch(err) {
        console.log(err);
        openModal(err, "DICOM thumbnail Loading Failed");
    }
}

function showCsvThumbnail(url) {
    smoothPlotter.smoothing = 0.2;
    var elem = document.getElementById("image-previewer-graph");

    var g = new Dygraph(
        elem,
        url, {
            width: thumbnailWidth,
            height: thumbnailHeight,
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
    g.ready(function(g) {
            //console.log(g.getLabels());
            var lables = g.getLabels();

            if (lables.length > 2) {
                if (lables.length > 3 && lables[1].trim().toLowerCase().startsWith('time')) {
                    g.setVisibility(0, false);
                }
            }
        });
}

function getThumbnailImage() {
    for (var rootName in imageDirs) {
        var rootImgInfo = imageDirs[rootName];

        if (rootImgInfo['type'] == 'folder') {
            var rootDirKeys = [];
            for (var rootdirkey in rootImgInfo['file_list']) {
                rootDirKeys.push(rootdirkey);
            }
            rootDirKeys.sort(cmpStringsWithNumbers);
            //console.log(rootDirKeys);

            for (var i = 0; i < rootDirKeys.length; i++) {
                var dirs = rootImgInfo['file_list'][rootDirKeys[i]];
                var firstImage = nextImageNotFolder(dirs, rootDirKeys[i]);
                if (firstImage != null) return firstImage;
            }

        } else {
            var subject = imageInfo['subject'];
            if (subject == undefined) {
                subject = imageInfo['image_subject'];
            }

            return {
                type: rootImgInfo['type'],
                dir: rootImgInfo['dir'],
                name: subject
            };
        }
        return null;
    }
}

function nextImageNotFolder(dirs, name) {
    //console.log(dirs);

    if (dirs['type'] == 'folder') {
        var firstImage = null;
        var dirKeys = [];
        for (var dirkey in dirs['file_list']) {
            dirKeys.push(dirkey);
        }
        dirKeys.sort(cmpStringsWithNumbers);

        //if (dirKeys.length <= 0) return null;
        for (var i=0; i<dirKeys.length; i++) {
            var dirName = dirKeys[i];
            var childDirs = dirs['file_list'][dirName];
            firstImage = nextImageNotFolder(childDirs, dirName);
            if (firstImage != null) return firstImage;
        }
    } else {
        return {
            type: dirs['type'],
            dir: dirs['dir'],
            name: name
        };
    }
}