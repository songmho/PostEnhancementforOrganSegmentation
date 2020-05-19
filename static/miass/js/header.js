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
    });

    $("#nav_liver_abnormality").click(function () {
    });

    $("#nav_lung_abnormality").click(function () {
    });

    $("#nav_breast_abnormality").click(function () {
    });

    $("#nav_stomach_abnormality").click(function () {
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
        location.replace("/view/update_profile")
    });

    $("#btn_change").click(function () {
        var a = $("input[name='role']:checked").val();
        console.log(a);
        set_current_role(a);

        location.reload();
    });

    $(document).ready(function () {
        // try {
            c_u = get_current_user();
            var c_r = get_current_role();
            if (c_u == null) {
                $("#nav_user").prop("hidden", true);
            } else {
                $("#nav_user").prop("hidden", false);
                var sen = c_u['first_name']+" "+c_u['last_name']+" ("+c_r+")";
                $("#txt_role").last().html(sen);

                var roles = c_u['role'].split(' ');
                console.log(roles);

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
        // } catch (e) {
        //     $("#nav_user").prop("hidden", true);
        // }

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