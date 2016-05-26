/**
 * Created by hanter on 2016. 2. 23..
 */

var profiles = [];

$(document).ready(function () {
    $.LoadingOverlay('show');
    $.ajax("api/patient_profile", {
        method: 'GET',
        data: {
            user_id: user.user_id
        },
        dataType: 'json',
        success: function (res) {
            $.LoadingOverlay('hide');
            //console.log(JSON.stringify(res));
            if (res['code'] == 'SUCCESS') {
                profiles = res['profiles'];
                resetProfile();
            } else {
                openUpdateFailModal(res['msg'], 'Getting Profile Failed');
            }
        }
    });

    $('#btnFormReset').click(resetProfile);
    $('#btnFormUpdate').click(function() {
        $('#patientProfileForm').submit();
    });
    $('#patientProfileForm').on('submit', function (e) {
        e.preventDefault();
        updateProfile();
    });

    var heightType = $('#heightType');
    var height = $('#height');
    heightType.change(function () {
        if (heightType.val() == "Centimeters") {
            height.attr('min', 60);
            height.attr('max', 300);
        }
        else if (heightType.val() == 'Inch') {
            height.attr('min', 23);
            height.attr('max', 120);
        }
        else if (heightType.val() == 'Feet') {
            height.attr('min', 2);
            height.attr('max', 10);
        }
    });

    var weightType = $('#weightType');
    var weight = $('#weight');
    weightType.change(function () {
        if (weightType.val() == "Kilogram") {
            weight.attr('min', 30);
            weight.attr('max', 500);
        }
        else if (weightType.val() == 'Pound') {
            weight.attr('min', 66);
            weight.attr('max', 1100);
        }
    });


    /*** for detailed profile tables ***/
    $('#btn-add-pmh-record').click(function () {
        addRow($('#table-pmh'), $('#info-phm'))
    });

    $('#btn-add-ed-record').click(function () {
        addRow($('#table-ed'), $('#info-ed'));
    });

    $('#btn-add-sd-record').click(function () {
        function changeClassName(table, info, newEntry){
            var lastItemNo = table.find("tr:last").attr("class").replace("sd", "");
            if(lastItemNo > 10){
                info.text("You can't add records more than 10.");
                return false
            }
            newEntry.removeClass();
            newEntry.find("td:eq(0)").attr("rowspan", "1");
            newEntry.addClass("sd" + (parseInt(lastItemNo) + 1));
            return true
        }
        addRow($('#table-sd'), $('#info-sd'), changeClassName)
    });

    $('#table-sd').on('click', '#btn-add-symptom', function (e) {
        var clickedEntry = $(this).parent().parent();
        var cls = clickedEntry.attr("class");
        if($("." + cls).length > 4){
            $('#info-sd').text("You can't add symptoms more than 5.");
            return
        }
        var newEntry = clickedEntry.clone();
        newEntry.find("td:eq(0)").remove();
        newEntry.insertAfter($("#table-sd ." + cls + ":last"));
        resizeRowspan(cls);
    });

    $('#btn-add-m-record').click(function () {
        addRow($('#table-m'), $('#info-m'));
    });

    $('#btn-add-fmh-record').click(function () {
        addRow($('#table-fmh'), $('#info-fmh'));
    });

    $('#btn-add-a-record').click(function () {
        addRow($('#table-a'), $('#info-a'));
    });

    $('.input-in-table').keydown(function(e) {
        //console.log(e);
        if (e.shiftKey && e.keyCode==220) {     // | key (it is used as delimiter
            e.preventDefault();

            var textarea = $(this);
            textarea.popover({
                title: "Alert",
                content: "This form cannot contain the special character '|'.",
                placement: "bottom",
                trigger: "manual"
            });
            textarea.popover("show");
            setTimeout(function () {
                textarea.popover('destroy');
            }, 2000);
        }
    });

});

function resizeRowspan(cls) {
    var rowspan = $("." + cls).length;
    $("." + cls + ":first td:eq(0)").attr("rowspan", rowspan);
}

