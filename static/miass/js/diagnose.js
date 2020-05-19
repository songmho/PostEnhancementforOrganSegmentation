cornerstoneWADOImageLoader.external.cornerston = cornerstone;

var images = {};
var cur = 0;
var id = 0;
var max = 0;
var extension = 0;

function handleFileSelect(evt) {
    evt.stopPropagation();
    evt.preventDefault();

    // Get the FileList object that contains the list of files that were dropped
    const files = evt.dataTransfer.files;

    // this UI is only built for a single file so just dump the first one
    file = files[0];
    const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(file);
    loadAndViewImage(imageId);
}

function handleDragOver(evt) {
    evt.stopPropagation();
    evt.preventDefault();
    evt.dataTransfer.dropEffect = 'copy'; // Explicitly show this is a copy.
}


const main_view = document.getElementById('main_viewer_dicom');
main_view.addEventListener('dragover', handleDragOver, false);
main_view.addEventListener('drop', handleFileSelect, false);


cornerstoneWADOImageLoader.configure({
    beforeSend: function(xhr) {
        // Add custom headers here (e.g. auth tokens)
        //xhr.setRequestHeader('x-auth-token', 'my auth token');
    },
    useWebWorkers: true,
});

let loaded = false;
function loadAndViewImage(imageId) {
    const element = document.getElementById('main_viewer_dicom');
    const start = new Date().getTime();
    cornerstone.loadImage(imageId).then(function(image) {
        instance_num = parseInt(image.data.string('x00200013'));    // To parse dicom image's instance number
        images[instance_num] = image;
        if (Object.keys(images).length === 1){
            const viewport = cornerstone.getDefaultViewportForImage(element, image);
            // document.getElementById('toggleModalityLUT').checked = (viewport.modalityLUT !== undefined);
            // document.getElementById('toggleVOILUT').checked = (viewport.voiLUT !== undefined);
            cornerstone.displayImage(element, image, viewport);
            document.getElementById('txt_num').innerHTML = cur+1;
            document.getElementById('txt_max_num').innerHTML = max;
            const preview = document.getElementById('thum_1_dicom');
            const viewport_preview = cornerstone.getDefaultViewportForImage(preview, image);
            cornerstone.displayImage(preview, image, viewport_preview);

        }
        if(loaded === false) {
            cornerstoneTools.mouseInput.enable(element);
            cornerstoneTools.mouseWheelInput.enable(element);
            cornerstoneTools.wwwc.activate(element, 1); // ww/wc is the default tool for left mouse button
            cornerstoneTools.pan.activate(element, 2); // pan is the default tool for middle mouse button
            cornerstoneTools.zoom.activate(element, 4); // zoom is the default tool for right mouse button
            cornerstoneTools.zoomWheel.activate(element); // zoom is the default tool for middle mouse wheel

            // cornerstoneTools.imageStats.enable(element);
            loaded = true;
        }

        function getTransferSyntax() {
            const value = image.data.string('x00020010');
            return value + ' [' + uids[value] + ']';
        }

        function getSopClass() {
            const value = image.data.string('x00080016');
            return value + ' [' + uids[value] + ']';
        }

        function getPixelRepresentation() {
            const value = image.data.uint16('x00280103');
            if(value === undefined) {
                return;
            }
            return value + (value === 0 ? ' (unsigned)' : ' (signed)');
        }

        function getPlanarConfiguration() {
            const value = image.data.uint16('x00280006');
            if(value === undefined) {
                return;
            }
            return value + (value === 0 ? ' (pixel)' : ' (plane)');
        }

        // document.getElementById('transferSyntax').textContent = getTransferSyntax();
        // document.getElementById('sopClass').textContent = getSopClass();
        // document.getElementById('samplesPerPixel').textContent = image.data.uint16('x00280002');
        // document.getElementById('photometricInterpretation').textContent = image.data.string('x00280004');
        // document.getElementById('numberOfFrames').textContent = image.data.string('x00280008');
        // document.getElementById('planarConfiguration').textContent = getPlanarConfiguration();
        // document.getElementById('rows').textContent = image.data.uint16('x00280010');
        // document.getElementById('columns').textContent = image.data.uint16('x00280011');
        // document.getElementById('pixelSpacing').textContent = image.data.string('x00280030');
        // document.getElementById('bitsAllocated').textContent = image.data.uint16('x00280100');
        // document.getElementById('bitsStored').textContent = image.data.uint16('x00280101');
        // document.getElementById('highBit').textContent = image.data.uint16('x00280102');
        // document.getElementById('pixelRepresentation').textContent = getPixelRepresentation();
        // document.getElementById('windowCenter').textContent = image.data.string('x00281050');
        // document.getElementById('windowWidth').textContent = image.data.string('x00281051');
        // document.getElementById('rescaleIntercept').textContent = image.data.string('x00281052');
        // document.getElementById('rescaleSlope').textContent = image.data.string('x00281053');
        // document.getElementById('basicOffsetTable').textContent = image.data.elements.x7fe00010 && image.data.elements.x7fe00010.basicOffsetTable ? image.data.elements.x7fe00010.basicOffsetTable.length : '';
        // document.getElementById('fragments').textContent = image.data.elements.x7fe00010 && image.data.elements.x7fe00010.fragments ? image.data.elements.x7fe00010.fragments.length : '';
        // document.getElementById('minStoredPixelValue').textContent = image.minPixelValue;
        // document.getElementById('maxStoredPixelValue').textContent = image.maxPixelValue;
        // const end = new Date().getTime();
        // const time = end - start;
        // document.getElementById('totalTime').textContent = time + "ms";
        // document.getElementById('loadTime').textContent = image.loadTimeInMS + "ms";
        // document.getElementById('decodeTime').textContent = image.decodeTimeInMS + "ms";

    }, function(err) {
        alert(err);
    });
}

