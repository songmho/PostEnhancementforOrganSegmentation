(function () {
    var cur_user_info;
    var added_role;
    var checked_role;
    var add_result = false;

    $(document).ready(function () {
        cur_user_info = get_current_user();
        var roles = cur_user_info['role'].split(" ");
        for(const i in roles){
            $("#rdo_"+roles[i]).hide();
            $("#lb_"+roles[i]).hide();
        }
        if (roles.length === 2){
            $("#rdo_")
        }
    });

    $("#btn_add").on("click", function () {
        if (added_role!==undefined)
            $("#modal_add").modal("show");
        else{

        }
    });

    $("#btn_cancel").on("click", function () {
        console.log("Cancel");
        history.back();
    });

    $(":input:radio[name='group_role_add']").change(
        function () {
            checked_role = $(this).val();
            if (added_role !== undefined){
                if(added_role===checked_role){
                    added_role = checked_role;
                    $("#div_Patient_info").css("display", "none");
                    $("#div_Physician_info").css("display", "none");
                    $("#div_Staff_info").css("display", "none");
                    $("#div_"+added_role+"_info").css("display", "block");
                    console.log(added_role);
                }else{
                    $("#modal_change").modal("show");
                }
            } else {
                added_role = checked_role;
                $("#div_patient_info").css("display", "none");
                $("#div_physician_info").css("display", "none");
                $("#div_staff_info").css("display", "none");
                $("#div_"+added_role+"_info").css("display", "block");
                console.log(added_role);
            }

        });

    $("#btn_yes_add").on("click", function () {
        var role_data = {};
        if (added_role==="Patient"){  // if selected role is s
            role_data = {};
            role_data["blood_type"] = $("#slct_pat_blood_type").val();
            role_data["height"] = $("#txt_pat_height").val();
            role_data["weight"] = $("#txt_pat_weight").val();
        } else if (added_role==="Physician"){
            role_data = {};
            role_data["affiliation"] = $("#txt_phy_affiliation").val();
            role_data["license_number"] = $("#txt_phy_license_number").val();
            role_data["major"] = $("#txt_phy_major").val();

        } else if (added_role === "Staff"){
            role_data = {};
            role_data["affiliation"] = $("#txt_saf_affiliation").val();
        }else {

        }
        console.log(cur_user_info['identification_number'], added_role);
        $.ajax({
            url: "/api/add_role",
            method: 'POST',
            async: true,
            data: JSON.stringify({
                "id": cur_user_info["identification_number"],
                "role": added_role,
                "role_data": role_data,
            }),
            success: function (data) {
                $("#modal_add").modal("hide");
                $("#modal_add_finish").modal("show");
                $("#modal_add_finish_text").empty();
                if (data["state"]){    // if result is true
                    add_result = true;
                    $("#modal_add_finish_text").append("New role is added!");
                }else{                  // if result is false
                    $("#modal_add_finish_text").append("New role is not added. Check your Account.");
                    add_result = false;
                }
                console.log(data);
            }, error: function (err) {
                console.log(err);
            }
        });
    });

    $("#btn_yes_add_finish").on("click", function () {
        $("#modal_add_finish").modal("hide");
        if(add_result){
            // change user information --> update data -->


            $.ajax({
            url: "/api/get_cur_user_info",
            method: 'POST',
            async: true,
            data: JSON.stringify({
                "id": cur_user_info["identification_number"],
            }),
            success: function (data) {
                if (data["state"]){
                    const user_info = data["data"]
                    set_current_user(user_info)
                    location.reload();
                    history.back();
                }else{

                }
            }, error: function (err) {
                console.log(err);
            }
        });


        }
    });

    $("#btn_no_add").on("click", function () {
        $("#modal_add").modal("hide");
    });

    $("#btn_yes_change").on("click", function () {
        added_role = checked_role;
        $("#modal_change").modal("hide");
        $("#div_Patient_info").css("display", "none");
        $("#div_Physician_info").css("display", "none");
        $("#div_Staff_info").css("display", "none");
        $("#div_"+added_role+"_info").css("display", "block");
        $("[name='group_role_add'][value='"+added_role+"']").prop("checked", true);
        console.log(added_role);

    });

    $("#btn_no_change").on("click", function () {
        checked_role = added_role;
        // $(":input:radio[name='group_role_add']").attr("checked", false);
        $("#div_Patient_info").css("display", "none");
        $("#div_Physician_info").css("display", "none");
        $("#div_Staff_info").css("display", "none");
        $("#div_"+added_role+"_info").css("display", "block");
        $("[name='group_role_add'][value='"+added_role+"']").prop("checked", true);
        $("#modal_change").modal("hide");
        console.log(added_role);
    });

})(jQuery);