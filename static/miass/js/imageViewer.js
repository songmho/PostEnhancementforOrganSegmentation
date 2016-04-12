/**
 * Created by hanter on 2016. 3. 12..
 */

var graphColors = ['#D76474', '#ADD764', '#8E64D7', '#64D7C7', '#607D8B', '#FFD600',
                   '#1493CC', '#3F51B5', '#FF5722', '#2196F3', '#009688', '#795548'];

var imageDirs = null;
var $imageViewer = null;
var lastImageData = null;
var canvasSize = 512;
var chartWidth = 1100;
var bShowGraphView = false;

cornerstoneWADOImageLoader.configure({
    beforeSend: function(xhr) {
        //console.log('beforesend');
        // Add custom headers here (e.g. auth tokens)
        //xhr.setRequestHeader('x-auth-token', 'my auth token');
        showImageViewerLoader(true);
    }
});

var conerstoneloaded = false;

function dicomReadHeader(wadoURL) {
    $('#imageViewShowDetail').text('Detail Information Loading...')
                .unbind('click').off('click');

    var oReq = new XMLHttpRequest();
    try {
        oReq.open("get", wadoURL, true);
    } catch(err) {
        $('#imageViewShowDetail').text('Detail Information Loading Failed');
        console.log(err);
        return false;
    }

    oReq.responseType = "arraybuffer";
    oReq.onreadystatechange = function(oEvent) {
        if(oReq.readyState == 4) {
            if(oReq.status == 200) {
                var byteArray = new Uint8Array(oReq.response);

                var kb = byteArray.length / 1024;
                var mb = kb / 1024;
                var byteStr = mb > 1 ? mb.toFixed(3) + " MB" : kb.toFixed(0) + " KB";
                //document.getElementById('statusText').innerHTML = 'Status: Parsing ' + byteStr + ' bytes, please wait..';
                console.log('Status: Parsing ' + byteStr + ' bytes, please wait..');
                // set a short timeout to do the parse so the DOM has time to update itself with the above message
                setTimeout(function() {
                    // Invoke the paresDicom function and get back a DataSet object with the contents
                    var dataSet;
                    try {
                        dataSet = dicomParser.parseDicom(byteArray);
                        dicomShowDataSet(dataSet);
                        $('#imageViewShowDetail').hide();

                    } catch (err) {
                        $('#imageViewShowDetail').text('Detail Information Loading Failed');
                        console.log(err);
                    }
                }, 30);

            } else {
                $('#imageViewShowDetail').text('Detail Information Loading Failed');
                console.log(oEvent);
            }
        }
    };
    oReq.send();
}

function dicomShowDataSet(dataSet) {
    $('#imageViewerDetail span[data-dicom]').each(function(index, value) {
        var attr = $(value).attr('data-dicom');
        var element = dataSet.elements[attr];
        var text = "";
        if(element !== undefined)
        {
            var str = dataSet.string(attr);
            if(str !== undefined) {
                text = str;
            }
        }
        $(value).text(text);
    });

    $('#imageViewerDetail span[data-dicomUint]').each(function(index, value) {
        var attr = $(value).attr('data-dicomUint');
        var element = dataSet.elements[attr];
        var text = "";
        if(element !== undefined)
        {
            if(element.length === 2)
            {
                text += dataSet.uint16(attr);
            }
            else if(element.length === 4)
            {
                text += dataSet.uint32(attr);
            }
        }

        $(value).text(text);
    });

    $('#imageViewerDetail').show();
}

function dicomloadAndView(dicomURL) {

    // prefix the url with wadouri: so cornerstone can find the image loader
    var wadoURI = "wadouri:" + dicomURL;

    var element = $('#imageViewer').get(0);
    showImageViewerLoader(true);
    try {
        cornerstone.loadAndCacheImage(wadoURI).then(function(image) {
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

            //$('#imageViewerDetail').hide();
            //$('#imageViewShowDetail').text('Show Detail Information').show()
            //        .unbind('click').off('click').click(function() {
            //    dicomReadHeader(dicomURL);
            //});
            $('#imageViewShowDetail').text('Loading Detail Information...').show();
            dicomReadHeader(dicomURL);

            console.log('dicom loaded');
            showImageViewerLoader(false);

        }, function(err) {
            console.log(err);
            showImageViewerLoader(false);
            openModal(err, "DICOM Loading Failed");
        });
    }
    catch(err) {
        console.log(err);
        showImageViewerLoader(false);
        openModal(err, "DICOM Loading Failed");
    }
}

function generalImageLoadAndView(imageURL) {
    var canvas = $('#imageViewer canvas')[0];
    var ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    var image = new Image();

    showImageViewerLoader(true);
    image.addEventListener("load", function () {
        //var canvasSize = canvas.width;
        var drawingWidth = image.width;
        var drawingHeight = image.height;
        var magni = 1;
        if (canvasSize >= image.height) {
            var magni = canvasSize/image.width;
        } else {
            var magni = canvasSize/image.height;
        }
        drawingWidth *= magni;
        drawingHeight *= magni;
        ctx.drawImage(image, 0, 0, drawingWidth, drawingHeight);
        showImageViewerLoader(false);
    });
    image.src = imageURL;
}

