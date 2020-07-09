var is_sign = false;
(function () {
    $(function () {
        $("#txt_birthday").datepicker({
            format: "yyyy/mm/dd",	//데이터 포맷 형식(yyyy : 년 mm : 월 dd : 일 )
            // format: "dd/mm/yyyy",	//데이터 포맷 형식(yyyy : 년 mm : 월 dd : 일 )
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
        });
    });

    $("#slct_role").on("change", function () {
        var value = $(this).val();
        console.log(value);
        $("#div_patient_info").css("display", "none");
        $("#div_physician_info").css("display", "none");

        $("#div_staff_info").css("display", "none");
        $("#div_"+value.toLowerCase()+"_info").css("display", "block");
    });

    $("#btn_sign_up").click(function () {
        $("#txt_chk_gen").prop("hidden", true);
        $('#txt_chk_fir_name').prop("hidden", true);
        $('#txt_chk_last_name').prop("hidden", true);
        $('#txt_chk_pwd').prop("hidden", true);
        $('#txt_chk_pwd_re').prop("hidden", true);
        $('#txt_chk_email').prop("hidden", true);
        $('#txt_chk_role').prop("hidden", true);

        $('#txt_first_name').removeClass("is-invalid");
        $('#txt_last_name').removeClass("is-invalid");
        $('#txt_email').removeClass("is-invalid");
        $('#txt_pwd').removeClass("is-invalid");
        $('#txt_pwd_check').removeClass("is-invalid");
        $('#txt_phone').removeClass("is-invalid");
        // $("#txt_role").removeClass("is-invalid");
        $('input[name="signup_role"]').removeClass("is-invalid");
        var is_possible = true;
        var fir_name = $("#txt_first_name").val();
        var last_name = $("#txt_last_name").val();
        var email = $("#txt_email").val();
        var pwd = $("#txt_pwd").val();
        var pwd_check = $("#txt_pwd_check").val();
        var phone = $("#txt_phone").val();

        var gender = $('input:radio[name=rdo_gender]:checked').val();
        var txt_birthday = $('#txt_birthday').val();
        var role = $("#slct_role").val();
        var role_data = {};
        if (role==="Patient"){  // if selected role is s
            role_data = {};
            role_data["blood_type"] = $("#slct_pat_blood_type").val();
            role_data["height"] = $("#txt_pat_height").val();
            role_data["weight"] = $("#txt_pat_weight").val();
        } else if (role==="Physician"){
            role_data = {};
            role_data["affiliation"] = $("#txt_phy_affiliation").val();
            role_data["license_number"] = $("#txt_phy_license_number").val();
            role_data["major"] = $("#txt_phy_major").val();

        } else if (role === "Staff"){
            role_data = {};
            role_data["affiliation"] = $("#txt_saf_affiliation").val();
        }else {

        }

        if (fir_name === ""){
            is_possible = false;
            $('#txt_first_name').addClass("is-invalid");
            $('#txt_chk_fir_name').text("Enter first name.");
            $('#txt_chk_fir_name').prop("hidden", false);
        } if (last_name === ""){
            is_possible = false;
            $('#txt_last_name').addClass("is-invalid");
            $('#txt_chk_last_name').text("Enter last name.");
            $('#txt_chk_last_name').prop("hidden", false);
        } if (email === ""){
            is_possible = false;
            $('#txt_email').addClass("is-invalid");
            $('#txt_chk_email').text("Enter email.");
            $('#txt_chk_email').prop("hidden", false);
        } if (pwd === ""){
            is_possible = false;
            $('#txt_pwd').addClass("is-invalid");
            $('#txt_chk_pwd').text("Enter password.");
            $('#txt_chk_pwd').prop("hidden", false);
        } if (pwd_check === ""){
            is_possible = false;
            $('#txt_pwd_check').addClass("is-invalid");
            $('#txt_chk_pwd_re').text("Enter password.");
            $('#txt_chk_pwd_re').prop("hidden", false);
        } if (role === "" || role===null){
            is_possible = false;
            $("#slct_role").addClass("is-invalid");
            $('#txt_chk_role').prop("hidden", false);
        } if (pwd !== pwd_check && pwd_check !== ""){
            is_possible = false;
            $('#txt_pwd').addClass("is-invalid");
            $('#txt_pwd_check').addClass("is-invalid");
            $('#txt_chk_pwd_re').text("Check password.");
            $('#txt_chk_pwd_re').prop("hidden", false);
            $('#txt_chk_pwd').text("Check password.");
            $('#txt_chk_pwd').prop("hidden", false);
        } if (gender === "" || gender===undefined){
            is_possible = false;
            $("#txt_chk_gen").prop("hidden", false);
        }


        if (is_possible){
            $('#btn_sign_up').prop("hidden", true);
            $('#btn_loading').prop("hidden", false);
            role = [role];
            $.ajax({
                url: "/api/sign_up",
                method: 'POST',
                async: true,
                data: JSON.stringify({
                    "first_name": fir_name,
                    "last_name": last_name,
                    "email": email,
                    "phone_number": phone,
                    "pwd": pwd,
                    "role": role,
                    "active": 0,
                    "gender":gender,
                    "birthday":txt_birthday,
                    "role_data":role_data,
                }),
                success: function (data) {
                    is_sign = data['state'];

                    if(data['state']){
                        $("#modal_signup_text").text(data['data']);
                        $("#modal_signup").modal('show');
                        $('#btn_loading').prop("hidden", true);
                        $('#btn_sign_up').prop("hidden", false);
                    }else{
                        $("#modal_signup_text").text(data['data']);
                        $("#modal_signup").modal('show');
                        $('#btn_loading').prop("hidden", true);
                        $('#btn_sign_up').prop("hidden", false);
                    }
                }, error: function (err) {
                }
            });

        }
    });

    $("#btn_yes").on('click', function () {
        if (is_sign){
            location.replace(SERVER_ADDRESS+"/main");
        }
        else{
            $("#modal_signup").modal('hide');
        }

    });

})(jQuery);