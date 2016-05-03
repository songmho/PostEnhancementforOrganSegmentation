/**
 * Created by hanter on 2016. 1. 27..
 */
var usertype = null;
$(document).ready(function () {
    $('#col-signup-basic').hide();
    $('#col-signup-detail-patient').hide();
    $('#col-signup-detail-physician').hide();
    for(var country in country_arr){
        var opt = country_arr[country];
        $('#selectNationality').append('<option value="' +opt+'">'+opt+'</option>');
    }

    $('#inputId').blur(function (){
        checkID();
    });
    $('#inputPw').blur(function (){
        checkPassword();
    });
    $('#inputPwConfirm').blur(function (){
        checkPasswordConfirm();
    });
    $('#inputName').blur(function (){
        checkName();
    });
    $('#inputMobile').blur(function (){
        checkPhone();
    });
    $('#inputEmail').blur(function (){
        checkEmail();
    });
    $('#inputBirthday').blur(function (){
        checkBirth();
    });
    $('#inputLicence').blur(function (){
        checkLicense();
    });

    $('#inputBirthday').prop('max', function () {
        return new Date().toJSON().split('T')[0];
    });
    $('#btn-patient').click(function () {
        usertype = 'patient';
        $('#selectField').removeAttr('required');
        $('#inputLicence').removeAttr('required');
        $('#fileCertification').removeAttr('required');
        $('#selectGender').attr('required', '');
        $('#inputAge').attr('required', '');

        $('#col-signup-usertype').hide();
        $('#col-signup-basic').show();
    });
    $('#btn-physician').click(function () {
        usertype = 'physician';
        $('#selectGender').removeAttr('required');
        $('#inputAge').removeAttr('required');
        $('#selectField').attr('required', '');
        $('#inputLicence').attr('required', '');
        $('#fileCertification').attr('required', '');
        $('#col-signup-usertype').hide();
        $('#col-signup-basic').show();
    });

    $('#btn-basic-prev').click(function () {
        usertype = null;
        $('#col-signup-basic').hide();
        $('#col-signup-usertype').show();
    });

    $('#col-signup-basic').on('submit', function (e) {
        e.preventDefault();
        var invalidElements = "";
        if (!(checkIDFlag && checkPasswordFlag && checkNameFlag && checkPhoneFlag && checkEmailFlag && checkEmailFlag)) {
            if (!checkIDFlag) {
                invalidElements += "ID"
            }
            if (!checkPasswordFlag) {
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
            if (!checkEmailFlag) {
                if (invalidElements == "")
                    invalidElements += "E-mail";
                else
                    invalidElements += ", E-mail"
            }
            openModal("Please check these elements;" + invalidElements, "Warning");
        }
        else {
            $('#col-signup-basic').hide();
            if (usertype == 'patient') {
                $('#col-signup-detail-patient').show();
            } else if (usertype == 'physician') {
                $('#col-signup-detail-physician').show();
            }
        }
    });

    $('#btn-patient-prev').click(function () {
        $('#col-signup-detail-patient').hide();
        $('#col-signup-basic').show();
    });

    $('#btn-physician-prev').click(function () {
        $('#col-signup-detail-physician').hide();
        $('#col-signup-basic').show();
    });

    $('#col-signup-detail-patient').on('submit', function (e) {
        e.preventDefault();
        signup('patient');
    });
    $('#col-signup-detail-physician').on('submit', function (e) {
        e.preventDefault();
        signup('physician');
    });
});

function signup(usertype) {
    var user = {};
    if (usertype == 'patient') {
        if (!checkBirthFlag) {
            openModal("Please check birthday.", "Warning");
            return
        }
        user['gender'] = $('#selectGender').val();
        user['birthday'] = Date.parse($('#inputBirthday').val());
    } else if (usertype == 'physician') {
        if (!checkLicenseFlag) {
            openModal("Please check license.", "Warning");
            return
        }
        user['medicine_field'] = $('#selectField').val();
        user['license_number'] = $('#inputLicence').val();
        user['certificate_dir'] = 'here';
    }
    user['join_date'] = new Date().getTime();
    user['user_id'] = $('#inputId').val();
    user['password'] = $('#inputPw').val();
    user['name'] = $('#inputName').val();
    user['phone_number'] = $('#inputMobile').val();
    user['email'] = $('#inputEmail').val();
    user['nationality'] = $('#selectNationality :selected').val();
    user['user_type'] = usertype;

    $.LoadingOverlay('show');
    $.ajax("/api/user", {
        method: 'POST',
        data: JSON.stringify({
            action: 'signup',
            user: user
        }),
        dataType: 'json',
        success: function (res) {
            $.LoadingOverlay('hide');
            if (res['code'] == 'SUCCESS') {
                location.href = indexPage;
            } else {
                openSignupFailModal(res['msg']);
            }
        }
    });
}

function openSignupFailModal(msg, title) {
    if (title != undefined && title != null && title != '') {
        $('#signupFailedTitle').text(title)
    }
    if (msg == undefined || msg == null || msg == '') {
        msg = 'Sign up failed. Please try again.'
    }
    $('#signupFailedModal .modal-body').text(msg);
    $('#signupFailedModal').modal();
}