(function () {
    $(document).ready(function () {
        var cur_user_info = get_current_user();
        console.log(cur_user_info);
        $("#txt_user_fir_name").text(cur_user_info['first_name']);
        $("#txt_user_last_name").text(cur_user_info['last_name']);
        $("#txt_user_email").text(cur_user_info['email']);
        $("#txt_user_birthday").text(cur_user_info['birthday']);
        $("#txt_user_role").text(cur_user_info["role"]);
        $("#txt_user_phone").text(cur_user_info['phone_number']);
        $("#img_curr_profile").attr("src", "data:image/png;base64,"+get_current_profile());
    });

    $("#btn_update").on('click', function () {
        location.href = "/view/update_profile";
        $("#profile-retrieve").css("display", "none");
        $("#profile-update").css("display", "block");
    });
})(jQuery);