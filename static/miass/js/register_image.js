var is_uploaded= false;
var path = "";
(function () {
    // function getfolder(e) {
    //     var files = e.target.files;
    //     var path = files[0].webkitRelativePath;
    //     var Folder = path.split("/");
    //     alert("Files in " + Folder[0] + " are uploaded.")
    // }
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
        console.log(birthday, acq_date, img_type);
        if (img_type==="" || fir_name==="" || last_name === "" || acq_date==="" || exam_src==="" ) {
        $("#txt_fir_name").addClass("is-invalid");
        $("#txt_last_name").addClass("is-invalid");
        $("#txt_img_type").addClass("is-invalid");
        $("#txt_acq_date").addClass("is-invalid");
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
                        is_uploaded = true;
                        path= data['path'];
                    }else{
                        is_uploaded = false;

                    }
                }, error: function (err) {
                        is_uploaded = false;

                }
            });

            if (is_uploaded){
                $.ajax({
                    type:"POST",
                    url: '/api/upload_txt/',
                    data: JSON.stringify({"fir_name": fir_name, "last_name": last_name, "birthday": birthday,
                        "gender": gender, "img_path":path, "acquisition_date": acq_date, "examination_source":exam_src, "interpretation":interpretation,
                        "description": description, 'uploader_id':1, "img_type":img_type}),
                    async: false,
                    success: function (data) {
                        if(data['state']){
                            location.reload();
                        }else{
                        }
                    },
                    error: function (e) {
                    }
                });
            }

        }


    });

    // $("#image_folder").
    $('#btn_img_loader').on('change', function (e) {
        var fileList = this.files;
        var fileReader = new FileReader();
        var fileName = e.target.files[0];
        $('#img_slider').attr('min', 0);
        $('#img_slider').attr('max', fileList.length-1);
        $('#txt_max_num').text(fileList.length);
        $('#txt_num').text(1);


        console.log("name: ", $('#btn_img_loader').prop('files'));
        fileReader.readAsDataURL($('#btn_img_loader').prop('files')[0]);
        fileReader.onload = function () {
            $('#img_preview').attr("src", fileReader.result);
        };
    });

    $('#img_slider').on("input", function () {
        var fileReader = new FileReader();
        fileReader.readAsDataURL($('#btn_img_loader').prop('files')[$('#img_slider').val()]);
        fileReader.onload = function () {
            $('#img_preview').attr("src",fileReader.result);
        };
        var num = Number($('#img_slider').val())+1;
        $('#txt_num').text(num);
    });

    $(document).ready(function () {
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

