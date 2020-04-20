var current_user_info;
(function () {
    // if (get_current_user() !== null){
    //     s_data = get_current_user();
    //     openWindowWithPost('.', {
    //         'first_name': s_data['first_name'],
    //         'last_name': s_data['last_name'],
    //         'email': s_data['email'],
    //         'cur_role':s_data['role'],
    //         'identification_number': s_data['identification_number'],
    //     });
    // }
    var cur_id_num = -1;

    function openWindowWithPost(url, data) {
        $('#form_sending_data').empty();
        var form = $('#form_sending_data').get(0);
        form.target = "_self";
        // form.target = "_blank";
        form.method = "POST";
        form.action = url;
        form.style.display = "none";

        for (var key in data) {
            var label = document.createElement("label");
            label.type = "hidden";
            label.htmlFor = "id_" + key;
            var input = document.createElement("input");
            input.type = "hidden";
            input.setAttribute('id', 'id_' + key);
            input.name = key;
            input.value = data[key];
            console.log(data, input);
            form.appendChild(input);
        }
        form.submit();
    }

    $('#btn_signin').click(function () {
        $("#txt_role_err").attr("hidden",true);
        $("#txt_acc_err").attr("hidden",true);
        $('#modal_login').modal();
        $('#modal_login').on('shown.bs.modal', function () {
            $('#btn_sign_in').click(function () {
                state = true;
                if($("#input_sign_in_id").val()===""){
                    state = false;
                    $("#input_sign_in_id").addClass("is-invalid");
                } if($("#input_sign_in_pwd").val()==="") {
                    state = false;
                    $("#input_sign_in_pwd").addClass("is-invalid");
               }
                if (state) {
                    login();
                }
            });
        });
    });
    $("#input_sign_in_id").keydown(function (key) {
        if(key.keyCode==13){
            if($("#input_sign_in_id").val()===""){
                $("#input_sign_in_id").addClass("is-invalid");
            }else{
                $("#input_sign_in_id").removeClass("is-invalid");
                $("#input_sign_in_pwd").focus();
            }
        }
    })
    $("#input_sign_in_pwd").keydown(function (key) {
       if(key.keyCode == 13){   //Enter key
           if($("#input_sign_in_pwd").val()===""){
                $("#input_sign_in_pwd").addClass("is-invalid");
           }else{
               $("#input_sign_in_pwd").removeClass("is-invalid");
               login();
           }
       }
    });

    $("#btn_check_code").click(function () {
        code = $("#txt_invitation_code").val();
        if (code !== ""){
            $.ajax({
                url: '/api/check_invitation_code',
                method: 'POST',
                async: false,
                data: JSON.stringify({'invitation_code': code}),
                success: function (data) {
                    console.log(data);
                    console.log(data["result"]);
                    data = JSON.parse(data["result"]);
                    data = data[0];
                    $('#txt_first_name').val(data['first_name']);
                    $('#txt_last_name').val(data['last_name']);
                    $('#txt_email').val(data['email']);
                    $('#txt_role').val(data['role'].replace(" ", ", "));
                    cur_id_num = data['identification_number'];

                },
                error: function (err) {
                    return false;
                }
            });
        }
    });

    function login(){
        // console.log($('input[name="signin_role"]:checked').val() );
        // var csrftoken = getCookie('csrftoken');
        // $.ajaxSetup({
        //     url: '/api/sign_in',
        //     type: 'POST',
        //     async: true,
        //     data: JSON.stringify({
        //         'id': $("#input_sign_in_id").val(), 'pwd': $("#input_sign_in_pwd").val(),
        //         'role': $('input[name="signin_role"]:checked').val()
        //     }),
        //     beforeSend: function(xhr, settings) {
        //        console.log(settings.type);
        //         if (!csrfSafeMethod(settings.type) && !this.crossDomain){
        //             xhr.setRequestHeader("X-CSRFToken", csrftoken);
        //         }
        //     },
        //     success: function (data) {
        //        console.log(data);
        //         if (data['state'] === true) { // success to log in
        //             current_user_info = data;
        //             set_current_user(data['data'][0]);
        //             console.log("Current User: ", get_current_user());
        //
        //             $('#modal_login').modal("hide");
        //             s_data = get_current_user();
        //             remove_current_page();
        //             if(s_data['role']=="Author"){
        //                 set_current_page(20);
        //             }else if(s_data['role']=="Staff"){
        //                 set_current_page(0);
        //             }else if(s_data['role']=="Evaluator"){
        //                 set_current_page(30);
        //             }else if(s_data['role']=="Trainee"){
        //                 set_current_page(40);
        //             }
        //             set_login_time(Math.floor(+new Date()/1000));
        //             openWindowWithPost('.', {
        //                 'first_name': s_data['first_name'],
        //                 'last_name': s_data['last_name'],
        //                 'email': s_data['email'],
        //                 'cur_role':s_data['role'],
        //                 'identification_number': s_data['identification_number'],
        //             });
        //             // window.location.reload();
        //         } else {                      // fail to log in
        //         $("#input_sign_in_id").addClass("is-invalid");
        //         $("#input_sign_in_pwd").addClass("is-invalid");
        //         if($('input[name="signin_role"]:checked').val() === undefined)
        //             $("#txt_role_err").removeAttr("hidden");
        //         }
        //     },
        //     error: function (err) {
        //         $("#input_sign_in_id").addClass("is-invalid");
        //         $("#input_sign_in_pwd").addClass("is-invalid");
        //         if($('input[name="signin_role"]:checked').val() === undefined)
        //             $("#txt_role_err").removeAttr("hidden");
        //
        //     }
        //
        // });

        $.ajax({
            url: '/api/sign_in',
            method: 'POST',
            async: true,
            data: JSON.stringify({
                'id': $("#input_sign_in_id").val(), 'pwd': $("#input_sign_in_pwd").val(),
                'role': $('input[name="signin_role"]:checked').val()
            }),
            success: function (data) {
                console.log(data);
                if (data['state'] === true) { // success to log in
                    current_user_info = data;
                    $('#modal_login').modal("hide");
                    s_data = data['data'][0];
                    openWindowWithPost('.', {
                        'first_name': s_data['first_name'],
                        'last_name': s_data['last_name'],
                        'email': s_data['email'],
                        'cur_role':s_data['role'],
                        'identification_number': s_data['identification_number'],
                    });
                } else {                      // fail to log in
                $("#input_sign_in_id").addClass("is-invalid");
                $("#input_sign_in_pwd").addClass("is-invalid");
                $('#txt_acc_err').removeAttr("hidden");
                if($('input[name="signin_role"]:checked').val() === undefined)
                    $("#txt_role_err").removeAttr("hidden");
                }
            },
            error: function (err) {
                $("#input_sign_in_id").addClass("is-invalid");
                $("#input_sign_in_pwd").addClass("is-invalid");
                $('#txt_acc_err').removeAttr("hidden");
                if($('input[name="signin_role"]:checked').val() === undefined)
                    $("#txt_role_err").removeAttr("hidden");
            }
        });

    }

    $('#btn_signup').click(function () {
       $('#modal_sign_up_1').modal();
    });

    $('#modal_login').on('hidden.bs.modal', function () {
        $("#input_sign_in_id").val("");
        $("#input_sign_in_pwd").val("");
       $('input[name="signin_role"]').prop('checked', false);
        $("#input_sign_in_id").removeClass("is-invalid");
        $("#input_sign_in_pwd").removeClass("is-invalid");
    });

    $('#modal_sign_up_1').on('hidden.bs.modal', function () {
       $("#txt_first_name").val("");
       $("#txt_last_name").val("");
       $("#txt_email").val("");
       $("#txt_pwd").val("");
       $("#txt_pwd_check").val("");
       $("#txt_phone").val("");
       $("#txt_affiliation").val("");
       $("#txt_leader_role").val("");
       $("#txt_qualification").val("");
       $("#txt_rank").val("");
       $("#txt_department").val("");
       $("#txt_work_phone").val("");
       $("#txt_work_email").val("");
       $('input[name="inlineRadioOptions"]').prop('checked', false);


       $("#txt_first_name").removeClass("is-invalid");
       $("#txt_last_name").removeClass("is-invalid");
       $("#txt_email").removeClass("is-invalid");
       $("#txt_pwd").removeClass("is-invalid");
       $("#txt_pwd_check").removeClass("is-invalid");
       $("#txt_phone").removeClass("is-invalid");
       $("#txt_affiliation").removeClass("is-invalid");
    });

    $('#btn_close').click(function () {
        console.log("btn_close Clicked!");
        $("#modal_sign_up_1").modal("hide");
    });

    $("#btn_finish").click(function () {
            signup();
    });
    $("input[name='inlineRadioOptions']").change(function () {
        $("input[name='inlineRadioOptions']").each(function () {
           var value = $(this).val();
           var checked = $(this).prop('checked');
           if (checked){
               if (value !== "Staff"){
                   $("#label_qualification").attr("hidden", false);
                   $("#txt_qualification").attr("hidden", false);
                   $("#label_leader_role").attr("hidden", true);
                   $("#txt_leader_role").attr("hidden", true);
               } else {
                   $("#label_qualification").attr("hidden", true);
                   $("#txt_qualification").attr("hidden", true);
                   $("#label_leader_role").attr("hidden", false);
                   $("#txt_leader_role").attr("hidden", false);
               }
           }
        });
    });

    function signup() {
        if ($("#txt_invitation_code").val()!==""){
            console.log("btn_finish Clicked!");
            var input_data = {};
            input_data['first_name'] = $("#txt_first_name").val();
            input_data['last_name'] = $("#txt_last_name").val();
            input_data['email'] = $("#txt_email").val();
            input_data['pwd'] = $("#txt_pwd").val();
            input_data['affiliation'] = $("#txt_affiliation").val();
            input_data['phone_number'] = $("#txt_phone").val();
            // input_data['role'] = $("#txt_role").val();
            input_data['identification_number'] = cur_id_num;
            state = true;
            if ($("#txt_pwd").val()!==$('#txt_pwd_check').val()){
                state = false;
                $("#txt_pwd").addClass("is-invalid");
                $("#txt_pwd_check").addClass("is-invalid");
            } if ($('#txt_first_name').val() === "") {
                state = false;
                $("#txt_first_name").addClass("is-invalid");
            } if ($('#txt_last_name').val() === "") {
                state = false;
                $("#txt_last_name").addClass("is-invalid");
            } if ($('#txt_email').val() === "") {
                state = false;
                $("#txt_email").addClass("is-invalid");
            } if ($('#txt_pwd').val() === "") {
                state = false;
                $("#txt_pwd").addClass("is-invalid");
            } if ($('#txt_pwd_check').val() === "") {
                state = false;
                $("#txt_pwd_check").addClass("is-invalid");
            } if ($('#txt_affiliation').val() === "") {
                state = false;
                $("#txt_affiliation").addClass("is-invalid");
            } if ($('#txt_phone').val() === "") {
                state = false;
                $("#txt_phone").addClass("is-invalid");
            }
            // if ($('#txt_qualification').val() === "") {
            //     state = false;
            //     $("#txt_qualification").addClass("is-invalid");
            // } if ($('#txt_leader_role').val() === "") {
            //     state = false;
            //     $("#txt_leader_role").addClass("is-invalid");
            // } if ($('#txt_rank').val() === "") {
            //     state = false;
            //     $("#txt_rank").addClass("is-invalid");
            // }  if ($('#txt_department').val() === "") {
            //     state = false;
            //     $("#txt_department").addClass("is-invalid");
            // } if ($('#txt_work_phone').val() === "") {
            //     state = false;
            //     $("#txt_work_phone").addClass("is-invalid");
            // } if ($('#txt_work_email').val() === "") {
            //     state = false;
            //     $("#txt_work_email").addClass("is-invalid");
            // }
            if (state) {
                $.ajax({
                    url: '/api/sign_up',
                    method: 'POST',
                    async: false,
                    data: JSON.stringify(input_data),
                    success: function (data) {
                        console.log(data['state']);
                        if (data['state'] === true) { // success to log in
                            window.location.reload();
                        } else {                      // fail to log in

                        }
                    },
                    error: function (err) {
                        return false;
                    }
                });
            }
        }
    }
})(jQuery);