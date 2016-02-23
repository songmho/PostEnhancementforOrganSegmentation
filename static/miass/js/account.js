/**
 * Created by hanter on 2016. 2. 23..
 */

$(document).ready(function() {
    if (user.user_type == 'patient') {
        $("#selectGender").val(user.gender).attr("selected", "selected");

    } else if (user.user_type = 'physician') {
        $("#selectField").val(user.medicine_field).attr("selected", "selected");
        //certification
    }

    $('#btnFormReset').click(function(){
        resetUser();
    });

    $('#accountForm').on('submit', function(e) {
        e.preventDefault();


    });

});

function updateUser() {

}

function resetUser() {
    $('#inputName').val(user.name);
    $('#inputPw').val('');
    $('#inputPwConfirm').val('');
    $('#inputMobile').val(user.phone_number);
    $('#inputEmail').val(user.email);

    if(user.user_type == 'patient') {

    } else if (user.user_type == 'physician') {
        $("#selectField").val(user.medicine_field).attr("selected", "selected");
        $('#inputLicence').val(user.license_number);
    }
}