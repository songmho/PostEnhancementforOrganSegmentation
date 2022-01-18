(function () {
    var cur_user_role = get_current_role();


    $(document.body).delegate('#list_body tr', 'click', function () {
        // console.log($(this).text());
        // console.log(tr.attr("id"));
        // // var tds = tr.children();
        // location.href = SERVER_ADDRESS+"/view/diagnose?current_diagnosis="+tr.attr('id');
        console.log($(this).attr("id"));
        $("#input_diagnosis_id").val($(this).attr("id"));
        $("#form-detail_diagnosis").submit();
    });

    $(document).ready(function () {
        $.ajax({
            url: "/api/retrieve_diagnosis_liver",
            method: 'POST',
            async: true,
            data: {"data": JSON.stringify({
                "diagnosis_id": null,
            })},
            success: function (data) {
                data = data["data"]
                var id = 0;
                for (var i in data){
                    id++;
                    $("#list_diagnose tbody").append("" +
                        "<tr id="+data[i]['diagnosis_id']+">" +
                        "<td scope=\'row\'>"+id+"</td>\n" +
                        // "<td id='img_id' hidden>"+data[i]["img_id"]+"</td>\n" +
                        "<td>"+data[i]["pat_name"]+"</td>\n" +
                        "<td>"+data[i]["birthday"]+"</td>\n" +
                        "<td>"+data[i]["diagnosis_date"]+"</td>\n" +
                        "<td>"+data[i]["stages"].split(",").length+"</td>\n" +
                        "<td>"+data[i]["stages"]+"</td>\n" +
                        "</tr>" +
                        "");
                }

                var table = $('#list_diagnose').DataTable({
                    responsive: true,
                    search: true
                });
                $('#myInput').on( 'keyup', function () {
                    table.search( this.value ).draw();
                });
            }, error: function (err) {

            }
        });
        if (cur_user_role !== "Physician"){
            $("#btn_diagnose_pat").css("display", "none");
        }else
            $("#btn_diagnose_pat").css("display", "block");
    });


})(jQuery);