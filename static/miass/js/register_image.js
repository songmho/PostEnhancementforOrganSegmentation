var is_uploaded= true;
var path = "";
var cur_img_type = "Normal";

(function () {
    // function getfolder(e) {
    //     var files = e.target.files;
    //     var path = files[0].webkitRelativePath;
    //     var Folder = path.split("/");
    //     alert("Files in " + Folder[0] + " are uploaded.")
    // }
    $(window).resize(function () {
        resizeCanvas();
    });

    $(function () {
        $("#txt_Birthday").datepicker({
            format: "yyyy-mm-dd",	//데이터 포맷 형식(yyyy : 년 mm : 월 dd : 일 )
                // startDate: '-10d',	//달력에서 선택 할 수 있는 가장 빠른 날짜. 이전으로는 선택 불가능 ( d : 일 m : 달 y : 년 w : 주)
                // endDate: '+10d',	//달력에서 선택 할 수 있는 가장 느린 날짜. 이후로 선택 불가 ( d : 일 m : 달 y : 년 w : 주)
                autoclose : true,	//사용자가 날짜를 클릭하면 자동 캘린더가 닫히는 옵션
                calendarWeeks : false, //캘린더 옆에 몇 주차인지 보여주는 옵션 기본값 false 보여주려면 true
                clearBtn : false, //날짜 선택한 값 초기화 해주는 버튼 보여주는 옵션 기본값 false 보여주려면 true
                // datesDisabled : ['2019-06-24','2019-06-26'],//선택 불가능한 일 설정 하는 배열 위에 있는 format 과 형식이 같아야함.
                // daysOfWeekDisabled : [0,6],	//선택 불가능한 요일 설정 0 : 일요일 ~ 6 : 토요일
                // daysOfWeekHighlighted : [3], //강조 되어야 하는 요일 설정
                disableTouchKeyboard : false,	//모바일에서 플러그인 작동 여부 기본값 false 가 작동 true가 작동 안함.
                immediateUpdates: true,	//사용자가 보는 화면으로 바로바로 날짜를 변경할지 여부 기본값 :false
                multidate : false, //여러 날짜 선택할 수 있게 하는 옵션 기본값 :false
                // multidateSeparator :",", //여러 날짜를 선택했을 때 사이에 나타나는 글짜 2019-05-01,2019-06-01
                templates : {
                    leftArrow: '&laquo;',
                    rightArrow: '&raquo;'
                }, //다음달 이전달로 넘어가는 화살표 모양 커스텀 마이징
                showWeekDays : true ,// 위에 요일 보여주는 옵션 기본값 : true
                // title: "테스트",	//캘린더 상단에 보여주는 타이틀
                todayHighlight : true ,	//오늘 날짜에 하이라이팅 기능 기본값 :false
                toggleActive : true,	//이미 선택된 날짜 선택하면 기본값 : false인경우 그대로 유지 true인 경우 날짜 삭제
                weekStart : 0 ,//달력 시작 요일 선택하는 것 기본값은 0인 일요일
                language : "ko"	//달력의 언어 선택, 그에 맞는 js로 교체해줘야한다.
        }).on("changeDate", function (e) {
            console.log("Selected Date: ", e);
        });
    });

    $(function () {
        $("#txt_acq_date").datepicker({
            format: "yyyy-mm-dd",	//데이터 포맷 형식(yyyy : 년 mm : 월 dd : 일 )
                // startDate: '-10d',	//달력에서 선택 할 수 있는 가장 빠른 날짜. 이전으로는 선택 불가능 ( d : 일 m : 달 y : 년 w : 주)
                // endDate: '+10d',	//달력에서 선택 할 수 있는 가장 느린 날짜. 이후로 선택 불가 ( d : 일 m : 달 y : 년 w : 주)
                autoclose : true,	//사용자가 날짜를 클릭하면 자동 캘린더가 닫히는 옵션
                calendarWeeks : false, //캘린더 옆에 몇 주차인지 보여주는 옵션 기본값 false 보여주려면 true
                clearBtn : false, //날짜 선택한 값 초기화 해주는 버튼 보여주는 옵션 기본값 false 보여주려면 true
                // datesDisabled : ['2019-06-24','2019-06-26'],//선택 불가능한 일 설정 하는 배열 위에 있는 format 과 형식이 같아야함.
                // daysOfWeekDisabled : [0,6],	//선택 불가능한 요일 설정 0 : 일요일 ~ 6 : 토요일
                // daysOfWeekHighlighted : [3], //강조 되어야 하는 요일 설정
                disableTouchKeyboard : false,	//모바일에서 플러그인 작동 여부 기본값 false 가 작동 true가 작동 안함.
                immediateUpdates: true,	//사용자가 보는 화면으로 바로바로 날짜를 변경할지 여부 기본값 :false
                multidate : false, //여러 날짜 선택할 수 있게 하는 옵션 기본값 :false
                // multidateSeparator :",", //여러 날짜를 선택했을 때 사이에 나타나는 글짜 2019-05-01,2019-06-01
                templates : {
                    leftArrow: '&laquo;',
                    rightArrow: '&raquo;'
                }, //다음달 이전달로 넘어가는 화살표 모양 커스텀 마이징
                showWeekDays : true ,// 위에 요일 보여주는 옵션 기본값 : true
                // title: "테스트",	//캘린더 상단에 보여주는 타이틀
                todayHighlight : true ,	//오늘 날짜에 하이라이팅 기능 기본값 :false
                toggleActive : true,	//이미 선택된 날짜 선택하면 기본값 : false인경우 그대로 유지 true인 경우 날짜 삭제
                weekStart : 0 ,//달력 시작 요일 선택하는 것 기본값은 0인 일요일
                language : "ko"	//달력의 언어 선택, 그에 맞는 js로 교체해줘야한다.
        }).on("changeDate", function (e) {
            console.log("Selected Date: ", e);
        });
    });

    $("#btn_reset").click(function () {
        $("#modal_cancel_reg_img").modal("show");
    });

    $("#btn_submit").click(function () {
        var fir_name = $("#txt_fir_name").val();
        var last_name = $("#txt_last_name").val();
        var birthday = $("#txt_Birthday").val();

        var gender = $('input:radio[name=rdo_gender]:checked').val();

        var acq_date = $("#txt_acq_date").val();
        var exam_src = $("#txt_exam_src").val();
        var interpretation = $("#txt_interpret").val();
        var description = $("#txt_desc").val();
        var img_type = $("#txt_img_type").val();

        var form_upload = $("#form_upload")[0];
        var file_data = new FormData(form_upload);

        if (gender === undefined){
            gender = "";
        }

        data = {"fir_name": fir_name, "last_name": last_name, "birthday": birthday, "gender": gender,
            "acquisition_date": acq_date, "examination_source":exam_src, "interpretation":interpretation,
            "description": description, 'uploader_id':get_current_user()['identification_number'], "img_type":img_type}

        file_data.append("data", JSON.stringify(data))

        if (img_type==="" || img_type===null) {
            $("#txt_img_type").addClass("is-invalid");
        } if (fir_name==="") {
            $("#txt_fir_name").addClass("is-invalid");
        } if (last_name === "") {
            $("#txt_last_name").addClass("is-invalid");
        } if (acq_date==="") {
            $("#txt_acq_date").addClass("is-invalid");
        } if (exam_src==="" ) {
            $("#txt_exam_src").addClass("is-invalid");
        }else{
            $.ajax({
                type:"POST",
                enctype: 'multipart/form-data',
                url: '/api/upload/',
                data: file_data,
                processData: false,
                contentType: false,
                cache: false,
                timeout: 600000,
                async: false,
                success: function (data) {
                    if(data['state']){
                        console.log(data['state']);
                        $("#modal_body").text("Upload is finished");
                        $("#modal_reg_img").modal("show");
                        // location.reload();
                    }else{
                        $("#modal_body").text("Uploading files is fail.");
                        $("#modal_reg_img").modal("show");
                        is_uploaded = false;

                    }
                }, error: function (err) {
                    $("#modal_body").text("Uploading files is fail.");
                    $("#modal_reg_img").modal("show");
                    is_uploaded = false;
                }
            });

        }
    });

    $('#btn_yes').click(function () {
        if(is_uploaded){
            location.reload();
        }
        location.reload();
    })

    $("#btn_cancel_yes").click(function () {
        location.reload();
    });

    $("#btn_cancel_no").click(function () {
        $("#modal_cancel_reg_img").modal("hide");
    });

    $('#btn_img_loader').on('change', function (e) {
        var fileList = this.files;
        var fileReader = new FileReader();
        var fileName = e.target.files[0];
        $('#img_slider').attr('min', 0);
        $('#img_slider').attr('max', fileList.length-1);
        $('#txt_max_num').text(fileList.length);
        $('#txt_num').text(1);

        if ($('#btn_img_loader').prop('files')[0]["name"].split(".")[1] === "dcm"){
            cur_img_type = "DCM";
            console.log("DCM");
            // $('#img_preview').css('display', "none");
            // $('#img_dicom').css('display', "block");
            $('#img_preview').css('z-index', 1);
            $('#img_dicom').css('z-index', 100);
            // $('#img_preview').attr("src", fileReader.result);
            setDicomImage($('#btn_img_loader').prop('files')[0]);
            $('#img_slider').val(0);
        } else{
            cur_img_type = "Normal";
            console.log("Normal");
            // $('#img_preview').css('display', "block");
            // $('#img_dicom').css('display', "none");
            $('#img_preview').css('z-index', 100);
            $('#img_dicom').css('z-index', 1);
            console.log("name: ", $('#btn_img_loader').prop('files'));
            fileReader.readAsDataURL($('#btn_img_loader').prop('files')[0]);
            fileReader.onload = function () {
                $('#img_preview').attr("src", fileReader.result);
            };
            $('#img_slider').val(0);
        }
    });

    $('#img_slider').on("input", function () {
        var fileReader = new FileReader();
        if(cur_img_type === "DCM"){
            setDicomImage($('#btn_img_loader').prop('files')[$('#img_slider').val()]);
        } else{
            fileReader.readAsDataURL($('#btn_img_loader').prop('files')[$('#img_slider').val()]);
            fileReader.onload = function () {
                $('#img_preview').attr("src",fileReader.result);
            };
        }

        var num = Number($('#img_slider').val())+1;
        $('#txt_num').text(num);
    });

    $(document).ready(function () {
        resizeCanvas();
        var cur_r = get_current_role();
        var cur_u = get_current_user();
        if (cur_r === "Patient"){
            $("#txt_fir_name").val(cur_u['first_name']);
            $("#txt_last_name").val(cur_u['last_name']);
            $("#txt_Birthday").val(cur_u['birthday']);
            var g = cur_u['gender'];
            if (g === "Male"){
                $('#rdo_male').attr('checked', true);
                $('#rdo_female').attr('checked', false);
            }else{
                $('#rdo_male').attr('checked', false);
                $('#rdo_female').attr('checked', true);
            }
        }
    });

})(jQuery);

