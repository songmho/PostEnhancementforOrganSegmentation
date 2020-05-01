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
                    var rememberMe = $("input[id='chk_remember']").is(":checked");

                    if (rememberMe){
                        set_remember(s_data);
                    } else{
                        remove_remember();
                    }
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

    $(document).ready(function () {
        try{
            r_u = get_remember();
            if (r_u != null){
                $('#input_sign_in_id').val(r_u["email"]);
                $('#input_sign_in_pwd').val(r_u["pwd"]);
                $("input[id='chk_remember']").prop("checked", true);
            }
        } catch (e) {
        }

    });

})(jQuery);