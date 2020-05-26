(function () {
    var cur_user_info = get_current_user();
    console.log(cur_user_info);
    $("#txt_user_fir_name").text(cur_user_info['first_name']);
    $("#txt_user_last_name").text(cur_user_info['last_name']);
    $("#txt_user_email").text(cur_user_info['email']);
    $("#txt_user_birthday").text(cur_user_info['birthday']);
    $("#txt_user_role").text(cur_user_info["role"]);
    $("#txt_user_phone").text(cur_user_info['phone_number']);

    $("#btn_withdraw").on("click", function () {
       $("#modal_withdraw").modal("show");
    });

    $('#btn_no_withdraw').on("click", function () {
        $("#modal_withdraw").modal("hide");
    });

    $('#btn_yes_withdraw').on("click", function () {
        $("#modal_withdraw").modal("hide");
        // logout
        // remove user
    });

    $("#btn_update").on('click', function () {
        $("#profile-retrieve").css("display", "none");
        $("#profile-update").css("display", "block");
    });
})(jQuery);