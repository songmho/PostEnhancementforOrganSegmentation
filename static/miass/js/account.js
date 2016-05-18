/**
 * Created by hanter on 2016. 2. 23..
 */

$(document).ready(function () {
    checkPasswordFlag = true;
    checkPasswordConfirmFlag = true;
    checkNameFlag = true;
    checkPhoneFlag = true;
    checkEmailFlag = true;
    checkEmailConfirmFlag = true;
    checkBirthFlag = true;
    checkLicenseFlag = true;
    checkEmailUsed = 1;

    var selectNationality = $('#selectNationality');
    for (var country in country_arr) {
        var opt = country_arr[country];
        selectNationality.append('<option value="' + opt + '">' + opt + '</option>');
    }
    selectNationality.val(user['nationality']);
    $('#inputPw').blur(function () {
        checkPassword();
    });
    $('#inputPwConfirm').blur(function () {
        checkPasswordConfirm();
    });
    $('#inputName').blur(function () {
        checkName();
    });
    $('#inputMobile').blur(function () {
        checkPhone();
    });
    $('#inputEmail').blur(function () {
        checkEmail();
    });
    $('#inputEmailConfirm').blur(function (){
        checkEmailConfirm();
    });
    $('#inputBirthday').blur(function () {
        checkBirth();
    });
    $('#inputLicence').blur(function () {
        checkLicense();
    });

    console.log(user);

    if (user.user_type == 'patient') {
        $("#selectGender").val(user.gender).attr("selected", "selected");
        var inputBirthday = $('#inputBirthday');
        inputBirthday.val(new Date(user.birthday).format("yyyy-MM-dd"));
        inputBirthday.prop('max', function () {
            return new Date().toJSON().split('T')[0];
        });

    } else if (user.user_type = 'physician') {
        $("#selectField").val(user.medicine_field).attr("selected", "selected");
        //certification
    }

    $('#btnFormReset').click(function () {
        resetUser();
    });

    $('#btnUpdateAccount').click(function() {
        console.log('btn account clicked');

        if($('#inputPw').val()=='' && $('#inputPwConfirm').val()=='') {
            $('#inputPw').removeAttr('required');
            $('#inputPwConfirm').removeAttr('required');
        }
    });

    $('#accountForm').on('submit', function (e) {
        console.log('account submit');
        e.preventDefault();
        $('#inputPw').attr('required', '');
        $('#inputPwConfirm').attr('required', '');

        if(checkingEmailUsed) {
            $.LoadingOverlay('show');
            var checkingEmailInterval = setInterval(function() {
                if(!checkingEmailUsed) {
                    clearInterval(checkingEmailInterval);
                    checkingEmailInterval = null;
                    $.LoadingOverlay('hide');
                    checkFormEmail();
                }
            }, 10);
        } else {
            checkFormEmail();
        }
    });

    $('#btnAccountEmailOK').click(function() {
        checkForm();
    })
});

function checkFormEmail() {
    if(checkEmailUsed < 0) {
        openModal("This email is already used.", "Account Update Fail");
    } else if(checkEmailUsed == 0) {
        var dlgMsg = 'This email is already used for ';
        if (usertype == 'patient')
            dlgMsg += 'physician';
        else
            dlgMsg += 'patient';
        dlgMsg += '. If you are the same person, you just continue. Or not, you should check the email and use another email.<br/>Are you sure to use this email?';
        $('#accountEmailAlertModal .modal-body').html(dlgMsg);
        $('#accountEmailAlertModal').modal({backdrop: 'static', keyboard: false})
    } else {
        checkForm();
    }
}

function checkForm() {
    var invalidElements = "";
    if (!(checkPasswordFlag && checkPasswordConfirmFlag && checkNameFlag && checkPhoneFlag && checkEmailFlag && checkEmailConfirmFlag)) {
        if (!checkPasswordFlag || !checkPasswordConfirmFlag) {
            if (invalidElements == "")
                invalidElements += "Password";
            else
                invalidElements += ", Password"
        }
        if (!checkNameFlag) {
            if (invalidElements == "")
                invalidElements += "Name";
            else
                invalidElements += ", Name"
        }
        if (!checkPhoneFlag) {
            if (invalidElements == "")
                invalidElements += "Phone Number";
            else
                invalidElements += ", Phone Number"
            }
        if (!checkEmailFlag || !checkEmailConfirmFlag) {
            if (invalidElements == "")
                invalidElements += "E-mail";
            else
                invalidElements += ", E-mail"
        }
        openModal("Please check these elements;" + invalidElements, "Account Update Fail");
    } else {
        updateUser();
    }
}

var updatingUser = {};
function updateUser() {
    updatingUser = {};
    if (user.user_type == 'patient') {
        updatingUser['gender'] = $('#selectGender').val();
        updatingUser['birthday'] = Date.parse($('#inputBirthday').val())

    } else if (user.user_type == 'physician') {
        updatingUser['medicine_field'] = $('#selectField').val();
        updatingUser['license_number'] = $('#inputLicence').val();
        //user['certificate_dir'] = $('#fileCertification').val();
        updatingUser['certificate_dir'] = 'here';
    }
    updatingUser['user_id'] = user.user_id;
    updatingUser['password'] = $('#inputPw').val();
    if (updatingUser['password']==undefined || updatingUser['password']==null || updatingUser['password']=='')
        updatingUser['password'] = user['password'];
    updatingUser['name'] = $('#inputName').val();
    updatingUser['phone_number'] = $('#inputMobile').val();
    updatingUser['email'] = $('#inputEmail').val();
    updatingUser['nationality'] = $('#selectNationality :selected').val();
    updatingUser['user_type'] = user.user_type;

    $.LoadingOverlay('show');
    $.ajax("/api/user", {
        method: 'POST',
        data: JSON.stringify({
            action: 'update',
            user: updatingUser
        }),
        dataType: 'json',
        success: function (res) {
            console.log(res);
            $.LoadingOverlay('hide');

            console.log(res['code']);

            if (res['code'] == "SUCCESS") {
                user = updatingUser;
                openModal("Account information is successfully updated.", "Update Success");
            } else if (res['code'] == 'WAIT') {
                user = updatingUser;
                openModal("Your email will be updated completely when your email is authenticated.<br/>" +
                    "Please check your new email and authenticate it.", "Update Success")
            } else {
                openModal(res['msg'], "Update Failed");
            }
        }
    });
}

function resetUser() {
    checkPasswordFlag = true;
    checkPasswordConfirmFlag = true;
    checkNameFlag = true;
    checkPhoneFlag = true;
    checkEmailFlag = true;
    checkEmailConfirmFlag = true;
    checkBirthFlag = true;
    checkLicenseFlag = true;

    $('#inputName').val(user.name);
    $('#inputName').css("border-color", "");
    $('#inputPw').val('');
    $('#inputPw').css("border-color", "");
    $('#inputPwConfirm').val('');
    $('#inputPwConfirm').css("border-color", "");
    $('#inputMobile').val(user.phone_number);
    $('#inputMobile').css("border-color", "");
    $('#inputEmail').val(user.email);
    $('#inputEmail').css("border-color", "");
    $('#selectNationality').val(user['nationality']);

    if (user.user_type == 'patient') {
        $("#selectGender").val(user.gender).attr("selected", "selected");
        $('#inputBirthday').val(new Date(user.birthday).format("yyyy-MM-dd"));
        $('#inputBirthday').css("border-color", "");
    } else if (user.user_type == 'physician') {
        $("#selectField").val(user.medicine_field).attr("selected", "selected");
        $('#inputLicence').val(user.license_number);
        $('#inputLicence').css("border-color", "");
    }
}