(function () {
    $('#btn_images').click(function () {
    });
    $("#nav_register_img").click(function () {
        location.replace(SERVER_ADDRESS+"/view/register_image");
    });

    $("#nav_browse_img").click(function () {
        location.replace(SERVER_ADDRESS+"/view/browse_image");

    });

    $("#nav_annotate_img").click(function () {
        location.replace(SERVER_ADDRESS+"/view/annotate_image");
    });

    $("#nav_remove_img").click(function () {
        location.replace(SERVER_ADDRESS+"/view/remove_image");
    });


    $("#nav_brain_abnormality").click(function () {
        location.replace(SERVER_ADDRESS+"/view/brain_abnormality_diagnosis");
    });

    $("#nav_liver_abnormality").click(function () {
        location.replace(SERVER_ADDRESS+"/view/liver_abnormality_diagnosis");
    });

    $("#nav_diagnosing").click(function () {
        location.replace(SERVER_ADDRESS+"/view/diagnose_abnormality_ml#step-1");
    });

    $("#nav_lung_abnormality").click(function () {
        location.replace(SERVER_ADDRESS+"/view/lung_abnormality_diagnosis");
    });

    $("#nav_breast_abnormality").click(function () {
        location.replace(SERVER_ADDRESS+"/view/breast_abnormality_diagnosis");
    });

    $("#nav_stomach_abnormality").click(function () {
        location.replace(SERVER_ADDRESS+"/view/stomach_abnormality_diagnosis");
    });


    $("#nav_load_diagnosis").click(function () {
    });

    $("#nav_recommend_treatments").click(function () {
    });

    $("#nav_retrieve_diagnosis").click(function () {
    });

    $('#nav_main').click(function () {
        location.replace(SERVER_ADDRESS);
    });

    $('#nav_log_out').click(function () {
        c_u = get_current_user();
         $.ajax("/api/signout", {
            method: 'POST',
            async: true,
            data: JSON.stringify({
                'email': c_u["email"],
                'pwd': c_u["pwd"],
                'identification_number':c_u["identification_number"]
            }),
            success: function(data) {
                if (data['state'] === true) { // success to log in
                    remove_current_user();
                    location.replace("/main")
                }
                else{

                }
            },
             error: function (err) {
                console.log(err);
             }
        });
    });

    $("#nav_profile").click(function () {
        location.replace("/view/browse_profile")
    });

    $("#nav_option").on("click", function () {
       console.log(get_voice());
       if (get_voice()==1){
            $("#rdo_female").prop("checked", true);
            $("#rdo_male").prop("checked", false);
       }else{
            $("#rdo_female").prop("checked", false);
            $("#rdo_male").prop("checked", true);
       }
    });

    $("#btn_change").click(function () {
        var a = $("input[name='role']:checked").val();
        console.log(a);
        set_current_role(a);

        location.reload();
    });

    $("#btn_option_change").on("click", function () {
        var a = $("input[name='voice']:checked").val();
        set_voice(a);

        $("#modal_option").modal("hide");

    });

    $(document).ready(function () {
        try {
            c_u = get_current_user();
            var c_r = get_current_role();
            if (get_current_profile() != "None" && get_current_profile() !==null) {
                $('#img_profile').attr("src", "data:image/png;base64,"+get_current_profile());
            }

            if (c_u == null) {
                $("#nav_user").prop("hidden", true);
            } else {
                $("#nav_user").prop("hidden", false);
                var sen = c_u['first_name']+" "+c_u['last_name']+" ("+c_r+")";
                $("#txt_role").last().html(sen);

                var roles = c_u['role'].split(' ');

                $("#div_patient").prop("hidden", true);
                $("#div_physician").prop("hidden", true);
                $("#div_staff").prop("hidden", true);
                for (r in roles){
                    if (roles[r]==="Patient"){
                        $("#div_patient").prop("hidden", false);
                        if (roles[r]===c_r){
                            $("#rdo_patient").attr('checked', true);
                        }
                    } if(roles[r]==="Physician"){
                        $("#div_physician").prop("hidden", false);
                        if (roles[r]===c_r){
                            $("#rdo_physician").attr('checked', true);
                        }
                    } if(roles[r]==="Staff"){
                        $("#div_staff").prop("hidden", false);
                        if (roles[r]===c_r){
                            $("#rdo_staff").attr('checked', true);
                        }
                    }
                }
            }
        } catch (e) {
            $("#nav_user").prop("hidden", true);
        }

    });

    $(window).bind("unload", function () {
        var identification_number = get_current_user()['identification_number'];
        $.ajax({
           type: "POST",
           url: "/api/signout",
            async: false,
            data: JSON.stringify({
                "identification_number": identification_number
            }),success: function (data) {},
        error: function (err) {}
        });

    })
})(jQuery);