function addRow(table, info, f) {
    var rowCount = table.find('>tbody>tr').length;
    if (rowCount > 10 && f == null) {
        info.text("You can't add records more than 10.");
        return
    }
    var controlForm = table;
    var currentEntry = table.find('>tbody>tr:first');
    var newEntry = $(currentEntry.clone());
    if(f != null){
        var res = f(table, info, newEntry);
        if(!res)
            return
    }
    newEntry.appendTo(controlForm);
    newEntry.find('input').val('');
    /*if (rowCount > 1) {
        var removeButtons = document.getElementsByClassName('btn-remove');
        for (var i = 0; i < removeButtons.length; i++) {
            removeButtons.item(i).disabled = false;
        }
    }*/
    newEntry.find('.input-in-table').keydown(function(e) {
        //console.log(e);
        if (e.shiftKey && e.keyCode==220) {     // | key (it is used as delimiter
            e.preventDefault();

            var textarea = $(this);
            textarea.popover({
                title: "Alert",
                content: "This form cannot contain the special character '|'.",
                placement: "bottom",
                trigger: "manual"
            });
            textarea.popover("show");
            setTimeout(function () {
                textarea.popover('destroy');
            }, 2000);
        }
    });
    newEntry.find('.btn-custom-delete').click(function() {
        newEntry.remove();
    });
}

function resetProfile() {
    $('#patientProfileForm input, #patientProfileForm textarea').each(function () {
        $(this).val('');
    });

    //console.log(profiles);

    for (var i in profiles) {
        var profile = profiles[i];

        if (profile.type == "height") {
            var height = profile.value.split(" ");
            $('#height').val(height[0]);
            var heightType = $('#heightType');
            heightType.val(height[1]).attr("selected", "selected");
            if (heightType.val() == "Centimeters") {
                $('#height').attr('min', 60);
                $('#height').attr('max', 300);
            }
            else if (heightType.val() == 'Inch') {
                $('#height').attr('min', 23);
                $('#height').attr('max', 120);
            }
            else if (heightType.val() == 'Feet') {
                $('#height').attr('min', 2);
                $('#height').attr('max', 10);
            }
        } else if (profile.type == "weight") {
            var weight = profile.value.split(" ");
            var weightType = $('#weightType');
            $('#weight').val(weight[0]);
            weightType.val(weight[1]).attr("selected", "selected");
            if (weightType.val() == "Kilogram") {
                $('#weight').attr('min', 30);
                $('#weight').attr('max', 500);
            }
            else if (weightType.val() == 'Pound') {
                $('#weight').attr('min', 66);
                $('#weight').attr('max', 1100);
            }
        } else if (profile.type == "smoking") {
            $('#smoking').val(profile.value).attr("selected", "selected");
        } else {
            $('#' + profile.type).val(profile.value);
        }
    }
}

