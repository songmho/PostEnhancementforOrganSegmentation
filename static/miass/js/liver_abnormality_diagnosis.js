(function () {
    var cur_user_role = get_current_role();

    $(document).ready(function () {
        if (cur_user_role !== "Physician"){
            $("#btn_diagnose_pat").css("display", "none");
        }else
            $("#btn_diagnose_pat").css("display", "block");

        $("#list_diagnose tbody").append("" +
            "<tr id="+1+">" +
            "<td scope=\'row\'>"+1+"</td>\n" +
            "<td>"+"Test"+"</td>\n" +
            "<td>"+"Test"+"</td>\n" +
            "<td>"+"Test"+"</td>\n" +
            "<td>"+"Test"+"</td>\n" +
            "</tr>" +
            "");

        var table = $('#list_diagnose').DataTable({
            responsive: true,
            search: true
        });
        $('#myInput').on( 'keyup', function () {
            table.search( this.value ).draw();
        });
    });
    $(document.body).delegate("#list_body tr", "click", function () {
        var tr = $(this);
        console.log(tr.attr("id"));
        location.href = SERVER_ADDRESS+"/view/diagnose/"+tr.attr('id');
    });

    $("#btn_diagnose_pat").on("click", function () {
        location.href = SERVER_ADDRESS+"/view/diagnose_abnormality";

    });

    $("#btn_diagnose_ml").on("click", function () {
        location.href = SERVER_ADDRESS+"/view/diagnose_abnormality_ml";

    });

})(jQuery);