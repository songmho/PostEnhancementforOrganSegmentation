(function () {
    var cur_user_info;
    var added_role;
    $(document).ready(function () {
        cur_user_info = get_current_user();
        var roles = cur_user_info['role'].split(" ");
        for(const i in roles){
            $("#rdo_"+roles[i]).hide();
            $("#lb_"+roles[i]).hide();
        }
    });

    $("#btn_add").on("click", function () {
        $("#modal_add").modal("show");
    });

    $("#btn_cancel").on("click", function () {
        console.log("Cancel");
    });

    $(":input:radio[name='group_role_add']").change(
        function () {
            $("#content").append($(this).val());
            added_role = $(this).val();
        });

    $("#btn_yes_add").on("click", function () {
        console.log(cur_user_info['identification_number'], added_role);
        $.ajax({
            url: "/api/add_role",
            method: 'POST',
            async: true,
            data: JSON.stringify({
                "id": cur_user_info["identification_number"],
                "role": added_role,
            }),
            success: function (data) {
                console.log(data);
            }, error: function (err) {
                console.log(err);
            }
        });
    });

    $("#btn_no_add").on("click", function () {
        $("#modal_add").modal("hide");
    });

})(jQuery);