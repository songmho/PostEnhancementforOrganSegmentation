/**
 * Created by khan on 2016-05-09.
 */

$('.notify-dropdown').on("click", function (event) {
    $(this).parent().toggleClass('open');
});
$('body').on('click', function (e) {
    if (!$('.notify-dropdown').is(e.target)
        && $('.notify-dropdown').has(e.target).length === 0
        && $('.open').has(e.target).length === 0
    ) {
        $('.notify-dropdown').removeClass('open');
    }
});

$('body').on('click', '.alert-custom-new', function(e){
    var session_id = $(this).attr('session_id');
    var alert = $(this);
    alert.attr('class', 'alert alert-custom fade in');
    $.ajax("/api/intpr_session", {
        method: 'PUT',
        data: JSON.stringify({
            action: 'read',
            session_id: session_id
        }),
        dataType: 'json',
        success: function (res) {
            console.log(res);
            if (res['code'] == 'SUCCESS') {
                $('#bell').load(document.URL + ' #bell');
            }
            else{
                alert.attr('class', 'alert alert-custom-new fade in')
            }
        }
    });
});
$('body').on('click', '.close', function(e){
    var session_id = $(this).attr('session_id');
    $.ajax("/api/intpr_session", {
        method: 'PUT',
        data: JSON.stringify({
            action: 'delete',
            session_id: session_id
        }),
        dataType: 'json',
        success: function (res) {
            console.log(res);
            $('#bell').load(document.URL + ' #bell');
        }
    });
});

$('#btnRefresh').click(function(e){
    $('.notifications').LoadingOverlay('show');
    $.ajax("/api/intpr_session", {
        method: 'POST',
        data: JSON.stringify({
            user_type: userType,
            user_id: userId
        }),
        dataType: 'json',
        success: function (res) {
            $('.notifications').LoadingOverlay('hide');
            console.log(res);
            $('#notifications-wrapper').load(document.URL + ' #notifications-wrapper');
            $('#bell').load(document.URL + ' #bell');
        }
    });
});