cornerstone.events.addEventListener('cornerstoneimageloadprogress', function(event) {
    const eventData = event.detail;
    // const loadProgress = document.getElementById('loadProgress');
    console.log(`Image Load Progress: ${eventData.percentComplete}%`);
    // loadProgress.textContent = `Image Load Progress: ${eventData.percentComplete}%`;
});

const element = document.getElementById('main_viewer_dicom');
cornerstone.enable(element);


function resizeCanvas(){
    var ele = document.getElementById("main_viewer_img");
    element.style.height = ele.clientWidth+"px";
    console.log(element.clientWidth, element.style.width)
    cornerstone.resize(element, true);
}

/// Jquery Part
(function () {

    $(window).resize(function () {
        resizeCanvas();
    });

    function loadImg(loc){
        $.ajax({
            url: "/api/send_images",
            method: 'POST',
            async: false,
            data: JSON.stringify({
                "img_id": id,
                "img_loc": loc
            }),
            success: function (data) {
                if (data !== undefined){
                    console.log(data);
                    images.push(data);
                    if (loc === 0){
                        $("#thum_1").attr("src", "data:image/png;base64,"+images[0]);
                        $("#main_viewer_img").attr("src", "data:image/png;base64,"+images[0]);
                        $("#txt_num").text(cur+1);
                        $("#txt_max_num").text(max);
                    }
                }
                }, error: function (err) {

            }
        });
    }
    $(document).ready(function () {
        resizeCanvas();
        id = $("#cur_id").text();

        $.ajax({
           url: "/api/get_max_img_count",
           method: 'POST',
           async: true,
           data: JSON.stringify({
               "img_id": id,
           }),
           success: function (data) {
                max = data['data']['length'];
                extension = data['data']['extension'];
                if (extension === "dcm"){
                    images = {};
                    $('#main_viewer_dicom').css('z-index', 100);
                    $('#main_viewer_img').css('z-index', 1);
                    for (var i=0;i<max; i++){
                        url = "wadouri:" + "/api/send_dicom/"+id+"/"+i;
                        // image enable the dicomImage element and activate a few tools
                        loadAndViewImage(url);
                    }
                }else{
                    images = [];
                    $('#main_viewer_img').css('z-index', 100);
                    $('#main_viewer_dicom').css('z-index', 1);
                    for(var i=0; i<max; i++){
                        loadImg(i);
                    }
                }
                }, error: function (err) {

           }
        });
    });
    $("#btn-left").on("click", function () {
        if (cur-1<0){
            cur = 0;
        }else {
            cur -= 1;
        }

        $("#txt_num").text(cur+1);
        if (extension === "dcm"){
            const viewport = cornerstone.getDefaultViewportForImage(element, images[cur]);
            // document.getElementById('toggleModalityLUT').checked = (viewport.modalityLUT !== undefined);
            // document.getElementById('toggleVOILUT').checked = (viewport.voiLUT !== undefined);
            cornerstone.displayImage(element, images[cur], viewport);
        }else
            $("#main_viewer_img").attr("src", "data:image/png;base64,"+images[cur]);

    });

    $("#btn-right").on("click", function () {
        if (cur < max-1){
            cur+= 1;
        } else{
            cur = max-1;
        }
        $("#txt_num").text(cur+1);
        if (extension === "dcm"){
            const viewport = cornerstone.getDefaultViewportForImage(element, images[cur]);
            // document.getElementById('toggleModalityLUT').checked = (viewport.modalityLUT !== undefined);
            // document.getElementById('toggleVOILUT').checked = (viewport.voiLUT !== undefined);
            cornerstone.displayImage(element, images[cur], viewport);
        }else
            $("#main_viewer_img").attr("src", "data:image/png;base64,"+images[cur]);

    });

    $(document).keydown(function (event) {
        if (event.keyCode === 37){ // Left
            if (cur-1<0){
                cur = 0;
            }else {
                cur -= 1;
            }

            $("#txt_num").text(cur+1);
            if (extension === "dcm"){
                const viewport = cornerstone.getDefaultViewportForImage(element, images[cur]);
                // document.getElementById('toggleModalityLUT').checked = (viewport.modalityLUT !== undefined);
                // document.getElementById('toggleVOILUT').checked = (viewport.voiLUT !== undefined);
                cornerstone.displayImage(element, images[cur], viewport);
            }else
                $("#main_viewer_img").attr("src", "data:image/png;base64,"+images[cur]);
        } else if(event.keyCode === 39){ // Right
            if (cur < max-1){
                cur+= 1;
            } else{
                cur = max-1;
            }
            $("#txt_num").text(cur+1);
            if (extension === "dcm"){
                const viewport = cornerstone.getDefaultViewportForImage(element, images[cur]);
                // document.getElementById('toggleModalityLUT').checked = (viewport.modalityLUT !== undefined);
                // document.getElementById('toggleVOILUT').checked = (viewport.voiLUT !== undefined);
                cornerstone.displayImage(element, images[cur], viewport);
            }else
                $("#main_viewer_img").attr("src", "data:image/png;base64,"+images[cur]);
        }
        console.log("Current Image Location: ", cur,"(",images.length,")"," Max Image Number: ", max, "Event: ", event.keyCode, images[cur]['imageId']);
    });
})(jQuery);
