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

    $('#btn_cancel').on("click", function () {
        // Need to check
        window.history.back();
    });

    $('#btn_apply').on("click", function () {

    });
})(jQuery);