cornerstoneWADOImageLoader.external.cornerston = cornerstone;

var images = {};
var cur = 0;
var id = 0;
var max = 0;
var extension = 0;
var isPlay = false;
var isStopped = true;
var phase;
var cur_phase = "";
var cur_phase_id = 0;
var target_phases = {};
var keys = [];
var dcmImgIDs = {};

function formatDate(value){
  if(value){
    Number.prototype.padLeft = function(base,chr){
      var len = (String(base || 10).length - String(this).length)+1;
      return len > 0? new Array(len).join(chr || '0')+this : this;
    }
    var d = new Date(value),
    dformat = [ (d.getMonth()+1).padLeft(),
                 d.getDate().padLeft(),
                 d.getFullYear()].join('/')+
              ' ' +
              [ d.getHours().padLeft(),
                d.getMinutes().padLeft(),
                d.getSeconds().padLeft()].join(':');
    return dformat;
  }
}

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
function viewImage(c_p, id){
    const element = document.getElementById('main_viewer_dicom');
    var elems = document.querySelectorAll(".loader");
    [].forEach.call(document.querySelectorAll('.loader'), function (el) {
      el.style.visibility = 'hidden';
    });

    document.getElementById('txt_num').innerHTML = id+1;
    document.getElementById('txt_max_num').innerHTML = max;
    const viewport = cornerstone.getDefaultViewportForImage(element, images[keys[c_p]][(id+1).toString()]);
    // document.getElementById('toggleModalityLUT').checked = (viewport.modalityLUT !== undefined);
    // document.getElementById('toggleVOILUT').checked = (viewport.voiLUT !== undefined);
    cornerstone.displayImage(element, images[keys[0]]['1'], viewport);

    proto_name = images[keys[c_p]][(id+1).toString()].data.string('x00181030');
    if (proto_name !== undefined)
        document.getElementById('txt_protocol_name').innerHTML = proto_name;
    else
        document.getElementById("sp_proto_name").setAttribute("hidden", true);

    taken_date = images[keys[c_p]][(id+1).toString()].data.string('x00080022');
    taken_time = images[keys[c_p]][(id+1).toString()].data.string('x00080032');
    if (taken_date !== undefined)
        document.getElementById('txt_taken_date').innerHTML = get_date(taken_date, taken_time);
    else
        document.getElementById('txt_taken_date').innerHTML = "Not Recorded";

    // study_desc = images['1'].data.string('x00081030');
    // if (study_desc !== undefined)
    //     document.getElementById('txt_study_desc').innerHTML = study_desc;
    // else
    //     document.getElementById("sp_study_desc").setAttribute("hidden", true);
    //
    // series_desc = images['1'].data.string('x0008103E');
    // if (series_desc !== undefined)
    //     document.getElementById('txt_series_desc').innerHTML = series_desc;
    // else
    //     document.getElementById("sp_series_desc").setAttribute("hidden", true);

    pat_name = images[keys[c_p]][(id+1).toString()].data.string('x00100010');
    if (pat_name !== undefined)
        document.getElementById('txt_pat_name').innerHTML = pat_name;
    else
        document.getElementById('txt_pat_name').innerHTML= "Not Recorded";

    gender = images[keys[c_p]][(id+1).toString()].data.string('x00100040');
    if (gender !== undefined){
        if (gender === "F")
            document.getElementById('txt_pat_gender').innerHTML = "Female";
        else if (gender === "M")
            document.getElementById('txt_pat_gender').innerHTML = "Male";
    } else
            document.getElementById('txt_pat_gender').innerHTML= "Not Recorded";
    birth = images[keys[c_p]][(id+1).toString()].data.string('x00100030');
    if (birth !== undefined)
        document.getElementById('txt_pat_birthday').innerHTML = birth;
    else
        document.getElementById('txt_pat_birthday').innerHTML= "Not Recorded";
    age = images[keys[c_p]][(id+1).toString()].data.string('x00101010');
    if (age !== undefined)
        document.getElementById('txt_pat_age').innerHTML = get_age(age);
    else
        document.getElementById('txt_pat_age').innerHTML = "Not Recorded";
    slice_loc = images[keys[c_p]][(id+1).toString()].data.string('x00201041');
    if (slice_loc !== undefined)
        document.getElementById('txt_slice_loc').innerHTML = slice_loc;
    else
        document.getElementById('txt_slice_loc').innerHTML = "Not Recorded";

    document.getElementById("div_info").removeAttribute("hidden");
}
function loadAndViewImage(imageId, c_p) {
    cornerstone.loadImage(imageId).then(function(image) {
        instance_num = parseInt(image.data.string('x00200013'));    // To parse dicom image's instance number
        images[c_p][instance_num] = image;
        console.log(c_p, instance_num, cur, max);
        if(Object.keys(images[keys[0]]).length === max){
            viewImage(0,0);
        }
        if(loaded === false) {
            cornerstoneTools.init();
            const ZoomTool = cornerstoneTools.ZoomTool;
            const panTool = cornerstoneTools.PanTool;
            cornerstoneTools.addTool(panTool);
            cornerstoneTools.addTool(cornerstoneTools.ZoomMouseWheelTool, {
                configuration: {
                    invert: false,
                    preventZoomOutsideImage: false,
                    minScale: .1,
                    maxScale: 20.0,
                }
            });
            cornerstoneTools.setToolActive("Pan", {mouseButtonMask: 1})
            cornerstoneTools.setToolActive("ZoomMouseWheel", {mouseButtonMask: 4})
            // cornerstoneTools.mouseInput.enable(element);
            // cornerstoneTools.mouseWheelInput.enable(element);
            // cornerstoneTools.wwwc.activate(element, 1); // ww/wc is the default tool for left mouse button
            // cornerstoneTools.pan.activate(element, 2); // pan is the default tool for middle mouse button
            // cornerstoneTools.zoom.activate(element, 4); // zoom is the default tool for right mouse button
            // cornerstoneTools.zoomWheel.activate(element); // zoom is the default tool for middle mouse wheel

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
    // console.log(`Image Load Progress: ${eventData.percentComplete}%`);
    // loadProgress.textContent = `Image Load Progress: ${eventData.percentComplete}%`;
});

const element = document.getElementById('main_viewer_dicom');
cornerstone.enable(element);


function resizeCanvas(){
    var ele = document.getElementById("main_viewer_img");
    element.style.height = ele.clientHeight+"px";
    cornerstone.resize(element, true);
}

/// Jquery Part
(function () {

    $("body").on("click", ".thumb_img", function (){
        console.log($(this).attr("id"));
        cur_phase_id = $(this).attr("id").split("_")[1];
        cur = 0;
        if (extension === "dcm"){

        }else{
            load_image_info();
        }
    });

    $("#main_viewer_img").on('mousewheel DOMMouseScroll', function (e) {
        var E = e.originalEvent;
        var delta = 0;
        // if (E.detail){
        //     delta = E.detail*-40;
        //     if (delta<0){
        //         $("#main_viewer_img").width($("#main_viewer_img").width()/1.02)
        //         $("#main_viewer_img").height($("#main_viewer_img").height()/1.02)
        //     }else{
        //         $("#main_viewer_img").width($("#main_viewer_img").width()*1.02)
        //         $("#main_viewer_img").height($("#main_viewer_img").height()*1.02)
        //
        //     }
        // }else{
        //     delta = E.wheelDelta;
        //         console.log($("#main_viewer_img").width(), $("#main_viewer_img").height());
        //     if (delta<0){
        //         $("#main_viewer_img").width($("#main_viewer_img").width()/1.02);
        //         $("#main_viewer_img").height($("#main_viewer_img").height()/1.02);
        //     }else{
        //         $("#main_viewer_img").width($("#main_viewer_img").width()*1.02);
        //         $("#main_viewer_img").height($("#main_viewer_img").height()*1.02);
        //
        //     }
        // }
    });

    $(window).resize(function () {
        resizeCanvas();
    });

    function loadImg(loc, k){
        $.ajax({
            url: "/api/send_images",
            method: 'POST',
            async: false,
            data: JSON.stringify({
                "img_id": id,
                "img_loc": loc,
                "cur_phase":cur_phase
            }),
            success: function (data) {
                if (data !== undefined){
                    images[keys[k]].push(data);
                    if (loc === 0 || k === 0){
                        $("#thum_"+k).attr("src", "data:image/png;base64,"+images[keys[k]][0]);
                        $("#main_viewer_img").attr("src", "data:image/png;base64,"+images[keys[k]][0]);
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
        phase = $("#cur_phase").text();
        // $(window).on('load', function () {
        //     setTimeout(function () {
        //         $('.loader').hide();
        //     }, 3000);
        // });

        $.ajax({
           url: "/api/get_max_img_count",
           method: 'POST',
           async: true,
           data: JSON.stringify({
               "img_id": id,
               "cur_phase":phase
           }),
           success: function (data) {
               target_phases = data['data']['length'];
               keys = Object.keys(target_phases);
               max = target_phases[keys[0]];
               cur_phase = keys[0];
               cur_phase_id = 0;
               for (var k in keys){
                   $("#navigator").append("" +
                   "<h4 class='mx-2'>"+keys[k]+"</h4>"+
                   "<img id=\"thum_"+k+"\" class=\"mx-2 mt-1 mb-4 thumb_img\" height=\"260px\" width=\"260px\">");
               }

               $('#img_slider').attr('min', 0);
               $('#img_slider').attr('max', max-1);

               extension = data['data']['extension'];
               if (extension === "dcm"){
                   images = {};
                   $('#main_viewer_dicom').css('z-index', 100);
                   $('#main_viewer_img').css('z-index', 1);
                   console.log(cur_phase);
                   console.log(id, cur_phase);

                   keys = Object.keys(target_phases);
                   for (var k in keys){
                       images[keys[k]] = {};
                       max = target_phases[keys[k]];
                       cur_phase = keys[k];
                       console.log(cur_phase,images, max);
                       for(var i=0; i<max; i++){
                           url = "wadouri:" + "/api/send_dicom/"+id+"/"+cur_phase+"/"+i;
                           loadAndViewImage(url, cur_phase);
                       }
                   }
                   max = target_phases[keys[0]];
                   cur_phase = keys[0];
                   // load_image_info();
                   // remove_spinner();
                   // for (var i=0;i<max; i++){
                   //     url = "wadouri:" + "/api/send_dicom/"+id+"/"+cur_phase+"/"+i;
                   //     // image enable the dicomImage element and activate a few tools
                   //     loadAndViewImage(url);
                   // }

               }else{
                   $('#main_viewer_img').css('z-index', 100);
                   $('#main_viewer_dicom').css('z-index', 1);

                   keys = Object.keys(target_phases);
                   for (var k in keys){
                       images[keys[k]] = [];
                       max = target_phases[keys[k]];
                       cur_phase = keys[k];
                       for(var i=0; i<max; i++){
                           loadImg(i, k);
                       }
                   }

                   cur_phase_id = 0;
                   remove_spinner();
               }
               }, error: function (err) {
           }
        });
    });

    $("#btn-play_pause").on("click", function () {
        if (isPlay){    // already play (play -> pause)
            $("#img_play").css("display", "block");
            $("#img_pause").css("display", "none");
            isPlay = false;
        } else {        // pause (pause -> play)
            $("#img_play").css("display", "none");
            $("#img_pause").css("display", "block");
            isPlay = true;
            function play(){
                setTimeout(function () {
                    if(isPlay && cur < max-1){
                        console.log(isPlay);
                        cur = cur+1;
                        load_image_info();

                        play();
                    } else{
                        $("#img_play").css("display", "block");
                        $("#img_pause").css("display", "none");
                        isPlay = false;
                    }
                }, 300);
            }
            play();
        }
    });
    $("#btn-stop").on("click", function () {
        isPlay = false;
        console.log("bye");
        cur = 0;
        load_image_info();

    });

    $("#img_slider").on("input", function () {
        cur =  Number($('#img_slider').val());
        load_image_info();
        $('#txt_num').text(cur+1);
    });


    $("#btn-left").on("click", function () {
        if (cur-1<0){
            cur = 0;
        }else {
            cur -= 1;
        }
        load_image_info();
    });

    $("#btn-right").on("click", function () {
        if (cur < max-1){
            cur+= 1;
        } else{
            cur = max-1;
        }
        load_image_info();
    });

    $("#btn_img_info").on("click", function () {
        if(extension === "dcm"){
            var dicom_info = get_dicom_info();
            $("#modal_tb_body").empty();
            for (k in dicom_info){
                $("#modal_tb_body").append("<tr>" +
                    "<td>"+k+"</td>"+
                    "<td>"+dicom_info[k]+"</td>"+
                    "</tr>");
            }


            $('#modal_info').modal("show");
        }
    });

    $(document).keydown(function (event) {
        if (event.keyCode === 37){ // Left
            if (cur-1<0){
                cur = 0;
            }else {
                cur -= 1;
            }
            load_image_info();
        } else if(event.keyCode === 39){ // Right
            if (cur < max-1){
                cur+= 1;
            } else{
                cur = max-1;
            }
            load_image_info();
        }
    });

    function load_image_info() {
        $('#img_slider').val(cur);
        $("#txt_num").text(cur+1);
        if (extension === "dcm"){
            const viewport = cornerstone.getDefaultViewportForImage(element, images[cur_phase][cur+1]);
            // document.getElementById('toggleModalityLUT').checked = (viewport.modalityLUT !== undefined);
            // document.getElementById('toggleVOILUT').checked = (viewport.voiLUT !== undefined);
            cornerstone.displayImage(element, images[cur_phase][cur+1], viewport);
            var proto_name = images[cur_phase][cur+1].data.string('x00181030');
            var name = images[cur_phase][cur+1].data.string('x00100010');
            var gender = images[cur_phase][cur+1].data.string('x00100040');
            var birth = images[cur_phase][cur+1].data.string('x00100030');
            var age = images[cur_phase][cur+1].data.string('x00101010');
            var slc_loc = images[cur_phase][cur+1].data.string('x00201041');
            var taken_day = images[cur_phase][cur+1].data.string('x00080022');
            var taken_time = images[cur_phase][cur+1].data.string('x00080032');
            console.log(get_date(taken_day, taken_time));

            if (proto_name !== undefined)
                $('#txt_protocol_name').text(proto_name);
            else
                $("#txt_protocol_name").text("Not Recorded");
            if (name !== undefined)
                $('#txt_pat_name').text(name);
            else
                $("#txt_pat_name").text("Not Recorded");

            if (gender !== undefined){
                if (gender === "F"){
                    $('#txt_pat_gender').text("Female");
                }else {
                    $('#txt_pat_gender').text("Male");
                }
            }
            else
                $("#txt_pat_gender").text("Not Recorded");
            if (birth !== undefined)
                $('#txt_pat_birthday').text(birth);
            else
                $("#txt_pat_birthday").text("Not Recorded");
            if (age !== undefined)
                $('#txt_pat_age').text(get_age(age));
            else
                $("#txt_pat_age").text("Not Recorded");
            if (slc_loc !== undefined)
                $('#txt_slice_loc').text(slc_loc);
            else
                $("#txt_slice_loc").text("Not Recorded");

            if (taken_day !== undefined )
                $("#txt_taken_date").text(get_date(taken_day, taken_time));
            else
                $("#txt_taken_date").text("Not Recorded");
        }else
            $("#main_viewer_img").attr("src", "data:image/png;base64,"+images[keys[cur_phase_id]][cur]);

    }
    function remove_spinner(){
        $('.loader').hide(300);
    }
    function get_dicom_info(){
        result = {};
        result['Image Type'] = check_undefined(images[cur+1].data.string('x00080008'));
        result['Study Date'] = get_date(images[cur+1].data.string('x00080020'), images[cur+1].data.string('x00080030'));
        result['Series Date'] = get_date(images[cur+1].data.string('x00080021'), images[cur+1].data.string('x00080031'));
        result['Acquisition Date'] = get_date(images[cur+1].data.string('x00080022'), images[cur+1].data.string('x00080032'));
        result['Modality'] = check_undefined(images[cur+1].data.string('x00080060'));
        result['Study Description'] = check_undefined(images[cur+1].data.string('x00081030'));
        result['Series Description'] = check_undefined(images[cur+1].data.string('x0008103E'));
        result['Patient Name'] = check_undefined(images[cur+1].data.string('x00100010'));
        result['Patient Birth Date'] = check_undefined(images[cur+1].data.string('x00100030'));
        result['Patient Gender'] = get_gender(images[cur+1].data.string('x00100040'));
        result['Patient Age'] = get_age(images[cur+1].data.string('x00101010'));
        result['Body Part Examined'] = check_undefined(images[cur+1].data.string('x00180015'));
        result['Slice Thickness'] = check_undefined(images[cur+1].data.string('x00180050'));
        result['Protocol Name'] = check_undefined(images[cur+1].data.string('x00181030'));
        result['Rotation Direction'] = check_undefined(images[cur+1].data.string('x00181140'));
        result['Study ID'] = check_undefined(images[cur+1].data.string('x00200010'));
        result['Series Number'] = check_undefined(images[cur+1].data.string('x00200011'));
        result['Acquisition Number'] = check_undefined(images[cur+1].data.string('x00200012'));
        result['Instance Number'] = check_undefined(images[cur+1].data.string('x00200013'));
        result['Rows'] = check_undefined(images[cur+1].data.uint16('x00280010'));
        result['Columns'] = check_undefined(images[cur+1].data.uint16('x00280011'));
        result['Pixel Spacing'] = check_undefined(images[cur+1].data.string('x00280030'));

        return result;
    }
})(jQuery);

function check_undefined(d){
    if(d === undefined)
        return "";
    else
        return d;
}

function get_date(day, time) {
    if (day === undefined || time === undefined){
        return ""
    }
    try {
        var ld = day.split("");
        var lt = time.split("");
        return ld[4]+ld[5]+"/"+ld[6]+ld[7]+"/"+ld[0]+ld[1]+ld[2]+ld[3]+" "+lt[0]+lt[1]+":"+lt[2]+lt[3]+":"+lt[4]+lt[5];
    }catch (e) {
        return "";
    }
}

function get_gender(gender) {
    if (gender === "F"){
        return "Female";
    }else if(gender === "M") {
        return "Male";
    } else{
        return "";
    }
}

function get_age(a){
    try{
        var as = a.split('');
        if (as[0] === '0'){
            if (as[1] === '0')
                return as[2];
            else
                return as[1]+as[2]
        }else
            return as[0]+as[1]+as[2]
    } catch (e) {
        return "";
    }
}