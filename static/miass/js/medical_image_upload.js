/**
 * Created by hanter on 2016. 3. 8..
 */

var INTERVAL_TIME = 250;
var circleProgress = null;
var g_progress_intv = null;
var uploadStatus = 0; //0=None, 1=waiting, 2=uploading, 3=configuring
var runningRotating = false;

function startFileProgressUpdate(upload_id) {
    console.log('start file upload');

    setProgress(0);
    g_progress_intv = setInterval(function() {
        $.getJSON("/api/get_upload_progress?X-Progress-ID="+upload_id,
            function(data) {
                if(data == null) {
                    if(uploadStatus == 2) {
                        console.log('end data, stop.');
                        setProgress(100);
                        clearInterval(g_progress_intv);
                        g_progress_intv = null;

                        uploadStatus = 3;
                        setProgressText('Configuring...');
                        startRotatingProgress();

                    } else if (uploadStatus == 1) {
                        setProgress(0);
                    } else {
                        clearInterval(g_progress_intv);
                        g_progress_intv = null;
                    }
                    return;
                }

                uploadStatus = 2;
                var percentage = data.uploaded / data.length;
                animateProgress(percentage);
            });
    }, INTERVAL_TIME);
}


$(document).ready(function() {
    circleProgress = new ProgressBar.Circle('#uploadProgress', {
        color: '#D76474',
        strokeWidth: 3,
        trailWidth: 1,
        text: {
            value: '0'
        },
        step: function(state, bar) {
            bar.setText((bar.value() * 100).toFixed(0));
        }
    });

    $('#uploadImageForm').on('submit', function(e) {
        e.preventDefault();

        var data = new FormData($('#uploadImageForm').get(0));
        data.append('action', 'upload');
        data.append('image_info', JSON.stringify({
            user_id : user['user_id'],
            subject : $('#subject').val(),
            image_type : $('#imageType').val(),
            taken_date: Date.parse($('#takenDate').val()),
            taken_from : $('#takenFrom').val(),
            physician : $('#takenPhysicianName').val(),
            place : $('#clinicName').val(),
            description : $('#imageDescription').val()
        }));
        console.log(data);

        var xprogressID = new Date().getTime();
        setTimeout(function() {
            startFileProgressUpdate(xprogressID);
        }, 500);

        setProgressText('Uploading...');
        $('#uploadingProgressModal').modal({
            backdrop: 'static',
            keyboard: false
        });

        uploadStatus=1;
        $.ajax({
            url: $(this).attr('action') + '?X-Progress-ID='+xprogressID,
            type: $(this).attr('method'),
            data: data,
            cache: false,
            processData: false,
            contentType: false,
            success: function(res) {
                console.log(res);
                uploadStatus=0;
                stopRotatingProgress();
                $('#uploadingProgressModal').modal('hide');

                if (res['code'] == 'SUCCESS') {
                    $.LoadingOverlay('show');
                    location.href = archiveURL;
                } else {
                    openUploadFailedModal(res['msg']);
                }
            }
        });
    });

    $('#takenFrom').change(function() {
        var tf = $(this).val();
        if(tf == 'Home') {
            $('#takenPhysicianName').removeAttr('required').val('');
            $('#clinicName').removeAttr('required').val('');
            $('#physicianGroup').hide();
            $('#clinicNameGroup').hide();
        } else {
            $('#takenPhysicianName').attr('required', '');
            $('#clinicName').attr('required', '');
            $('#physicianGroup').show();
            $('#clinicNameGroup').show();
        }
    });

    //$('#uploadingProgressModal').modal({
    //    backdrop: 'static',
    //    keyboard: false
    //});
});

function setProgressText(text) {
    $('#uploadingProgressModal #uploadStatus').text(text);
}
function setProgress(percent) {
    if(percent<0) percent=0;
    else if(percent>1.0) percent=1.0;
    circleProgress.set(percent, {
        duration: INTERVAL_TIME
    });
}
function animateProgress(percent) {
    if(percent<0) percent=0;
    else if(percent>1.0) percent=1.0;
    circleProgress.animate(percent, {
        duration: INTERVAL_TIME
    });
}
function showLoadingText(bShow) {
    if(bShow) {
        $('#uploadProgress .progressbar-text').show();
    } else {
        $('#uploadProgress .progressbar-text').hide();
    }
}
function rotatingProgress() {
    if(runningRotating) {
        var duration = 1000;

        setTimeout(function () {
            rotatingProgress();
        }, duration);

        var $elm = $('#uploadProgress');

        $({deg: 0}).animate({deg: 360}, {
            duration: duration,
            step: function (now) {
                $elm.css({
                    //'transform': 'rotate(' + easeInOutCubic (now/360*1000, 0, 360, 1000) + 'deg)'
                    'transform': 'rotate(' + now + 'deg)'
                });
            }
        });

        console.log('rotating...');
    } else {
        console.log('rotating stopped');
    }
}
function startRotatingProgress() {
    runningRotating = true;
    showLoadingText(false);
    setProgress(0.7);
    rotatingProgress();
}
function stopRotatingProgress() {
    runningRotating = false;
    showLoadingText(true);
    setProgress(0);
    var $elm = $('#uploadProgress');
    $({deg: 0}).animate({deg: 0}, {
        duration: 0,
        step: function (now) {
            $elm.css({
                'transform': 'rotate(' + 0 + 'deg)'
            });
        }
    });
}
function easeInOutCubic (t, b, c, d) {
	t /= d/2;
	if (t < 1) return c/2*t*t*t + b;
	t -= 2;
	return c/2*(t*t*t + 2) + b;
}
function openUploadFailedModal(msg) {
    if (msg==undefined || msg==null || msg=='') {
        msg = 'Uploading Medical Image Failed.';
    }
    $('#uploadFailModal .modal-body').text(msg);
    $('#uploadFailModal').modal();
}