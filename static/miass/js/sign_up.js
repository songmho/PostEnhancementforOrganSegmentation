(function () {
    $("#btn_sign_up").click(function () {
        $('#txt_first_name').removeClass("is-invalid");
        $('#txt_last_name').removeClass("is-invalid");
        $('#txt_email').removeClass("is-invalid");
        $('#txt_pwd').removeClass("is-invalid");
        $('#txt_pwd_check').removeClass("is-invalid");
        $('#txt_phone').removeClass("is-invalid");
        var is_possible = true;
        var fir_name = $("#txt_first_name").val();
        var last_name = $("#txt_last_name").val();
        var email = $("#txt_email").val();
        var pwd = $("#txt_pwd").val();
        var pwd_check = $("#txt_pwd_check").val();
        var phone = $("#txt_phone").val();

        if (fir_name === ""){
            is_possible = false;
            $('#txt_first_name').addClass("is-invalid");
        } if (last_name === ""){
            is_possible = false;
            $('#txt_last_name').addClass("is-invalid");
        } if (email === ""){
            is_possible = false;
            $('#txt_email').addClass("is-invalid");
        } if (pwd === ""){
            is_possible = false;
            $('#txt_pwd').addClass("is-invalid");
        } if (pwd_check === ""){
            is_possible = false;
            $('#txt_pwd_check').addClass("is-invalid");
        } if (phone === ""){
            is_possible = false;
            $('#txt_phone').addClass("is-invalid");
        }
        if (pwd !== pwd_check){
            is_possible = false;
            $('#txt_pwd').addClass("is-invalid");
            $('#txt_pwd_check').addClass("is-invalid");

        }

        if (is_possible){
            console.log("Add Sign up query");
        }
    });
})(jQuery);