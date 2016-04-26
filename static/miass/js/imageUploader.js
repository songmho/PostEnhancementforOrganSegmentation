/**
 * Created by hanter on 2016. 3. 15..
 */
var INTERVAL_TIME = 250;
var circleProgress = null;
var g_progress_intv = null;
var uploadStatus = 0; //0=None, 1=waiting, 2=uploading, 3=configuring
var runningRotating = false;

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
});

function startFileProgressUpdate(upload_id) {
    uploadStatus=1;
    console.log('start file upload');

    setProgress(0);
    g_progress_intv = setInterval(function() {
        $.getJSON("/api/get_upload_progress?X-Progress-ID="+upload_id,
            function(data) {
                //console.log(uploadStatus);
                if(data == null) {
                    if(uploadStatus == 2) {
                        stopFileProgressUpdate()

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

function stopFileProgressUpdate(bStartValidating) {
    console.log('end data, stop.');
    clearInterval(g_progress_intv);
    g_progress_intv = null;
    setProgress(100);

    if (bStartValidating==undefined || bStartValidating==null)
        bStartValidating = true;
    if(bStartValidating) {
        uploadStatus = 3;
        setTimeout(function () {
            setProgressText('Decomposing...');
            startRotatingProgress();
        }, 200);
    }
}


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

    } else {

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

function getFiles(fileForm) {
    var files = fileForm.prop("files");
    var names = $.map(files, function(val) { return val.name; });
    return names;
}

function getFileExtension(fakePath) {
    var fakePaths = fakePath.split('.');
    var ext = fakePaths[fakePaths.length-1];
    return ext;
}

function checkImageTypeAndExtension(imageType, ext) {
    switch(imageType) {
        case 'EEG':
        case 'ECG':
        case 'EMG':
            if (ext == 'csv' || ext == 'edf') return true;
            else return false;

        case 'CT':
        case 'X-ray':
        case 'MRI':
        case 'US':
            if (ext == 'jpg' || ext == 'png' || ext == 'dcm' || ext == 'zip') return true;
            else return false;
    }
    return false;
}

function checkImageTypeIsGraphic(imageType) {
    switch(imageType) {
        case 'EEG':
        case 'ECG':
        case 'EMG':
            return false;
        case 'CT':
        case 'X-ray':
        case 'MRI':
        case 'US':
            return true;
    }
    return undefined;
}