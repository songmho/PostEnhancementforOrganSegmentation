(function () {
    // $("#list_image tr").click(function () {
    //     console.log($(this).text());
    // });

    $(document.body).delegate('#list_body tr', 'click', function () {
        // console.log($(this).text());
        var tr = $(this);

        // var tds = tr.children();
        location.href = SERVER_ADDRESS+"/view/browse/"+tr.attr('id');
    });

    $(document).ready(function () {
        $.ajax({
            url: "/api/retrieve_images",
            method: 'POST',
            async: true,
            data: JSON.stringify({
                "uid": null,
            }),
            success: function (data) {
                data = data["data"]
                for (var i in data){
                    var id = Number(i)+1;
                    $("#list_image tbody").append("" +
                        "<tr id="+data[i]['img_id']+">" +
                        "<td scope=\'row\'>"+id+"</td>\n" +
                        // "<td id='img_id' hidden>"+data[i]["img_id"]+"</td>\n" +
                        "<td>"+data[i]["first_name"]+"</td>\n" +
                        "<td>"+data[i]["last_name"]+"</td>\n" +
                        "<td>"+data[i]["img_type"]+"</td>\n" +
                        "<td>"+data[i]["acquisition_date"]+"</td>\n" +
                        "<td>"+data[i]["examination_source"]+"</td>\n" +
                        "</tr>" +
                        "");
                }

                var table = $('#list_image').DataTable({
                    responsive: true,
                    search: true
                });
                $('#myInput').on( 'keyup', function () {
                    table.search( this.value ).draw();
                });
            }, error: function (err) {

            }
        });

    });
})(jQuery);