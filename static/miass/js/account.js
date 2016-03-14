/**
 * Created by hanter on 2016. 2. 23..
 */

$(document).ready(function() {
    console.log(user);

    if (user.user_type == 'patient') {
        $("#selectGender").val(user.gender).attr("selected", "selected");
        $('#inputBirthday').val(new Date(user.birthday).format("yyyy-MM-dd"));
    } else if (user.user_type = 'physician') {
        $("#selectField").val(user.medicine_field).attr("selected", "selected");
        //certification
    }

    $('#btnFormReset').click(function(){
        resetUser();
    });

    $('#accountForm').on('submit', function(e) {
        e.preventDefault();

        if($('#inputPw').val() != $('#inputPwConfirm').val()) {
            openUpdateFailModal("Password Confirm is not same.");
        } else {
            updateUser();
        }
    });
});

var updatingUser = {};
function updateUser() {
    var inputPw = $('#inputPw');
    if(inputPw.val().length > 20) {
        openUpdateFailModal("Invalid Password");
        inputPw.focus();
        return;
    }
    var phoneRe = /^[+]*[(]{0,1}[0-9]{1,3}[)]{0,1}[-\s\./0-9]*$/g;
    var inputMobile = $('#inputMobile');
    if(!inputMobile.val().match(phoneRe)){
        openUpdateFailModal("Invalid Phone Number");
        inputMobile.focus();
        return;
    }
    updatingUser = {};
    updatingUser['user_id'] = user.user_id;
    updatingUser['password'] = inputPw.val();
    updatingUser['name'] = $('#inputName').val();
    updatingUser['phone_number'] = inputMobile.val();
    updatingUser['email'] = $('#inputEmail').val();
    updatingUser['user_type'] = user.user_type;

    if(user.user_type == 'patient') {
        updatingUser['gender'] = $('#selectGender').val();
        var currentTime = new Date().getTime();
        var minBirthday = 0;
        var inputBirthday = $('#inputBirthday');
        if(Date.parse(inputBirthday.val()) > currentTime || Date.parse(inputBirthday.val()) < minBirthday) {
            openUpdateFailModal("Invalid Birthday");
            inputBirthday.focus();
            return;
        }
        updatingUser['birthday'] = Date.parse(inputBirthday.val())

    } else if(user.user_type == 'physician') {
        updatingUser['medicine_field'] = $('#selectField').val();
        updatingUser['license_number'] = $('#inputLicence').val();
        //user['certificate_dir'] = $('#fileCertification').val();
        updatingUser['certificate_dir'] = 'here';
    }

    $.LoadingOverlay('show');
    $.ajax("/api/user", {
        method: 'POST',
        data: JSON.stringify({
            action: 'update',
            user: updatingUser
        }),
        dataType: 'json',
        success: function(res) {
            console.log(res);
            $.LoadingOverlay('hide');
            if(res['code'] == 'SUCCESS') {
                user = updatingUser;
                openUpdatedModal();
            } else {
                openUpdateFailModal(res['msg']);
            }
        }
    });
}

function resetUser() {
    $('#inputName').val(user.name);
    $('#inputPw').val('');
    $('#inputPwConfirm').val('');
    $('#inputMobile').val(user.phone_number);
    $('#inputEmail').val(user.email);

    if(user.user_type == 'patient') {
        $("#selectGender").val(user.gender).attr("selected", "selected");
        $('#inputBirthday').val(new Date(user.birthday).format("yyyy-MM-dd"));
    } else if (user.user_type == 'physician') {
        $("#selectField").val(user.medicine_field).attr("selected", "selected");
        $('#inputLicence').val(user.license_number);
    }
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
        msg = 'Account information is successfully updated.'
    }
    $('#updatedModal .modal-body').text(msg);
    $('#updatedModal').modal();
}