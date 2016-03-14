/**
 * Created by hanter on 2016. 2. 23..
 */

var profiles = {};

$(document).ready(function() {
    $.LoadingOverlay('show');
    $.ajax("api/patient_profile", {
        method: 'GET',
        data: {
            user_id: user.user_id
        },
        dataType: 'json',
        success: function(res) {
            $.LoadingOverlay('hide');
            //console.log(JSON.stringify(res));
            if(res['code'] == 'SUCCESS') {
                profiles = res['profiles'];
                resetProfile();
            } else {
                openUpdateFailModal(res['msg'], 'Getting Profile Failed');
            }
        }
    });

    $('#btnFormReset').click(resetProfile);
    $('#patientProfileForm').on('submit', function(e) {
        e.preventDefault();

        updateProfile();
    });
});


function resetProfile() {
    $('#patientProfileForm input, #patientProfileForm textarea').each(function() {
        $(this).val('');
    });

    console.log(profiles);

    for (var i in profiles) {
        var profile = profiles[i];

        if(profile.type == "height") {
            var height = profile.value.split(" ");
            $('#height').val(height[0]);
            $('#heightType').val(height[1]).attr("selected", "selected");
        } else if(profile.type == "weight") {
            var weight = profile.value.split(" ");
            $('#weight').val(weight[0]);
            $('#weightType').val(weight[1]).attr("selected", "selected");
        } else if(profile.type == "smoking") {
            $('#smoking').val(profile.value).attr("selected", "selected");
        } else {
            $('#'+profile.type).val(profile.value);
        }
    }
}

var newProfiles = [];
function updateProfile() {
    newProfiles = [];
    var height = $('#height');
    if(height.val() <= 0){
        openUpdateFailModal('Invalid Height', 'Update Failed');
        height.focus();
        return
    }
    var weight = $('#weight');
    if(weight.val() <= 0){
        openUpdateFailModal('Invalid Weight', 'Update Failed');
        weight.focus();
        return
    }
    var drinkingCapacity = $('#drinkingCapacity');
    if(drinkingCapacity.val() <= 0){
        openUpdateFailModal('Invalid Drinking Capacity', 'Update Failed');
        drinkingCapacity.focus();
        return
    }
    var drinkingFrequency = $('#drinkingFrequency');
    if(drinkingFrequency.val() <= 0){
        openUpdateFailModal('Invalid Drinking Frequency', 'Update Failed');
        drinkingFrequency.focus();
        return
    }
    var sleeping = $('#sleeping');
    if(sleeping.val() <= 0 || sleeping.val() >= 24){
        openUpdateFailModal('Invalid Sleeping Hours', 'Update Failed');
        sleeping.focus();
        return
    }
    var exercise = $('#exercise');
    if(exercise.val() <= 0 || exercise.val() >= 1440){
        openUpdateFailModal('Invalid Exercise Hours', 'Update Failed');
        exercise.focus();
        return
    }
    var water = $('#water');
    if(water.val() <= 0){
        openUpdateFailModal('Invalid Water Intake', 'Update Failed');
        water.focus();
        return
    }


    $('#patientProfileForm input, #patientProfileForm textarea').each(function() {
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
    newProfiles.push({type: 'smoking', value: $('#smoking').val()});

    //console.log(newProfiles);
    $.LoadingOverlay('show');
    $.ajax("/api/patient_profile", {
        method: 'POST',
        data: JSON.stringify({
            user_id: user.user_id,
            profiles: newProfiles,
            timestamp: new Date().getTime()
        }),
        dataType: 'json',
        success: function(res) {
            $.LoadingOverlay('hide');
            //console.log(JSON.stringify(res));
            if(res['code'] = 'SUCCESS') {
                profiles = newProfiles;
                openUpdatedModal();
            } else {
                openUpdateFailModal(res['msg'], 'Update Failed');
            }
        }
    });
}

function openUpdateFailModal(msg, title) {
    if (title!=undefined && title!=null && title!='') {
        $('#updateFailedTitle').text(title)
    }
    if (msg==undefined || msg==null || msg=='') {
        msg = 'Updating failed. Please try again.'
    }
    $('#updateFailedModal .modal-body').text(msg);
    $('#updateFailedModal').modal();
}

function openUpdatedModal(msg, title) {
    if (title!=undefined && title!=null && title!='') {
        $('#updatedTitle').text(title)
    }
    if (msg==undefined || msg==null || msg=='') {
        msg = 'Your profile is successfully updated.'
    }
    $('#updatedModal .modal-body').text(msg);
    $('#updatedModal').modal();
}