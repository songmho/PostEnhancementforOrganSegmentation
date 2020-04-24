(function () {
    $('#btn_images').click(function () {
        console.log("hgihihih");
    });
    $("#nav_register_img").click(function () {
        location.replace("view/register_image");
    });

    $("#nav_browse_img").click(function () {
        $("#main_container").load("view/browse_image", function () {

        });
    });

    $("#nav_annotate_img").click(function () {
    });

    $("#nav_remove_img").click(function () {
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
        location.replace("/")
    });

    $('#nav_log_out').click(function () {
        c_u = get_current_user();
        console.log("hi", c_u);
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
                    location.reload();
                }
                else{

                }
            },
             error: function (err) {
                console.log(err);
             }
        });
    });

    $(document).ready(function () {
        try {
            c_u = get_current_user();
            console.log(c_u);
            if (c_u == null) {
                $("#nav_user").prop("hidden", true);
            } else {
                $("#nav_user").prop("hidden", false);
                var sen = c_u['first_name']+" "+c_u['last_name']+" ("+c_u["role"]+")";
                console.log(sen);
                $("#txt_role").last().html(sen);

            }
        } catch (e) {
            console.log(c_u);
            $("#nav_user").prop("hidden", true);
        }

    });

})(jQuery);