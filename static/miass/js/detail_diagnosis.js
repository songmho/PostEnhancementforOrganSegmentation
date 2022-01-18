(function () {
    $(document).ready(function () {
        var params = location.search.substr(location.search.indexOf("?")+1);
        params = params.split("&");
        let cur_id = params[0].split("=")[1];
        $.ajax({
            url: "/api/retrieve_diagnosis_liver",
            method: 'POST',
            async: true,
            data: {"data": JSON.stringify({
                "diagnosis_id": cur_id,
            })},
            success: function (data) {
                data = data["data"][0]
                console.log(data);
                $("#txt_patient_name").text(data["pat_name"]);
                $("#txt_patient_mrn").text(data["mrn"]);
                $("#txt_birthday").text(data["birthday"]);
                $("#txt_tumor_type").text(data["tumor_types"]);
                $("#txt_tumor_aphe_type").text(data["aphe_types"]);
                $("#txt_tumor_size").text(data["tumor_sizes"]);
                $("#txt_number_major_feature").text(data["num_mfs"]);
                $("#txt_stage").text(data["stages"]);
            }, error: function (err) {

            }
        });

    });

})(jQuery);