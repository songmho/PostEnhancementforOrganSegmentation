(function () {
    var cur_user_info;
    $(document).ready(function () {
        cur_user_info = get_current_user();
        console.log(cur_user_info);
        $("#txt_user_name").text(cur_user_info['first_name']+" "+cur_user_info['last_name']);
        $("#txt_user_email").text(cur_user_info['email']);
        $("#txt_user_gender").text(cur_user_info['gender']);
        $("#txt_user_birthday").text(cur_user_info['birthday']);
        $("#txt_user_role").text(cur_user_info["role"]);
        $("#txt_user_phone").text(cur_user_info['phone_number']);
        if (get_current_profile() != "None" && get_current_profile() !== null){
            $("#img_curr_profile").attr("src", "data:image/png;base64,"+get_current_profile());
        }
        var roles = cur_user_info['role'].split(" ");
        if (roles.length === 3)
            $("#btn_add_role").css("display", "none");
        for (const id in roles){
            $("#group_"+roles[id]).show();
        }
    });

    $("#btn_modify_profile").on("click", function () {
        location.href = "/view/update_profile"
    });

    $("#btn_add_role").on("click", function () {
        location.href = "/view/add_role"
    });

    $("#btn_patient_collapse").on("click", function () {
        // $("#btn_patient_collapse").toggle("active");
        console.log("Hi");
        if ($("#content_patient").css("display")==="none"){
            $("#content_patient").show();
        }else{
            $("#content_patient").hide();
        }
    });

    $("#btn_physician_collapse").on("click", function () {
        // $("#btn_patient_collapse").toggle("active");
        console.log("Hi");
        if ($("#content_physician").css("display")==="none"){
            $("#content_physician").show();
        }else{
            $("#content_physician").hide();
        }
    });

    $("#btn_staff_collapse").on("click", function () {
        // $("#btn_patient_collapse").toggle("active");
        console.log("Hi");
        if ($("#content_staff").css("display")==="none"){
            $("#content_staff").show();
        }else{
            $("#content_staff").hide();
        }
    });

    $("#btn_withdraw").on("click", function () {
        $("#modal_withdraw").modal("show");
    });

    $("#btn_update").on('click', function () {
        location.href = "/view/update_profile";
        $("#profile-retrieve").css("display", "none");
        $("#profile-update").css("display", "block");
    });

    $('#btn_no_withdraw').on("click", function () {
        $("#modal_withdraw").modal("hide");
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
})(jQuery);