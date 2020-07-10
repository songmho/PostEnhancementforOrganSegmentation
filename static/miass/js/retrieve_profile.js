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

        for(const i in roles){
            console.log(roles[i]);
            $.ajax({
               url: "/api/retrieve_role",
               method: 'POST',
               async: false,
               data: JSON.stringify({
                   "id": get_current_user()["identification_number"],
                   "role": roles[i],
               }),
               success: function(data){
                   state = data['state'];
                   const role_data = data['data'];
                   if (state){
                       if (roles[i] === "Physician"){
                           $("#txt_phy_affiliation").text(role_data['affiliation']);
                           $("#txt_phy_license_number").text(role_data['license_number']);
                           $("#txt_phy_major").text(role_data['major']);
                       } else if (roles[i] === "Patient"){
                           $("#txt_pat_blood_type").text(role_data['blood_type']);
                           $("#txt_pat_weight").text(role_data['weight']);
                           $("#txt_pat_height").text(role_data['height']);

                       }else{       // Staff
                           $("#txt_staff_affiliation").text(role_data['affiliation']);
                       }
                   }
               }, error: function (err) {
               }
            });
        }

    });

    $("#btn_modify_profile").on("click", function () {
        location.href = "/view/update_profile"
    });

    $("#btn_add_role").on("click", function () {
        location.href = "/view/add_role"
    });

    $("#btn_patient_collapse_down").on("click", function () {
        // $("#btn_patient_collapse").toggle("active");
        $("#content_patient").show();
        $("#btn_patient_collapse_down").hide();
        $("#btn_patient_collapse_up").show();
    });

    $("#btn_patient_collapse_up").on("click", function () {
        // $("#btn_patient_collapse").toggle("active");
        $("#content_patient").hide();
        $("#btn_patient_collapse_down").show();
        $("#btn_patient_collapse_up").hide();
    });

    $("#btn_physician_collapse_down").on("click", function () {
        // $("#btn_patient_collapse").toggle("active");
        $("#content_physician").show();
        $("#btn_physician_collapse_down").hide();
        $("#btn_physician_collapse_up").show();
    });

    $("#btn_physician_collapse_up").on("click", function () {
        // $("#btn_patient_collapse").toggle("active");
        $("#content_physician").hide();
        $("#btn_physician_collapse_down").show();
        $("#btn_physician_collapse_up").hide();
    });

    $("#btn_staff_collapse_down").on("click", function () {
        // $("#btn_patient_collapse").toggle("active");
        $("#content_staff").show();
        $("#btn_staff_collapse_down").hide();
        $("#btn_staff_collapse_up").show();
    });

    $("#btn_staff_collapse_up").on("click", function () {
        // $("#btn_patient_collapse").toggle("active");
        $("#content_staff").hide();
        $("#btn_staff_collapse_down").show();
        $("#btn_staff_collapse_up").hide();
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