var graph = null;
function csvGrpahLoadAndView(csvURL) {
    showImageViewerLoader(true);
    setTimeout(function() {
        var data = csvURL;
        smoothPlotter.smoothing = 0.333;

        var elem = null;
        if(bShowGraphView) elem = document.getElementById("graphViewer");
        else elem = document.getElementById("imageViewer");

        var g = new Dygraph (
            elem,
            data, {
                //labels: [ "Time", "Direct_1", "Abdomen_1"],
                width: chartWidth,
                height: canvasSize,
                //valueRange: [-3, 5.1],
                axes: {
                    y: {
                        drawAxis: true
                    }, x: {
                        drawAxis: true,
                        drawGrid: true
                    }
                },
                animatedZooms: true,
                strokeWidth: 2,
                //color: '#D76474',
                colors: graphColors,
                plotter: smoothPlotter,
                ylabel: 'Micro Volt (μV)',
                xlabel: 'Time (ms)'


                //visibility: [true, true, true, false, false, false],
                //drawCallback: function(g) {
                //    console.log(g.getLabels());
                //}
            }
        );
        g.ready(function(g) {
            console.log(g.getLabels());
            var lables = g.getLabels();

            var timeLable = lables[0];
            if(timeLable.length != 0 && !/^[\s]*$/.test(timeLable) && timeLable.trim().toLowerCase() != 'time') {
                $('#graphView .dygraph-xlabel').text(timeLable);
            }

            if (lables.length > 2) {
                var startLabel = 1;
                if (lables.length > 3 && lables[1].trim().toLowerCase().startsWith('time')) {
                    startLabel = 2;
                    g.setVisibility(0, false);
                }

                $('#graphLabelChecks').show();
                var checkboxesHTMLString = "";
                for (var i = startLabel; i < lables.length; i++) {
                    checkboxesHTMLString += '<div class="checkbox"><label style="color:'
                        + graphColors[i - 1] + ';"><input type="checkbox" data-column="' + (i - 1)
                        + '"> ' + lables[i] + '</label></div>'
                }
                //checkboxesHTMLString += '<button id="columnChangeBtn" class="btn btn-primary">Show</button>';
                $('#graphLabelChecks').empty().html(checkboxesHTMLString);
                $('#graphLabelChecks input:checkbox').prop('checked', true).change(function () {
                    var pos = parseInt($(this).data('column'));
                    g.setVisibility(pos, $(this).prop('checked'));
                });

                //$('#columnChangeBtn').off('click').unbind('click').click(function() {
                //    var labelCnt = lables.length-1;
                //    var arrVisibility = new Array(labelCnt);
                //    $('#graphLabelChecks input:checkbox').each(function() {
                //        var pos = parseInt($(this).data('column'));
                //        arrVisibility[pos] = $(this).prop('checked');
                //        g.setVisibility(pos, $(this).prop('checked'));
                //    });
                //    //g.setVisibility(arrVisibility);
                //});
            } else {
                $('#graphLabelChecks').hide();
            }
        });

        $('#rollPeriodConfirm').off('click');
        $('#rollPeriodConfirm').click(function() {
            var roll = $('#rollPeriod').val();
            if(roll < 0) {
                roll = 0;
                $('#rollPeriod').val(0);
            }
            g.adjustRoll(roll);
        });

        showImageViewerLoader(false);
    }, 10);
}

function showViewExploerer(bShow) {
    if(bShow == undefined || bShow == null) bShow = true;

    if(bShow) {
        $('.image-view-explorer').show();
        $('.image-view-image').removeClass('col-sm-12')
            .addClass('col-sm-7').addClass('col-md-8');
    } else {
        $('.image-view-explorer').hide();
        $('.image-view-image').removeClass('col-sm-7').removeClass('col-md-8')
            .addClass('col-sm-12');
    }
}


function showGraphView(bShow) {
    if(bShow == undefined || bShow == null) bShow = true;
    bShowGraphView = bShow;

    if(bShow) {
        $('#imageView').hide();
        $('#graphView').show();
    } else {
        $('#graphView').hide();
        $('#imageView').show();
    }
}

