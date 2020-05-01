(function () {
    $("#btn_send").on("click", function () {
        $('#txt_user_name').removeClass("is-invalid");
        var txt_user_name = $("#txt_user_name").val();
        var is_possible = true;
        console.log(txt_user_name);
        if (txt_user_name===""){
            is_possible = false;
            $('#txt_user_name').addClass("is-invalid");
        }

        if(is_possible){
            $.ajax({
                url: "/api/forgot_pwd",
                method: 'POST',
                async: true,
                data: JSON.stringify({
                    "email": txt_user_name,
                }),
                success: function (data) {
                    if(data['state']){
                        console.log("fir");
                        location.replace(SERVER_ADDRESS+"/main");
                    }else{
                        is_possible = false;
                        $('#txt_user_name').addClass("is-invalid");
                    }
                }, error: function (err) {
                    is_possible = false;
                    $('#txt_user_name').addClass("is-invalid");
                }
            });
        }
    });

    $("#btn_change_pwd").on("click", function () {
        var txt_pwd = $("#txt_pwd").val();
        var txt_pwd_check = $("#txt_pwd_check").val();

        $("#txt_pwd").removeClass("is-invalid");
        $("#txt_pwd_check").removeClass("is-invalid");
        var is_possible = true;
        if (txt_pwd === ""){
            is_posible = false;
            $("#txt_pwd").addClass("is-invalid");
        } if (txt_pwd_check === ""){
            is_posible = false;
            $("#txt_pwd_check").addClass("is-invalid");
        }
        if (txt_pwd !== txt_pwd_check){
            is_posible = false;
            $("#txt_pwd").addClass("is-invalid");
            $("#txt_pwd_check").addClass("is-invalid");
        }

        if(is_possible){
            var id = $("#id").text();
            var email = $("#email").text();
            console.log(txt_pwd, txt_pwd_check, id, email, $("#id").text());
            $.ajax({
                url: "/api/reset_pwd",
                method: 'POST',
                async: true,
                data: JSON.stringify({
                    "id": id,
                    "email":email,
                    "pwd":txt_pwd
                }),
                success: function (data) {
                    if(data['state']){
                        location.replace(SERVER_ADDRESS+"/main");
                        // Need to add modal for changing success
                    }else{
                        is_possible = false;
                        $('#txt_user_name').addClass("is-invalid");
                    }
                }, error: function (err) {
                    is_possible = false;
                    $('#txt_user_name').addClass("is-invalid");
                }
            });
        }
    });
})(jQuery);