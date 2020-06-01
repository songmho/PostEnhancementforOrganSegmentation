var isWithdrawed = false;

(function () {
    $(function () {
        $("#txt_birthday").datepicker({
            format: "dd/mm/yyyy",	//데이터 포맷 형식(yyyy : 년 mm : 월 dd : 일 )
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
                todayHighlight : false ,	//오늘 날짜에 하이라이팅 기능 기본값 :false
                toggleActive : true,	//이미 선택된 날짜 선택하면 기본값 : false인경우 그대로 유지 true인 경우 날짜 삭제
                weekStart : 0 ,//달력 시작 요일 선택하는 것 기본값은 0인 일요일
                language : "ko"	//달력의 언어 선택, 그에 맞는 js로 교체해줘야한다.
        }).on("changeDate", function (e) {
        });
    });

    $('#btn_change_pwd').on("click", function () {
        $('#txt_crr_pwd').removeClass("is-invalid");
        $('#txt_pwd').removeClass("is-invalid");
        $('#txt_pwd_check').removeClass("is-invalid");
        $('#txt_chk_crr_pwd').prop("hidden", true);
        $('#txt_chk_pwd').prop("hidden", true);
        $('#txt_chk_pwd_re').prop("hidden", true);
        $("#txt_crr_pwd").val('');
        $("#txt_pwd").val('');
        $("#txt_pwd_check").val('');
        $("#modal_change_pwd").modal("show");
    });

    $("#btn_withdraw").on("click", function () {

        $("#modal_withdraw").modal("show");
    });
    $('#btn_no_withdraw').on("click", function () {
        $("#modal_withdraw").modal("hide");
    });

    $('#btn_checked_notice').on("click", function () {
        if(isWithdrawed){
            $("#modal_update_notice").modal("hide");
            location.replace("/main")
        } else{
            $("#modal_update_notice").modal("hide");

        }
    });

    $('#btn_yes_withdraw').on("click", function () {
        $("#modal_withdraw").modal("hide");
        $("#modal_notice").modal("show");
        // logout
        // remove user
        $.ajax({
           url: "/api/withdraw",
           method: 'POST',
           async: true,
           data: JSON.stringify({
               "id": get_current_user()["identification_number"],
           }),
           success: function(data){
               isWithdrawed = data['state'];
               console.log(isWithdrawed);
               if (isWithdrawed){
                    remove_current_user();
                    remove_remember();
                   $('#modal_text_notice').text("Your account is removed.");
               }else{
                   $('#modal_text_notice').text("Your account is not removed.");

               }
           }, error: function (err) {
               console.log(err);
               $('#modal_text_notice').text("Your account is not removed.");

           }
        });
    });


    $("#btn_change_no").on("click", function () {
        $("#modal_change_pwd").modal("hide");
        $('#txt_crr_pwd').removeClass("is-invalid");
        $('#txt_pwd').removeClass("is-invalid");
        $('#txt_pwd_check').removeClass("is-invalid");
        $('#txt_chk_crr_pwd').prop("hidden", true);
        $('#txt_chk_pwd').prop("hidden", true);
        $('#txt_chk_pwd_re').prop("hidden", true);
        $("#txt_crr_pwd").val('');
        $("#txt_pwd").val('');
        $("#txt_pwd_check").val('');
    });

    $("#btn_change_yes").on("click", function () {
        var cur_pwd = $("#txt_crr_pwd").val();
        var changed_pwd = $("#txt_pwd").val();
        var changed_pwd_re = $("#txt_pwd_check").val();
        var isPossible = true;
        $('#txt_crr_pwd').removeClass("is-invalid");
        $('#txt_pwd').removeClass("is-invalid");
        $('#txt_pwd_check').removeClass("is-invalid");

        $('#txt_chk_crr_pwd').prop("hidden", true);
        $('#txt_chk_pwd').prop("hidden", true);
        $('#txt_chk_pwd_re').prop("hidden", true);

        if (cur_pwd === undefined || cur_pwd === ""){
            isPossible = false;
            $('#txt_crr_pwd').addClass("is-invalid");
            $('#txt_chk_crr_pwd').prop("hidden", false);

        } if (changed_pwd === undefined || changed_pwd === ""){
            isPossible = false;
            $('#txt_pwd').addClass("is-invalid");
            $('#txt_chk_pwd').prop("hidden", false);

        } if (changed_pwd_re === undefined || changed_pwd_re === ""){
            isPossible = false;
            $('#txt_pwd_check').addClass("is-invalid");
            $('#txt_chk_pwd_re').prop("hidden", false);
        }

        if (cur_pwd !== get_current_user()['pwd']){
            isPossible = false;
            $('#txt_crr_pwd').addClass("is-invalid");
            $('#txt_chk_crr_pwd').prop("hidden", false);

        } if (changed_pwd !== changed_pwd_re){
            isPossible = false;
            $('#txt_pwd').addClass("is-invalid");
            $('#txt_pwd_check').addClass("is-invalid");
            $('#txt_chk_pwd').prop("hidden", false);
            $('#txt_chk_pwd_re').prop("hidden", false);

        }

        if (isPossible){
            // change password
            $.ajax({
               url: "/api/change_pwd",
               method: 'POST',
               async: true,
               data: JSON.stringify({
                   "id": get_current_user()["identification_number"],
                   "target_pwd": $("#txt_pwd").val(),
               }),
               success: function(data){
                   var isChanged = data['state'];
                   if (isChanged){
                        var curUser = get_current_user();
                        curUser['pwd'] = $("#txt_pwd").val();
                        console.log(curUser);
                        set_current_user(curUser);
                        $('#modal_change_pwd').modal("hide");
                   }else{

                   }
               }, error: function (err) {
                   console.log(err);

               }
            });
        }

    });


    $('#btn_cancel').on("click", function () {
        // Need to check
        window.history.back();
    });

    $('#btn_apply').on("click", function () {
        // General Information
        var first_name = $('#txt_first_name').val();
        var last_name = $('#txt_last_name').val();
        var gender = $('input:radio[name=rdo_gender]:checked').val();
        if (gender === undefined)
            gender = "";
        var birthday = $("#txt_birthday").val();
        if (birthday === undefined || birthday === "")
            birthday = null;
        var phone = $("#txt_phone").val();

        var isPosible = true;
        console.log(first_name, last_name, gender, birthday, phone);
        if(isPosible){
            $.ajax({
               url: "/api/modify_general_info",
               method: 'POST',
               async: true,
               data: JSON.stringify({
                   "id": get_current_user()["identification_number"],
                   "first_name": first_name,
                   "last_name": last_name,
                   "gender": gender,
                   "birthday": birthday,
                   "phone": phone,
               }),
               success: function(data){
                   var isChanged = data['state'];
                   if (isChanged){
                        var curUser = data['data'];
                        console.log(curUser);
                        set_current_user(curUser[0]);
                        $('#modal_change_pwd').modal("hide");
                        $("#modal_text_notice").text("Information is updated successfully.")
                        $("#modal_update_notice").modal("show");
                   }else{
                        $("#modal_text_notice").text("Updating information is Failed. Try again.")
                        $("#modal_update_notice").modal("show");

                   }
               }, error: function (err) {
                   console.log(err);

               }
            });
        }
    });

    $("#btn_checked_notice").on("click", function () {
        $("#modal_notice").modal("hide");
    });

    function loadProfileImage(){
        $.ajax({
            url: "/api/send_profile",
            method: 'POST',
            async: false,
            data: JSON.stringify({
                "id": get_current_user()['identification_number'],
            }),
            success: function (data) {
                console.log(">>> ", data);
                if (data !== undefined){
                    console.log(data);
                    $("#img_chng_default").css("display", "none");
                    $('#img_chng_profile').css("display", "block");
                    $("#img_chng_profile").attr("src", "data:image/png;base64,"+data);
                    set_current_profile(data);
                    location.reload()
                }
                }, error: function (err) {

            }
            });
        }

    $(document).ready(function () {

        if (get_current_profile() != "None" && get_current_profile() !==null){
            $("#img_chng_default").css("display", "none");
            $('#img_chng_profile').css("display", "block");
            $('#img_chng_profile').attr("src", "data:image/png;base64,"+get_current_profile());
        } else{
            $('#img_chng_profile').css("display", "none");
            $("#img_chng_default").css("display", "block");
        }
        // var hasProfile = true;
        // console.log(hasProfile);

        var cur_user_data = get_current_user();
        console.log(cur_user_data);
        $("#txt_first_name").val(cur_user_data['first_name']);
        $("#txt_last_name").val(cur_user_data['last_name']);
        if (cur_user_data["gender"]==="Male"){
            $("#rdo_male").prop('checked', true);
            console.log("Hi");
        }
        else if(cur_user_data["gender"]==="Female")
            $("#rdo_female").prop('checked', true);

        $("#txt_phone").val(cur_user_data['phone_number']);
        $("#txt_user_role").text(cur_user_data['role']);

        var birthday = cur_user_data['birthday'];
        try{
            if (birthday === undefined || birthday === "" || birthday=== null)
                $("#txt_birthday").val("");
            else
                $("#txt_birthday").val(changeDateFormat(cur_user_data['birthday']));
        } catch (e) {
            $("#txt_birthday").val("");
        }
    });

    $('#btn_select_profile_img').on("click", function () {

        var fileToUpload = $('#btn_select_profile_img').prop('files');
    });

    $("#btn_select_profile_img").on("change", function (e) {
        var selectedProfile = null;
        var fileList = this.files;
        var fileReader = new FileReader();
        var fileName = e.target.files[0];

        fileReader.readAsDataURL($('#btn_select_profile_img').prop('files')[0]);
        fileReader.onload = function () {
            $('#img_chng_profile').attr("src", fileReader.result);
            selectedProfile = fileReader.result;

            var form_profile = $('#form_upload')[0];
            var file_data = new FormData(form_profile);
            var data = {"id":get_current_user()["identification_number"]};
            file_data.append("data", JSON.stringify(data));

            $.ajax({
                type:"POST",
                enctype: 'multipart/form-data',
                url: '/api/register_profile_image/',
                data: file_data,
                processData: false,
                contentType: false,
                cache: false,
                timeout: 600000,
                async: false,
                success: function (data) {
                    if(data['state']){
                        $("#modal_body").text("Upload is finished");
                        $("#modal_reg_img").modal("show");
                        loadProfileImage();
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
        // console.log(selectedProfile)
        // if (selectedProfile !== null){
        //     $.ajax({
        //         type:"POST",
        //         enctype: 'multipart/form-data',
        //         url: '/api/register_profile_image/',
        //         data: selectedProfile,
        //         processData: false,
        //         contentType: false,
        //         cache: false,
        //         timeout: 600000,
        //         async: false,
        //         success: function (data) {
        //             if(data['state']){
        //                 $("#modal_body").text("Upload is finished");
        //                 $("#modal_reg_img").modal("show");
        //                 // location.reload();
        //             }else{
        //                 $("#modal_body").text("Uploading files is fail.");
        //                 $("#modal_reg_img").modal("show");
        //                 is_uploaded = false;
        //
        //             }
        //         }, error: function (err) {
        //             $("#modal_body").text("Uploading files is fail.");
        //             $("#modal_reg_img").modal("show");
        //             is_uploaded = false;
        //         }
        //     });
        // }


    });

    $('#btn_remove_profile').on("click", function () {
        $.ajax({
            url: "/api/remove_profile",
            method: 'POST',
            async: false,
            data: JSON.stringify({
                "id": get_current_user()['identification_number'],
            }),
            success: function (data) {
                if (data['state']) {
                    $('#img_chng_profile').css("display", "none");
                    $('#img_chng_default').css("display", "block");
                    remove_current_profile();
                    location.reload()
                }
                }, error: function (err) {

                }
            });



    });
})(jQuery);

function changeDateFormat(str){
    var dateStr = str.split(" ");
    dateStr = dateStr[0].split("-");
    var yyyy = dateStr[0];
    var mm = dateStr[1];
    var dd = dateStr[2];

    return dd+"/"+(mm)+"/"+yyyy;

}