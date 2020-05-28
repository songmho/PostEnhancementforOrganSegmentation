var isWithdrawed = false;

(function () {
    $("#btn_withdraw").on("click", function () {
        $("#modal_withdraw").modal("show");
    });

    $('#btn_no_withdraw').on("click", function () {
        $("#modal_withdraw").modal("hide");
    });

    $('#btn_checked_notice').on("click", function () {
        if(isWithdrawed){
            $("#modal_notice").modal("hide");
            location.replace("/main")
        } else{
            $("#modal_notice").modal("hide");

        }
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

    $("#btn_change_no").on("click", function () {
        $("#modal_change_pwd").modal("hide");
        $('#txt_crr_pwd').removeClass("is-invalid");
        $('#txt_pwd').removeClass("is-invalid");
        $('#txt_pwd_check').removeClass("is-invalid");
        $('#txt_chk_crr_pwd').prop("hidden", true);
        $('#txt_chk_pwd').prop("hidden", true);
        $('#txt_chk_pwd_re').prop("hidden", true);
    });

    $("#btn_change_yes").on("click", function () {
        console.log('adf');
        var cur_pwd = $("#txt_crr_pwd").val();
        var changed_pwd = $("#txt_pwd").val();
        var changed_pwd_re = $("#txt_pwd_check").val();

        $('#txt_crr_pwd').removeClass("is-invalid");
        $('#txt_pwd').removeClass("is-invalid");
        $('#txt_pwd_check').removeClass("is-invalid");

        $('#txt_chk_crr_pwd').prop("hidden", true);
        $('#txt_chk_pwd').prop("hidden", true);
        $('#txt_chk_pwd_re').prop("hidden", true);

        if (cur_pwd === undefined || cur_pwd === ""){
            $('#txt_crr_pwd').addClass("is-invalid");
            $('#txt_chk_crr_pwd').prop("hidden", false);

        } if (changed_pwd === undefined || changed_pwd === ""){
            $('#txt_pwd').addClass("is-invalid");
        $('#txt_chk_pwd').prop("hidden", false);

        } if (changed_pwd_re === undefined || changed_pwd_re === ""){
            $('#txt_pwd_check').addClass("is-invalid");
            $('#txt_chk_pwd_re').prop("hidden", false);
        }

        if (cur_pwd !== get_current_user()['pwd']){
            $('#txt_crr_pwd').addClass("is-invalid");
            $('#txt_chk_crr_pwd').prop("hidden", false);

        } if (changed_pwd !== changed_pwd_re){
            $('#txt_pwd').addClass("is-invalid");
            $('#txt_pwd_check').addClass("is-invalid");
            $('#txt_chk_pwd').prop("hidden", false);
            $('#txt_chk_pwd_re').prop("hidden", false);

        }

    });

    $('#btn_cancel').on("click", function () {
        // Need to check
        window.history.back();
    });

    $('#btn_apply').on("click", function () {
        $.ajax({
           url: "/api/",
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