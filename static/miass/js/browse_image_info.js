(function (){
    $("#btn_view").on("click", function (){

        var id = $("#cur_id").text();
        location.href = SERVER_ADDRESS+"/view/browse_image_detail/"+id;
    });

    $(document).ready(function () {
        $.ajax({
            url:"/api/retrieve_image_info",
            method: 'POST',
            async: true,
            data: JSON.stringify({
                "i_id":$("#cur_id").text(),
            }),success: function (d) {
                if (d["state"]){
                    data = d['data'][0];
                    console.log(data);
                    $("#txt_fir_name").val(data['first_name']);
                    $("#txt_last_name").val(data['last_name']);
                    $("#txt_Birthday").val(data['birthday']);
                    if (data['gender']==="Male")
                        $("#rdo_male").prop("checked", true);
                    else
                        $("#rdo_female").prop("checked", true);
                    $("#txt_img_type").val(data['img_type']);
                    $("#txt_acq_date").val(data['acquisition_date']);
                    $("#txt_exam_src").val(data['examination_source']);

                    for(var i in data["images"]){
                        $("#list_phase").append(
                            "<div class=\"row pl-4 mb-2\" id=\"list_phase_"+i+"\">\n" +
                            "    <select class=\"phase_select\" id=\"txt_phase_select_"+i+"\">\n" +
                            "        <option disabled hidden selected>Acquired Phase</option>\n" +
                            "        <option>Plain</option>\n" +
                            "        <option>Arterial Phase</option>\n" +
                            "        <option>Portal Venous Phase</option>\n" +
                            "        <option>Delayed Phase</option>\n" +
                            "    </select>\n" +
                            "    <div id=\"cell\">\n" +
                            // "        <input id=\"btn_img_loader_"+i+"\" class=\"ml-1 img_loader y-auto\" type=\"file\" name=\"files\"  multiple=\"multiple\" webkitdirectory mozdirectory>\n" +
                            "    </div>\n" +
                            "    <button id=\"btn_view_"+i+"\" type=\"button\" class=\"btn btn-primary ml-2 btn_view\" style=\"display: none\" >View</button>\n" +
                            "    <button id=\"btn_cancel_"+i+"\" type=\"button\" class=\"btn btn-danger btn-cancel rounded-circle btn-circle ml-1\" style=\"display: none\">X</button>"+
                            "</div>");
                        $("#txt_phase_select_"+i).val(data["images"][i]).prop("selected", true);
                        // console.log(data["images"][i]);
                    }
                }else{

                }
            }, error: function (err){

            }
        })
    });
})(jQuery);