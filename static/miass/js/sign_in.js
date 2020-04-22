(function () {
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

    $('#btn_sign_in').click(function () {
        console.log("hi");
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

    $("#input_sign_in_id").keydown(function (key) {
        if(key.keyCode==13){
            if($("#input_sign_in_id").val()===""){
                $("#input_sign_in_id").addClass("is-invalid");
            }else{
                $("#input_sign_in_id").removeClass("is-invalid");
                $("#input_sign_in_pwd").focus();
            }
        }
    });

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
                'id': $("#input_sign_in_id").val(), 'pwd': $("#input_sign_in_pwd").val()
            }),
            success: function (data) {
                console.log(data);
                if (data['state'] === true) { // success to log in
                    current_user_info = data;
                    $('#modal_login').modal("hide");
                    s_data = data['data'];
                    openWindowWithPost('.', {
                        'first_name': s_data['first_name'],
                        'last_name': s_data['last_name'],
                        'email': s_data['email'],
                        'cur_role':s_data['role'],
                        'identification_number': s_data['identification_number'],
                    });
                    set_current_user(s_data);
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

    $("#btn_go_sign_up").click(function () {
        console.log("btn_finish Clicked!");
        location.href= "signup";
            // signup();
    });
})(jQuery);