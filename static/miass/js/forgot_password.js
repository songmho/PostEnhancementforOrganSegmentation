(function () {
    $("#btn_sign_up").on("click", function () {
        $('#txt_user_name').removeClass("is-invalid");
        var txt_user_name = $("#txt_user_name").val();
        var is_possible = true;
        if (txt_user_name===""){
            is_possible = false;
            $('#txt_user_name').addClass("is-invalid");
        }

        if(is_possible){
            $.ajax({
                url: "/api/change_pwd",
                method: 'POST',
                async: true,
                data: JSON.stringify({
                    "email": txt_user_name,
                }),
                success: function (data) {
                    if(data['state']){
                        console.log("fir");
                        location.replace("./main");
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