/**
 * Created by hanter on 2016. 2. 24..
 */

var profiles = {};

$(document).ready(function() {
    $.ajax("api/physician_profile", {
        method: 'GET',
        data: {
            user_id: user.user_id
        },
        dataType: 'json',
        success: function(res) {
            console.log(JSON.stringify(res));
            if(res['code'] == 'SUCCESS') {
                profiles = res['profiles'];
                resetProfile();
            } else {
                openUpdateFailModal(res['msg'], 'Getting Profile Failed');
            }
        }
    });

    $('#physicianProfileForm').on('submit', function(e) {
        e.preventDefault();

        updateProfile();
    });
});

function resetProfile() {
    $('#physicianProfileForm input, #physicianProfileForm textarea').each(function() {
        $(this).val('');
    });

    for (var i in profiles) {
        var profile = profiles[i];
        $('#'+profile.type).val(profile.value);
    }
}

function updateProfile() {
    newProfiles = [];

    $('#physicianProfileForm input, #physicianProfileForm textarea').each(function() {
        var id = $(this).attr('id');
        var value = $(this).val();
        var nowProf = {};

        if (value == undefined || value == null || value == '' || value == ' ') {
            return;
        }

        nowProf['type'] = id;
        nowProf['value'] = value;
        newProfiles.push(nowProf);
    });

    $.ajax("api/physician_profile", {
        method: 'POST',
        data: JSON.stringify({
            user_id: user.user_id,
            profiles: newProfiles
        }),
        dataType: 'json',
        success: function(res) {
            console.log(JSON.stringify(res));
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