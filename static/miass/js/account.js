/**
 * Created by hanter on 2016. 2. 23..
 */

$(document).ready(function () {
    checkPasswordFlag = true;
    checkPasswordConfirmFlag = true;
    checkFirstNameFlag = true;
    checkLastNameFlag = true;
    checkPhoneFlag = true;
    checkEmailFlag = true;
    checkEmailUsed = 1;
    checkBirthFlag = true;
    checkLicenseFlag = true;
    checkAddressFlag = true;
    checkCityFlag = true;

    var selectCountry = $('#selectCountry');
    for (var country in country_arr) {
        var opt = country_arr[country];
        selectCountry.append('<option value="' + opt + '">' + opt + '</option>');
    }
    selectCountry.val(user['country']);
    $('#inputPw').blur(function () {
        checkPassword();
    });
    $('#inputPwConfirm').blur(function () {
        checkPasswordConfirm();
    });
    $('#inputFirstName').blur(function () {
        checkFirstName();
    });
    $('#inputLastName').blur(function () {
        checkLastName();
    });
    $('#inputMobile').blur(function () {
        checkPhone();
    });
    //$('#inputEmail').blur(function () {
    //    checkEmail();
    //});
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
    $('#inputLicence').blur(function () {
        checkLicense();
    });

    if (user.birthday != undefined && user.birthday != null && user.birthday != 0) {
        var birthdayDate = new Date(user.birthday);
        var month = birthdayDate.getMonth() + 1;
        var day = birthdayDate.getDate();
        var year = birthdayDate.getYear() + 1900;

        $('#inputBirthdayMonth').val(month);
        $('#inputBirthdayDay').val(day);
        $('#inputBirthdayYear').val(year);
        var bmonth = month < 10 ? '0' + month : month;
        var bday = day < 10 ? '0' + day : day;
        var birthday = year + '-' + bmonth + '-' + bday;
        tempBirth = birthday;
    }

    if (user.user_type == 'patient') {
        $("#selectGender").val(user.gender).attr("selected", "selected");
    } else if (user.user_type = 'physician') {
        $("#selectField").val(user.medicine_field).attr("selected", "selected");
        //certification
    }

    $('#btnFormReset').click(function () {
        resetUser();
    });

    $('#btnUpdateAccount').click(function() {
        console.log('btn account clicked');

        //if($('#inputPw').val()=='' && $('#inputPwConfirm').val()=='') {
        //    $('#inputPw').removeAttr('required');
        //    $('#inputPwConfirm').removeAttr('required');
        //}
    });

    $('#accountForm').on('submit', function (e) {
        console.log('account submit');
        e.preventDefault();
        //$('#inputPw').attr('required', '');
        //$('#inputPwConfirm').attr('required', '');


        checkFormEmail();
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
    if (!(checkPasswordFlag && checkPasswordConfirmFlag && checkFirstNameFlag && checkLastNameFlag &&
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
        openModal("Please check these information: " + invalidElements, "Account Update Fail");
    } else {
        updateUser();
    }
}

var updatingUser = {};
function updateUser() {
    updatingUser = {};
    if (user.user_type == 'patient') {
        updatingUser['gender'] = $('#selectGender').val();

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
    updatingUser['first_name'] = $('#inputFirstName').val();
    updatingUser['last_name'] = $('#inputLastName').val();
    updatingUser['birthday'] = Date.parse(tempBirth);
    updatingUser['phone_number'] = $('#inputMobile').val();
    updatingUser['email'] = $('#inputEmail').val();
    updatingUser['address'] = $('#inputAddress').val();
    updatingUser['city'] = $('#inputCity').val();
    updatingUser['state'] = $('#inputState').val();
    updatingUser['country'] = $('#selectCountry :selected').val();
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
    checkFirstNameFlag = true;
    checkLastNameFlag = true;
    checkPhoneFlag = true;
    checkEmailFlag = true;
    checkEmailUsed = 1;
    checkBirthFlag = true;
    checkLicenseFlag = true;
    checkAddressFlag = true;
    checkCityFlag = true;

    $('#inputFirstName').val(user.first_name);
    $('#inputFirstName').css("border-color", "");
    $('#inputLastName').val(user.last_name);
    $('#inputLastName').css("border-color", "");
    $('#inputPw').val('');
    $('#inputPw').css("border-color", "");
    $('#inputPwConfirm').val('');
    $('#inputPwConfirm').css("border-color", "");
    $('#inputMobile').val(user.phone_number);
    $('#inputMobile').css("border-color", "");
    $('#inputEmail').val(user.email);
    $('#inputEmail').css("border-color", "");
    $('#inputAddress').val(user.address);
    $('#inputCity').val(user.city);
    $('#inputState').val(user.state);
    $('#selectCountry').val(user['country']);

    if (user.birthday != undefined && user.birthday != null && user.birthday != 0) {
        var birthdayDate = new Date(user.birthday);
        var month = birthdayDate.getMonth() + 1;
        var day = birthdayDate.getDate();
        var year = birthdayDate.getYear() + 1900;

        $('#inputBirthdayMonth').val(month);
        $('#inputBirthdayMonth').css("border-color", "");
        $('#inputBirthdayDay').val(day);
        $('#inputBirthdayDay').css("border-color", "");
        $('#inputBirthdayYear').val(year);
        $('#inputBirthdayYear').css("border-color", "");
        var bmonth = month < 10 ? '0' + month : month;
        var bday = day < 10 ? '0' + day : day;
        var birthday = year + '-' + bmonth + '-' + bday;
        tempBirth = birthday;
    }

    if (user.user_type == 'patient') {
        $("#selectGender").val(user.gender).attr("selected", "selected");
    } else if (user.user_type == 'physician') {
        $("#selectField").val(user.medicine_field).attr("selected", "selected");
        $('#inputLicence').val(user.license_number);
        $('#inputLicence').css("border-color", "");
    }
}