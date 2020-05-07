(function () {
    // $("#list_image tr").click(function () {
    //     console.log($(this).text());
    // });

    $(document.body).delegate('#list_image tr', 'click', function () {
        // console.log($(this).text());
        var tr = $(this);
        var tds = tr.children();
        // console.log(tds.eq(1).text());
    });

    $(document.body).delegate("#list_image button", 'click', function () {
        var trgId = $(this).eq(0).attr('id');
        $("#modalRmvImg").modal('show');
        $("#modalRmvImg").on('shown.bs.modal', function (event) {
            $('#btnYes').click(function () {
                $.ajax({
                    url: "/api/remove_image",
                    method: 'POST',
                    async: true,
                    data: JSON.stringify({
                        "id": trgId,
                    }),
                    success: function (data) {
                        if (data['state'])
                            location.reload();

                        $("#modalRmvImg").modal('hide');
                    }, error: function (err) {

                    }
                });
            });
        });
    });

    $(document).ready(function () {
        $.ajax({
            url: "/api/retrieve_images",
            method: 'POST',
            async: true,
            data: JSON.stringify({

            }),
            success: function (data) {
                data = data["data"]
                for (var i in data){
                    var id = Number(i)+1;
                    var row = "" +
                        "<tr>" +
                        "<th scope=\'row\'>"+id+"</th>\n" +
                        "<td id='img_id' hidden>"+data[i]["img_id"]+"</td>\n" +
                        "<td>"+data[i]["first_name"]+"</td>\n" +
                        "<td>"+data[i]["last_name"]+"</td>\n" +
                        "<td>"+data[i]["img_type"]+"</td>\n" +
                        "<td>"+data[i]["acquisition_date"]+"</td>\n" +
                        "<td>"+data[i]["examination_source"]+"</td>\n"
                    try{
                        if (get_current_user()['identification_number'] === data[i]['uploader_id']){
                            row += "<td> <button  class='checkBtn'  id='"+data[i]["img_id"]+"'> Remove </button></td>\n" +
                            "</tr>";
                        }else{
                            row += "<td> </td>" +"</tr>";
                        }
                    } catch (e) {
                           row += "<td> </td>" +"</tr>";
                    }

                    $("#list_image tbody").append(row);
                }
            }, error: function (err) {

            }
        });
    });
})(jQuery);