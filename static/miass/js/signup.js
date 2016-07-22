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
        $('#selectCountry').append('<option value="' +opt+'">'+opt+'</option>');
    }

    $('#inputId').blur(function (){
        var nowId = $('#inputId').val();
        if (/\S/.test(nowId) && nowId == tempID) {
            checkIDFlag = true;
        } else {
            checkIDFlag = false;
        }
    });
    $('#btnCheckId').click(checkID);
    $('#inputPw').blur(function (){
        checkPassword();
    });
    $('#inputPwConfirm').blur(function (){
        checkPasswordConfirm();
    });
    $('#inputLastName').blur(function (){
        checkLastName();
    });
    $('#inputFirstName').blur(function (){
        checkFirstName();
    });
    $('#inputMobile').blur(function (){
        checkPhone();
    });
    $('#inputEmail').blur(function (){
        var nowEmail = $('#inputEmail').val();
        if (/\S/.test(nowEmail) && nowEmail == tempEmail) {
            checkEmailFlag = true;
        } else {
            checkEmailFlag = false;
        };
    });
    $('#btnCheckEmail').click(checkEmail);
    $('#inputBirthdayMonth').blur(function (){
        checkBirth();
    });
    $('#inputBirthdayDay').blur(function (){
        checkBirth();
    });
    $('#inputBirthdayYear').blur(function (){
        checkBirth();
    });
    $('#inputAddress').blur(function (){
        checkAddress();
    });
    $('#inputCity').blur(function (){
        checkCity();
    });
    $('#inputLicence').blur(function (){
        checkLicense();
    });

    $('#btn-patient').click(function () {
        usertype = 'patient';
        //$('#selectField').removeAttr('required');
        //$('#inputLicence').removeAttr('required');
        $('#fileCertification').removeAttr('required');
        //$('#selectGender').attr('required', '');

        $('#col-signup-usertype').hide();
        $('#col-signup-basic').show();
    });
    $('#btn-physician').click(function () {
        usertype = 'physician';
        //$('#selectGender').removeAttr('required');
        //$('#selectField').attr('required', '');
        //$('#inputLicence').attr('required', '');
        $('#fileCertification').attr('required', '');
        $('#col-signup-usertype').hide();
        $('#col-signup-basic').show();
    });

    $('#btn-basic-prev').click(function () {
        usertype = null;
        $('#col-signup-basic').hide();
        $('#col-signup-usertype').show();
    });

    $('#btnSignupEmailOK').click(function() {
        setStep3();
    });

    $('#col-signup-basic').on('submit', function (e) {
        e.preventDefault();
        checkAndSetStep3();
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

function checkAndSetStep3() {
    if (!checkIDUsed) {
        openModal("Please check user ID.", "Signup");
        return;
    } else if (checkEmailUsed < 0) {
        openModal("Please check email address.", "Signup");
        return;
    } else if (checkEmailUsed == 0) {
        var dlgMsg = 'This email is already used for ';
        if (usertype == 'patient')
            dlgMsg += 'physician';
        else
            dlgMsg += 'patient';
        dlgMsg += '. If you are the same person, you just continue. Or not, you should check the email and use another email.<br/>Are you sure to use this email?';
        $('#signupEmailAlertModal .modal-body').html(dlgMsg);
        $('#signupEmailAlertModal').modal({backdrop: 'static', keyboard: false})
    } else {
        setStep3();
    }
}

function setStep3() {
    var invalidElements = "";
    if (!(checkIDFlag && checkPasswordFlag && checkPasswordConfirmFlag && checkFirstNameFlag && checkLastNameFlag &&
        checkPhoneFlag && checkEmailFlag && checkBirthFlag && checkAddressFlag && checkCityFlag)) {

        if (!checkFirstNameFlag) {
            invalidElements += "FirstName";
        }
        if (!checkLastNameFlag) {
            if (invalidElements == "")
                invalidElements += "LastName";
            else
                invalidElements += ", LastName"
        }
        if (!checkBirth) {
            if (invalidElements == "")
                invalidElements += "Date of Birth";
            else
                invalidElements += ", Date of Birth";
        }
        if (!checkPhoneFlag) {
            if (invalidElements == "")
                invalidElements += "Phone #";
            else
                invalidElements += ", Phone #";
        }
        if (!checkIDFlag) {
            if (invalidElements == "")
                invalidElements += "ID";
            else
                invalidElements += ", ID";
        }
        if (!checkPasswordFlag || !checkPasswordConfirmFlag) {
            if (invalidElements == "")
                invalidElements += "Password";
            else
                invalidElements += ", Password"
        }
        if (!checkEmailFlag) {
            if (invalidElements == "")
                invalidElements += "E-mail";
            else
                invalidElements += ", E-mail";
        }
        if (!checkAddressFlag) {
            if (invalidElements == "")
                invalidElements += "Address";
            else
                invalidElements += ", Address";
        }
        if (!checkCityFlag) {
            if (invalidElements == "")
                invalidElements += "City";
            else
                invalidElements += ", City";
        }
        openModal("Please check these information: " + invalidElements, "Warning");
    }
    else {
        $('#col-signup-basic').hide();
        if (usertype == 'patient') {
            $('#col-signup-detail-patient').show();
        } else if (usertype == 'physician') {
            $('#col-signup-detail-physician').show();
        }
    }
}

function signup(usertype) {
    var user = {};
    if (usertype == 'patient') {
        user['gender'] = $('#selectGender').val();
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
    user['first_name'] = $('#inputFirstName').val();
    user['last_name'] = $('#inputLastName').val();
    user['birthday'] = Date.parse(tempBirth);
    user['phone_number'] = $('#inputMobile').val();
    user['user_id'] = $('#inputId').val();
    user['password'] = $('#inputPw').val();
    user['email'] = $('#inputEmail').val();
    user['address'] = $('#inputAddress').val();
    user['city'] = $('#inputCity').val();
    user['state'] = $('#inputState').val();
    user['country'] = $('#selectCountry :selected').val();
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
                //location.href = indexPage;
                $('#col-signup-detail-patient').hide();
                $('#col-signup-detail-physician').hide();
                $('#col-signup-authentication').show();
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