function downloadAndView(tagData)
{
    lastImageData = tagData;
    var url = makeURL(tagData);
    if(tagData['type'] == 'dcm') {
        // image enable the dicomImage element and activate a few tools
        dicomloadAndView(url);
        $('#imageViewModalTitleName').text(tagData['name']);
        //showImageViewerLoader(false);
    } else if (tagData['type'] == 'csv') {
        csvGrpahLoadAndView(url);
    } else {
        generalImageLoadAndView(url);
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
    $('#rollPeriodLabel').popover();

    resizeViewer();
    window.addEventListener("resize", resizeViewer);

    showImageViewerLoader(false);
    $('#imageViewModal').on('show.bs.modal', function(e) {
        resizeViewer();

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

        if(bShowGraphView) {
            $('#graphViewer').empty();
            for (var rootName in imageDirs) {
                var rootImgInfo = imageDirs[rootName];

                if (rootImgInfo['type'] == 'csv') {
                    lastImageData = {
                        type: rootImgInfo['type'],
                        dir: rootImgInfo['dir'],
                        name: imageInfo['subject']
                    };
                    console.log(lastImageData);
                }
                break;
            }
        } else {
            var listExplorer = $('#image-view-list');
            listExplorer.empty();
            for (var rootName in imageDirs) {
                var rootImgInfo = imageDirs[rootName];

                if (rootImgInfo['type'] == 'folder') {
                    for (var dirName in rootImgInfo['file_list']) {
                        var dirs = rootImgInfo['file_list'][dirName];
                        listExplorer.append('<li>' + generateExplorer(dirs, dirName) + '</li>');
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

            $('#image-view-list a').each(function (elem) {
                $(this).off('click');
                $(this).click(function () {
                    //console.log($(this).data());
                    var imageData = $(this).data();
                    imageData['name'] = $(this).text();
                    downloadAndView(imageData);
                });
            });
        }

        console.log('image view modal opened');
        $.LoadingOverlay('hide');
        $('#imageViewModal').modal({backdrop: 'static'});
    }, 0);
}

function generateExplorer(dirs, name) {
    if (dirs['type'] == 'folder') {
        var htmlString = '<span>'+name+'</span><ul>';
        //for (var dirName in dirs['file_list']) {
        //var childDirs = dirs['file_list'][dirName];
        var dirKeys = [];
        for (var dirkey in dirs['file_list']) {
            dirKeys.push(dirkey);
        }
        dirKeys.sort();
        for (var i=0; i<dirKeys.length; i++) {
            var dirName = dirKeys[i];
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
    //console.log('set listener');
    //$('#imageViewer').empty();
    //console.log(imageInfo);
    //console.log(imageInfo['image_dir'].endsWith('.csv'));

    if(imageInfo['image_dir'].endsWith('.csv')) {
        showGraphView();
    //} else if(imageInfo['image_dir'].endsWith('.jpg') ||
    //          imageInfo['image_dir'].endsWith('.jpeg') ||
    //          imageInfo['image_dir'].endsWith('.png')){
    //    $('#imageViewer').append('<canvas></canvas>');
    } else {
        showGraphView(false);
        //var imageContainer = $('#imageViewer').get(0);
        //cornerstone.enable(imageContainer);
    }

    $imageViewer = elem;
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
                    imageDirs = res['image_list'];
                    $imageViewer.click(function() {
                        openImageViewer();
                    });
                    showThumbnail();
                } else {
                    openModal(res['msg'], "Image Loading Failed");
                }
            }
        });
    }
}

function resizeViewer() {
    //console.log($(window).width() + ', ' + $(window).height())
    var windowWidth = $(window).width();
    canvasSize = 512;
    chartWidth = 1100;
    if (windowWidth < 768) {
        canvasSize = 320;
        chartWidth = windowWidth;
    } else if (windowWidth < 992) {
        canvasSize = 360;
        chartWidth = 680;
    } else if (windowWidth < 1200) {
        canvasSize = 512;
        chartWidth = 900;
    }

    if(bShowGraphView) {
        var sizeStyle = {width: chartWidth + 'px', height: canvasSize + 'px'};
        $('#graphViewer').css(sizeStyle);
        $('#graphViewer').attr('width', chartWidth).attr('height', canvasSize);
    } else {
        var sizeStyle = {width: canvasSize + 'px', height: canvasSize + 'px'};
        //console.log(sizeStyle);
        $('#imageViewerWrapper').attr('width', canvasSize).attr('height', canvasSize).css(sizeStyle);
        $('#imageViewer').attr('width', canvasSize).attr('height', canvasSize).css(sizeStyle);
        //$('#imageViewer').attr('style', "width:"+canvasSize+"px; height:+"+canvasSize+"px; position:relative; color:white;");
        $('#imageViewerLoader').attr('width', canvasSize).attr('height', canvasSize).css(sizeStyle);
        $('#imageViewer canvas').attr('width', canvasSize).attr('height', canvasSize).css(sizeStyle);
    }
}

function showImageViewerLoader(bShow) {
    if(bShow) $('#imageViewerLoader').show();
    else $('#imageViewerLoader').hide();
}

function resetViewer() {
    $('#image-view-list a').each(function(elem) {
        $(this).off('click');
    });
    $imageViewer.off('click');
    imageDirs = null;
    lastImageData = null;
    showImageViewerLoader(false);
    $('#imageViewModalTitleName').text('');
    var imageContainer = $('#imageViewer').get(0);
    //cornerstone.disable(imageContainer);
    //$('#imageViewer').unbind('mousemove');
    //$('#imageViewer').unbind('mousedown');

    //console.log('reset view');
    setOpenImageViewerListener($imageViewer);
}