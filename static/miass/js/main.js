(function () {
    $("#logout").click(function () {
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

})(jQuery);