var newProfiles = [];
function updateProfile() {
    //console.log(profiles);
    newProfiles = [];

    //check form
    var height = $('#height');
    if (height.val() <= 0 && height.val() != "") {
        openUpdateFailModal('Height must be larger than 0', 'Update Failed');
        height.focus();
        return
    }
    var weight = $('#weight');
    if (weight.val() <= 0 && weight.val() != "") {
        openUpdateFailModal('Weight must be larger than 0.', 'Update Failed');
        weight.focus();
        return
    }
    var drinkingCapacity = $('#drinkingCapacity');
    if (drinkingCapacity.val() < 0 && drinkingCapacity.val() != "") {
        openUpdateFailModal('Drinking capacity must be equal or larger than 0', 'Update Failed');
        drinkingCapacity.focus();
        return
    }
    var drinkingFrequency = $('#drinkingFrequency');
    if (drinkingFrequency.val() < 0 && drinkingFrequency.val() != "") {
        openUpdateFailModal('Drinking frequency must be equal or larger than 0', 'Update Failed');
        drinkingFrequency.focus();
        return
    }
    var sleeping = $('#sleeping');
    if ((sleeping.val() < 0 || sleeping.val() > 24) && sleeping.val() != "") {
        openUpdateFailModal('Sleeping hours must be larger than 0 and lower than 24.', 'Update Failed');
        sleeping.focus();
        return
    }
    var exercise = $('#exercise');
    if ((exercise.val() < 0 || exercise.val() > 1440) && exercise.val() != "") {
        openUpdateFailModal('Exercise Time must be larger than 0 and lower than 1440', 'Update Failed');
        exercise.focus();
        return
    }
    var water = $('#water');
    if (water.val() < 0 && water.val() != "") {
        openUpdateFailModal('Water intake must be larger than 0', 'Update Failed');
        water.focus();
        return
    }

    //add value
    $('#patientProfileBasicForm input, #patientProfileBasicForm textarea').each(function () {
        var id = $(this).attr('id');
        var value = $(this).val();
        var nowProf = {};

        if (value == undefined || value == null || value == '' || value == ' ') {
            return;
        }

        nowProf['type'] = id;
        if (id == "height") {
            nowProf['value'] = value + ' ' + $('#heightType').val()
        } else if (id == "weight") {
            nowProf['value'] = value + ' ' + $('#weightType').val()
        } else {
            nowProf['value'] = value;
        }

        newProfiles.push(nowProf);
    });
    var smoking = $('#smoking');
    if (smoking.val() != undefined && smoking.val() != null && smoking.val() != "") {
        newProfiles.push({type: 'smoking', 'value': smoking.val()});
    }

    var detailedProfiles = getDetailedProfiles();
    var isProfilesEmpty = checkDetailProfilesEmpty(detailedProfiles);
    if (newProfiles.length == 0 && isProfilesEmpty) {
        openModal('No Data in Profiles', 'Profile Update Failure');
        return;
    }

    //console.log(detailedProfiles);
    //console.log(JSON.stringify(detailedProfiles));
    if (!isProfilesEmpty) {
        newProfiles.push({'type': 'detail', 'value': stingifyDetailProfiles(detailedProfiles)});
    }
    console.log(newProfiles);

    $.LoadingOverlay('show');
    $.ajax("/api/patient_profile", {
        method: 'POST',
        data: JSON.stringify({
            user_id: user.user_id,
            profiles: newProfiles,
            timestamp: new Date().getTime()
        }),
        dataType: 'json',
        success: function (res) {
            $.LoadingOverlay('hide');
            console.log(JSON.stringify(res));
            if (res['code'] == 'SUCCESS') {
                profiles = newProfiles;
                openUpdatedModal();
            } else {
                openModal(res['msg'], 'Update Failed');
            }
        }
    });
}

