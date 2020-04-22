(function () {
    // if (get_current_user() !== null){
    //     s_data = get_current_user();
    //     openWindowWithPost('.', {
    //         'first_name': s_data['first_name'],
    //         'last_name': s_data['last_name'],
    //         'email': s_data['email'],
    //         'cur_role':s_data['role'],
    //         'identification_number': s_data['identification_number'],
    //     });
    // }
    var cur_id_num = -1;

    $("#btn_check_code").click(function () {
        code = $("#txt_invitation_code").val();
        if (code !== ""){
            $.ajax({
                url: '/api/check_invitation_code',
                method: 'POST',
                async: false,
                data: JSON.stringify({'invitation_code': code}),
                success: function (data) {
                    console.log(data);
                    console.log(data["result"]);
                    data = JSON.parse(data["result"]);
                    data = data[0];
                    $('#txt_first_name').val(data['first_name']);
                    $('#txt_last_name').val(data['last_name']);
                    $('#txt_email').val(data['email']);
                    $('#txt_role').val(data['role'].replace(" ", ", "));
                    cur_id_num = data['identification_number'];

                },
                error: function (err) {
                    return false;
                }
            });
        }
    });




    $(document).ready(function () {
        try {
            console.log("hihih");
            c_u = get_current_user();
            if (c_u == null) {
                $("#main_container").load("view/sign_in");
            } else {
                $("#main_container").load("view/main");
            }
        } catch (e) {
            $("#main_container").load("view/sign_in");
        }

    });
})(jQuery);