cornerstoneWADOImageLoader.external.cornerston = cornerstone;

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


const main_view = document.getElementById('img_dicom');
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
    const element = document.getElementById('img_dicom');
    const start = new Date().getTime();
    cornerstone.loadImage(imageId).then(function(image) {
        console.log(image);
        const viewport = cornerstone.getDefaultViewportForImage(element, image);
        // document.getElementById('toggleModalityLUT').checked = (viewport.modalityLUT !== undefined);
        // document.getElementById('toggleVOILUT').checked = (viewport.voiLUT !== undefined);
        cornerstone.displayImage(element, image, viewport);
        if(loaded === false) {
            cornerstoneTools.mouseInput.enable(element);
            cornerstoneTools.mouseWheelInput.enable(element);
            cornerstoneTools.wwwc.activate(element, 1); // ww/wc is the default tool for left mouse button
            cornerstoneTools.pan.activate(element, 2); // pan is the default tool for middle mouse button
            cornerstoneTools.zoom.activate(element, 4); // zoom is the default tool for right mouse button
            cornerstoneTools.zoomWheel.activate(element); // zoom is the default tool for middle mouse wheel

            cornerstoneTools.imageStats.enable(element);        // Code for displaying information
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
    const loadProgress = document.getElementById('loadProgress');
    loadProgress.textContent = `Image Load Progress: ${eventData.percentComplete}%`;
});

const element = document.getElementById('img_dicom');
cornerstone.enable(element);

function setDicomImage(file){
    const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(file);
    console.log("Image ID: ", cornerstoneWADOImageLoader.wadouri.fileManager.get(imageId));
    console.log("Image ID: ", cornerstoneWADOImageLoader.wadouri.fileManager);
    console.log("Image ID: ", imageId);

    loadAndViewImage(imageId);

}

function resizeCanvas(){
    var ele = document.getElementById("img_preview");
    element.style.height = ele.clientWidth+"px";
    console.log(element.clientWidth, element.style.width)
    cornerstone.resize(element, true);
}
// document.getElementById('btn_img_loader').addEventListener('change', function(e) {
//     // Add the file to the cornerstoneFileImageLoader and get unique
//     // number for that file
//     const file = e.target.files[0];
//     console.log("file: ", file)
//     const imageId = cornerstoneWADOImageLoader.wadouri.fileManager.add(file);
//     console.log("Image ID: ", cornerstoneWADOImageLoader.wadouri.fileManager.get(imageId));
//     console.log("Image ID: ", cornerstoneWADOImageLoader.wadouri.fileManager);
//     console.log("Image ID: ", imageId);
//
//     loadAndViewImage(imageId);
// });