function getDetailedProfiles() {
    var detailedProfile = {};

    var pastMedicalHistory = [];
    $('#table-pmh > tbody > tr').each(function(index, elem) {
        if (index == 0) return;
        var pmh_column = {};
        pmh_column['history_type'] = $(elem).find('.table-pmh-type').val();
        pmh_column['name'] = $(elem).find('.table-pmh-name').val();
        pmh_column['date'] = $(elem).find('.table-pmh-date').val();
        pmh_column['comment'] = $(elem).find('.table-pmh-comment').val();
        pastMedicalHistory.push(pmh_column);
    });
    detailedProfile['pmh'] = pastMedicalHistory;

    var existingDiseases = [];
    $('#table-ed > tbody > tr').each(function(index, elem) {
        if (index == 0) return;
        var ed_column = {};
        ed_column['name'] = $(elem).find('.table-ed-name').val();
        ed_column['degree'] = $(elem).find('.table-ed-degree').val();
        ed_column['duration'] = $(elem).find('.table-ed-duration-val').val() + '|'
                + $(elem).find('.table-ed-duration-unit').val();
        ed_column['comment'] = $(elem).find('.table-ed-comment').val();
        existingDiseases.push(ed_column);
    });
    detailedProfile['ed'] = existingDiseases;

    var suspectedDiseases = [];
    var now_sd_column = {};
    var rowspan = 0;
    $('#table-sd > tbody > tr').each(function(index, elem) {
        if (index == 0) return;

        if (rowspan == 0) { //new row
            rowspan = $(this).find('> td:first-of-type').prop('rowspan');
            now_sd_column = {};
            now_sd_column['name'] = $(elem).find('.table-sd-name').val();
            now_sd_column['symptoms'] = [];

            suspectedDiseases.push(now_sd_column);
        }

        var nowSymtom = {};
        nowSymtom['symptom'] = $(elem).find('.table-sd-symptom').val();
        nowSymtom['degree'] = $(elem).find('.table-sd-degree').val();
        nowSymtom['duration'] = $(elem).find('.table-sd-duration-val').val() + '|'
                + $(elem).find('.table-sd-duration-unit').val();
        nowSymtom['comment'] = $(elem).find('.table-sd-comment').val();
        now_sd_column['symptoms'].push(nowSymtom);
        rowspan--;
    });
    detailedProfile['sd'] = suspectedDiseases;

    var medications = [];
    $('#table-m > tbody > tr').each(function(index, elem) {
        if (index == 0) return;
        var m_column = {};
        m_column['name'] = $(elem).find('.table-m-name').val();
        m_column['intake'] = $(elem).find('.table-m-intake-val').val() + '|'
                + $(elem).find('.table-m-intake-unit').val();
        m_column['frequency'] = $(elem).find('.table-m-freq-val').val() + '|'
                + $(elem).find('.table-m-freq-unit').val();
        m_column['duration'] = $(elem).find('.table-m-duration-val').val() + '|'
                + $(elem).find('.table-m-duration-unit').val();
        m_column['comment'] = $(elem).find('.table-m-comment').val();
        medications.push(m_column);
    });
    detailedProfile['med'] = medications;

    var familyMedicalHistory = [];
    $('#table-fmh > tbody > tr').each(function(index, elem) {
        if (index == 0) return;
        var fmh_column = {};
        fmh_column['relationship'] = $(elem).find('.table-fmh-relationship').val();
        fmh_column['history'] = $(elem).find('.table-fmh-history').val();
        familyMedicalHistory.push(fmh_column);
    });
    detailedProfile['fmh'] = familyMedicalHistory;

    var allergies = [];
    $('#table-a > tbody > tr').each(function(index, elem) {
        if (index == 0) return;
        var a_column = {};
        a_column['name'] = $(elem).find('.table-a-name').val();
        a_column['degree'] = $(elem).find('.table-a-degree').val();
        a_column['comment'] = $(elem).find('.table-a-comment').val();
        allergies.push(a_column);
    });
    detailedProfile['alg'] = allergies;

    detailedProfile['notice'] = $('#notice').val();

    return detailedProfile;
}

function checkDetailProfilesEmpty(detailedProfile) {
    if (detailedProfile['pmh'].length() > 0) return false;
    if (detailedProfile['ed'].length() > 0) return false;
    if (detailedProfile['sd'].length() > 0) return false;
    if (detailedProfile['med'].length() > 0) return false;
    if (detailedProfile['fmh'].length() > 0) return false;
    if (detailedProfile['alg'].length() > 0) return false;
    if (detailedProfile['notice'] != '') return false;
    return true
}

function stingifyDetailProfiles(detailedProfile) {
    var stringProfile = {};
    stringProfile['pmh'] = JSON.stringify(detailedProfile['pmh']);
    stringProfile['ed'] = JSON.stringify(detailedProfile['ed']);
    stringProfile['sd'] = JSON.stringify(detailedProfile['sd']);
    stringProfile['med'] = JSON.stringify(detailedProfile['med']);
    stringProfile['fmh'] = JSON.stringify(detailedProfile['fmh']);
    stringProfile['alg'] = JSON.stringify(detailedProfile['alg']);
    stringProfile['notice'] = detailedProfile['notice'];
    return stringProfile;
}

function openUpdateFailModal(msg, title) {
    if (title != undefined && title != null && title != '') {
        $('#updateFailedTitle').text(title)
    }
    if (msg == undefined || msg == null || msg == '') {
        msg = 'Updating failed. Please try again.'
    }
    $('#updateFailedModal .modal-body').text(msg);
    $('#updateFailedModal').modal();
}

function openUpdatedModal(msg, title) {
    if (title != undefined && title != null && title != '') {
        $('#updatedTitle').text(title)
    }
    if (msg == undefined || msg == null || msg == '') {
        msg = 'Your profile is successfully updated.'
    }
    $('#updatedModal .modal-body').text(msg);
    $('#updatedModal').modal();
}
